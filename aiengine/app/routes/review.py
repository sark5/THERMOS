"""
THERMOS Human-in-the-Loop Review Router
Provides audited review and gold-label validation interface for edge cases
and low-confidence candidate classifications.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "training" / "datasets" / "processed"
REVIEW_QUEUE_FILE = DATA_DIR / "review_queue.parquet"

router = APIRouter()

_REVIEW_CACHE: Optional[pd.DataFrame] = None


def _load_queue() -> pd.DataFrame:
    global _REVIEW_CACHE
    if _REVIEW_CACHE is not None:
        return _REVIEW_CACHE
    if REVIEW_QUEUE_FILE.exists():
        _REVIEW_CACHE = pd.read_parquet(REVIEW_QUEUE_FILE)
    else:
        _REVIEW_CACHE = pd.DataFrame()
    return _REVIEW_CACHE


class ReviewSubmission(BaseModel):
    event_id: str
    action: str  # CONFIRM, CORRECT, UNCERTAIN, REJECT
    assigned_label: Optional[str] = None
    reviewer: str = "Operator"
    notes: Optional[str] = None


@router.get("/queue")
def get_review_queue(limit: int = 50, status: Optional[str] = "PENDING"):
    """Fetch pending candidate classifications requiring expert human verification."""
    df = _load_queue()
    if df.empty:
        return {"total": 0, "pending": 0, "items": []}

    filtered = df
    if status and status != "ALL" and "review_status" in df.columns:
        filtered = df[df["review_status"] == status]

    items = []
    for row in filtered.head(limit).itertuples():
        items.append({
            "event_id": str(getattr(row, "event_id", "")),
            "latitude": float(getattr(row, "latitude", 20.0)),
            "longitude": float(getattr(row, "longitude", 80.0)),
            "frp": float(getattr(row, "frp", 10.0)),
            "predicted_class": str(getattr(row, "thermos_label", "UNCLASSIFIED")),
            "confidence": float(getattr(row, "label_score", 0.65)),
            "margin": float(getattr(row, "label_margin", 0.20)),
            "facility_name": str(getattr(row, "facility_name", "Nearby Industrial Site")),
            "distance_to_facility": float(getattr(row, "distance_to_facility", 12.0)),
            "reasons": str(getattr(row, "label_reasons", "Low classification margin")),
            "review_status": str(getattr(row, "review_status", "PENDING")),
            "human_label": getattr(row, "human_label", None),
            "reviewer": getattr(row, "reviewer", None),
        })

    return {
        "total": len(df),
        "pending": int((df["review_status"] == "PENDING").sum()) if "review_status" in df.columns else len(df),
        "items": items,
    }


@router.post("/submit")
def submit_review(sub: ReviewSubmission):
    """Record human reviewer validation action for an active edge-case event."""
    global _REVIEW_CACHE
    df = _load_queue()
    if df.empty:
        raise HTTPException(status_code=404, detail="Review queue is empty")

    idx = df[df["event_id"] == sub.event_id].index
    if len(idx) == 0:
        raise HTTPException(status_code=404, detail=f"Event {sub.event_id} not found in review queue")

    target_idx = idx[0]
    df.loc[target_idx, "review_status"] = sub.action
    df.loc[target_idx, "reviewer"] = sub.reviewer
    df.loc[target_idx, "review_notes"] = sub.notes or ""
    df.loc[target_idx, "reviewed_at"] = datetime.utcnow().isoformat()
    if sub.action == "CORRECT" and sub.assigned_label:
        df.loc[target_idx, "human_label"] = sub.assigned_label
    elif sub.action == "CONFIRM":
        df.loc[target_idx, "human_label"] = df.loc[target_idx, "thermos_label"]

    _REVIEW_CACHE = df
    try:
        df.to_parquet(REVIEW_QUEUE_FILE)
    except Exception as e:
        print(f"Warning: Failed to persist review queue: {e}")

    return {
        "status": "SUCCESS",
        "event_id": sub.event_id,
        "action": sub.action,
        "human_label": df.loc[target_idx, "human_label"],
        "reviewer": sub.reviewer,
        "reviewed_at": df.loc[target_idx, "reviewed_at"],
    }

