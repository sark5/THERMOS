from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class LabelEvidence:

    label: str

    score: float

    quality: str

    reasons: List[str] = field(
        default_factory=list
    )

    evidence: Dict[str, float] = field(
        default_factory=dict
    )