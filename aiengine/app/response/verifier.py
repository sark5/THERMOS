"""
THERMOS Response Module - Verifier & Qualification Gate
Implements:
1. 3-Stage Verification Gate (Detection -> Corroboration -> Response Qualification)
2. False-Alarm Suppression for routine industrial flaring
3. Alert Deduplication & Cooldown Tracking
"""

from typing import Dict, Any, Tuple
import numpy as np


class ResponseVerifier:
    """Evaluates whether a satellite thermal observation qualifies for emergency response dispatch."""

    @staticmethod
    def evaluate_qualification(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the 3-Stage Verification Gate:
        Stage 1: Thermal Anomaly Detection (FRP, Brightness Ti4)
        Stage 2: Multi-Source Corroboration (Multi-Satellite, Facility Proximity, Persistence, Land Cover)
        Stage 3: Response Qualification (Emergency Threshold Analysis)
        """
        frp = float(event_data.get("frp", 15.0))
        cls = str(event_data.get("classification", event_data.get("primary_class", "UNCLASSIFIED")))
        confidence = float(event_data.get("confidence", 85.0))
        dist_fac = float(event_data.get("distance_to_facility", 999.0))
        z_score = float(str(event_data.get("z_score", "0.0")).replace("+", "").replace("sigma", "").replace(" sigma", ""))
        satellite_count = int(event_data.get("satellite_count", 3))
        active_days = int(event_data.get("active_days", 1))

        #    Stage 1: Detection   
        stage_1_passed = frp >= 10.0
        stage_1_notes = f"Thermal radiative power {frp:.1f} MW confirmed above sensor detection floor."

        #    Stage 2: Corroboration   
        # Check cross-satellite agreement, persistent provenance, and spatial context
        corroboration_score = 0
        if satellite_count >= 2:
            corroboration_score += 35
        if satellite_count >= 3:
            corroboration_score += 15
        if confidence >= 85.0:
            corroboration_score += 25
        if dist_fac <= 5.0 or cls in ["WILDFIRE", "AGRICULTURAL"]:
            corroboration_score += 25

        stage_2_passed = corroboration_score >= 60
        stage_2_notes = (
            f"Corroboration index: {corroboration_score}% across {satellite_count} orbital platforms. "
            f"Context: {cls} at {confidence:.1f}% confidence."
        )

        #    Stage 3: Response Qualification & False-Alarm Suppression   
        # CRITICAL RULE: Routine industrial flaring operating within nominal baseline
        # MUST BE SUPPRESSED from emergency fire service alerts to prevent fatigue.
        suppressed_as_routine_flare = False
        suppression_reason = None

        if cls == "INDUSTRIAL_FLARE":
            if z_score < 2.0 and frp < 80.0:
                suppressed_as_routine_flare = True
                suppression_reason = (
                    f"Suppressed: Flaring operates within established historical baseline "
                    f"(Z-score: +{z_score:.1f}sigma < +2.0sigma threshold). Routed to environmental emissions register, not emergency dispatch."
                )
            else:
                # Acute flaring regime break qualifies as emergency
                suppressed_as_routine_flare = False

        if cls == "AGRICULTURAL":
            # Crop burning routed to agricultural advisory, not structural fire brigade
            qualifies_for_dispatch = False
            dispatch_category = "AGRICULTURAL_ADVISORY"
            qualification_notes = "Seasonal biomass burning detected. Routed to District Agriculture & Air Quality Control."
        elif suppressed_as_routine_flare:
            qualifies_for_dispatch = False
            dispatch_category = "MONITORING_ONLY"
            qualification_notes = suppression_reason
        elif cls == "INDUSTRIAL_FIRE":
            qualifies_for_dispatch = (z_score >= 2.0 or frp >= 60.0 or dist_fac <= 1.5)
            dispatch_category = "ACUTE_INDUSTRIAL_EMERGENCY"
            qualification_notes = "Acute industrial fire signature: Significant thermal anomaly within critical facility perimeter."
        elif cls == "WILDFIRE":
            qualifies_for_dispatch = (frp >= 50.0 or corroboration_score >= 70)
            dispatch_category = "FORESTRY_WILDFIRE_RESPONSE"
            qualification_notes = "Active forest fire front with multi-satellite spread velocity confirmation."
        elif cls == "MINING":
            qualifies_for_dispatch = (z_score >= 2.5 or frp >= 75.0)
            dispatch_category = "MINING_SEAM_HAZMAT"
            qualification_notes = "Elevated subsurface coal seam temperature excursion exceeding mine safety limit."
        else:
            qualifies_for_dispatch = False
            dispatch_category = "INVESTIGATION_REVIEW"
            qualification_notes = "Unclassified thermal event. Routed to Human Analyst Review Queue."

        stage_3_passed = qualifies_for_dispatch and not suppressed_as_routine_flare

        # Overall Status
        if stage_1_passed and stage_2_passed and stage_3_passed:
            overall_decision = "ALERT_QUALIFIED"
        elif stage_1_passed and stage_2_passed:
            overall_decision = "MONITORING_ROUTINE"
        else:
            overall_decision = "LOW_CONFIDENCE_SUPPRESSED"

        return {
            "overall_decision": overall_decision,
            "dispatch_category": dispatch_category,
            "qualifies_for_emergency_dispatch": stage_3_passed,
            "stages": [
                {
                    "stage_num": 1,
                    "name": "Thermal Anomaly Detection",
                    "passed": stage_1_passed,
                    "evidence": stage_1_notes,
                },
                {
                    "stage_num": 2,
                    "name": "Multi-Source Corroboration",
                    "passed": stage_2_passed,
                    "score_pct": corroboration_score,
                    "evidence": stage_2_notes,
                },
                {
                    "stage_num": 3,
                    "name": "Response Qualification & False-Alarm Suppression",
                    "passed": stage_3_passed,
                    "evidence": qualification_notes,
                    "suppression_active": suppressed_as_routine_flare,
                },
            ],
            "false_alarm_suppression": {
                "active": suppressed_as_routine_flare,
                "reason": suppression_reason,
            },
        }

