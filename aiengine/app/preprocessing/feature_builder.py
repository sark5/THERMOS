"""
THERMOS Preprocessing & Feature Vector Builder for Real-Time Inference Server
Constructs 86 Canonical Features for an Incoming Thermal Event Record with physically sound defaults.
"""

from typing import Dict, Any, List
import numpy as np

try:
    from training.model_features import FEATURE_COLUMNS, LABELS
except ModuleNotFoundError:
    try:
        from aiengine.training.model_features import FEATURE_COLUMNS, LABELS
    except ModuleNotFoundError:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
        from training.model_features import FEATURE_COLUMNS, LABELS

FEATURE_NAMES = FEATURE_COLUMNS

# Physically sound defaults for satellite observations when sparse telemetry is provided
PHYSICAL_DEFAULTS = {
    # Default distances to infrastructure are remote (999 km), not 0 km (on top of flare)
    "distance_to_facility": 999.0,
    "distance_to_refinery": 999.0,
    "distance_to_flare": 999.0,
    "distance_to_powerplant": 999.0,
    "distance_to_mine": 999.0,
    "distance_to_quarry": 999.0,
    "distance_to_settlement": 25.0,
    "inside_facility_boundary": 0,
    "nearest_facility_count_500m": 0,
    "nearest_facility_count_1km": 0,
    "industrial_facility_density": 0.0,
    # Radiative & spectral nominal values
    "bright_ti4": 325.0,
    "bright_ti5": 298.0,
    "confidence_score": 0.85,
    "scan": 1.0,
    "track": 1.0,
    "day_night_numeric": 1.0,
    "temperature": 300.0,
    "relative_humidity": 50.0,
    "wind_speed": 12.0,
    "weather_fire_risk": 0.35,
    # Temporal baselines (nominal single event)
    "active_days": 1,
    "observation_count": 1,
    "span_days": 1,
    "active_day_ratio": 0.05,
    "persistence_score": 0.05,
    "stability_score": 0.1,
    "anomaly_score": 0.1,
    "flare_signature_score": 0.0,
    "event_frp_vs_source_median": 1.0,
    "event_frp_vs_source_mean": 1.0,
    "event_frp_zscore": 0.0,
    "event_frp_percentile": 50.0,
    "event_frp_ratio_previous": 1.0,
    "event_frp_change": 0.0,
    "event_intensity_deviation": 0.0,
    # Spatial clustering
    "cluster_size": 1,
    "spatial_extent_km": 0.375,
    "convex_hull_area": 0.14,
    "spread_rate_km_day": 0.0,
    "month": 3,
    "day_of_year": 75,
    "week_of_year": 11,
    "season": 1,
}


def prepare_feature_dict(event: Dict[str, Any]) -> Dict[str, float]:
    """
    Normalizes incoming event telemetry with physical sanity rules:
    - Resolves spatial coordinates to nearest registered facility when lat/lon are supplied
    - Derives context flags from probabilities or explicit distance indicators
    - Supplies realistic satellite defaults rather than 0.0
    """
    d = dict(event)

    # 1. Resolve coordinates to facility distance if lat/lon are given and distance is omitted
    if ("latitude" in d or "lat" in d) and ("longitude" in d or "lon" in d):
        lat = float(d.get("latitude", d.get("lat", 20.0)))
        lon = float(d.get("longitude", d.get("lon", 80.0)))
        if "distance_to_facility" not in d:
            try:
                from app.services.facility_service import load_facilities_master, _FACILITY_TREE, _FACILITIES_DF
                load_facilities_master()
                if _FACILITY_TREE is not None and _FACILITIES_DF is not None and len(_FACILITIES_DF) > 0:
                    rad = np.radians([[lat, lon]])
                    dist_rad, idx = _FACILITY_TREE.query(rad, k=1)
                    dist_km = float(dist_rad[0] * 6371.0)
                    d["distance_to_facility"] = dist_km
                    fac_type = str(_FACILITIES_DF.iloc[idx[0]].get("facility_type", "")).lower()
                    if "refinery" in fac_type:
                        d["distance_to_refinery"] = dist_km
                    elif "power" in fac_type:
                        d["distance_to_powerplant"] = dist_km
                    elif "mine" in fac_type:
                        d["distance_to_mine"] = dist_km
            except Exception:
                pass

    def _val(k, default=0.0):
        v = d.get(k)
        if v is None or v == "":
            return default
        try:
            return float(v)
        except (ValueError, TypeError):
            return default

    # 2. Derive context from probabilities if not explicitly given
    if _val("cropland_probability", 0.0) >= 0.4 and ("agricultural_context" not in d or d["agricultural_context"] is None):
        d["agricultural_context"] = 1.0
    if _val("forest_probability", 0.0) >= 0.4 and ("forest_context" not in d or d["forest_context"] is None):
        d["forest_context"] = 1.0
    if _val("bareland_probability", 0.0) >= 0.4 and ("bare_land_context" not in d or d["bare_land_context"] is None):
        d["bare_land_context"] = 1.0
    if (_val("distance_to_mine", 999.0) <= 2.5 or _val("distance_to_quarry", 999.0) <= 2.5 or _val("mining_context", 0.0) >= 0.5):
        if "mining_context" not in d or d["mining_context"] is None:
            d["mining_context"] = 1.0
        if "bare_land_context" not in d or d["bare_land_context"] is None:
            d["bare_land_context"] = 1.0
        if "bareland_probability" not in d or d["bareland_probability"] is None:
            d["bareland_probability"] = 0.85
        mine_dist = min(_val("distance_to_mine", 999.0), _val("distance_to_quarry", 999.0))
        d["distance_to_facility"] = mine_dist
        d["persistence_score"] = 0.85
        d["active_days"] = 180

    if _val("distance_to_facility", 999.0) <= 1.0 and _val("mining_context", 0.0) < 0.5:
        if "inside_facility_boundary" not in d or d["inside_facility_boundary"] is None:
            d["inside_facility_boundary"] = 1
        if "industrial_context" not in d or d["industrial_context"] is None:
            d["industrial_context"] = 1.0

    # 3. Assemble feature dict with physical defaults
    features = {}
    for col in FEATURE_NAMES:
        val = d.get(col)
        if val is None or val == "":
            val = PHYSICAL_DEFAULTS.get(col, 0.0)
        try:
            features[col] = float(val)
        except (ValueError, TypeError):
            features[col] = PHYSICAL_DEFAULTS.get(col, 0.0)

    return features


def build_feature_vector(event: Dict) -> list:
    """Returns an ordered list of feature values for model input."""
    clean_dict = prepare_feature_dict(event)
    return [clean_dict[col] for col in FEATURE_NAMES]
