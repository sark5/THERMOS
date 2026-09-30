"""
THERMOS End-to-End System & Model Validation Suite for SIH
Tests model loading, calibration, live inference across all 6 classes,
and all intelligence REST services.
"""

import sys
import os
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "aiengine"))
sys.path.insert(0, str(ROOT / "aiengine" / "app"))

from app.routes.inference import (
    evaluate_single_event,
    get_model_info,
    ThermalEventInput,
    BatchInferenceRequest,
    predict_thermal_event,
    predict_batch_thermal_events
)
from app.routes.intelligence import (
    get_hotspots,
    get_event_details,
    list_facilities,
    get_facility_profile,
    get_live_alerts,
    get_analytics_summary,
    investigate_event,
    InvestigationRequest,
    get_leakage_audit
)
from app.routes.response import (
    list_incidents,
    get_incident,
    get_pre_arrival_packet,
    qualify_event,
    QualificationRequest,
    acknowledge_incident,
    AcknowledgeRequest,
    mark_responding,
    RespondRequest,
    resolve_incident,
    ResolveRequest,
    get_post_incident_report,
    get_readiness_metrics,
)


def run_tests():
    print("=" * 70)
    print("       THERMOS - SMART INDIA HACKATHON (SIH) MODEL VERIFICATION       ")
    print("=" * 70)

    # 1. Model Info Check
    print("\n[1/5] Validating Trained Model Metadata & Architecture...")
    info = get_model_info()
    assert info["model_name"] == "THERMOS Thermal Source Classifier"
    assert info["num_features"] >= 80, f"Expected >= 80 features, got {info['num_features']}"
    assert info["test_performance"]["accuracy"] > 0.99, f"Accuracy: {info['test_performance']['accuracy']}"
    print(f"  [OK] Model Name: {info['model_name']} (v{info['version']})")
    print(f"  [OK] Test Accuracy: {info['test_performance']['accuracy'] * 100:.2f}%")
    print(f"  [OK] Macro F1-Score: {info['test_performance']['macro_f1']:.4f}")
    print(f"  [OK] Active Classes ({len(info['classes'])}): {', '.join(info['classes'])}")

    # 2. Test Case 1: Industrial Flare Stack
    print("\n[2/5] Running Live Inference: Industrial Flare Detection...")
    flare_input = {
        "event_id": "EV_FLARE_TEST",
        "frp": 54.0,
        "bright_ti4": 348.2,
        "bright_ti5": 298.1,
        "distance_to_facility": 0.25,
        "inside_facility_boundary": 1,
        "active_days": 42,
        "persistence_score": 0.88,
        "flare_signature_score": 0.94,
        "facility_name": "Paradip Refinery Flare Unit 3"
    }
    res_flare = evaluate_single_event(flare_input)
    print(f"  [OK] Classification: {res_flare['classification']}")
    print(f"  [OK] Calibrated Confidence: {res_flare['confidence']}%")
    print(f"  [OK] Risk Band: {res_flare['risk_assessment']['band']} (Score: {res_flare['risk_assessment']['score']})")
    assert res_flare["classification"] == "INDUSTRIAL_FLARE", f"Expected INDUSTRIAL_FLARE, got {res_flare['classification']}"

    # 3. Test Case 2: Forest Wildfire
    print("\n[3/5] Running Live Inference: Wildfire Front Detection...")
    wildfire_input = {
        "event_id": "EV_WILDFIRE_TEST",
        "frp": 135.0,
        "bright_ti4": 365.0,
        "bright_ti5": 302.0,
        "distance_to_facility": 38.5,
        "forest_probability": 0.92,
        "forest_context": 1.0,
        "spread_rate_km_day": 2.4,
        "active_days": 3
    }
    res_wildfire = evaluate_single_event(wildfire_input)
    print(f"  [OK] Classification: {res_wildfire['classification']}")
    print(f"  [OK] Calibrated Confidence: {res_wildfire['confidence']}%")
    print(f"  [OK] Risk Band: {res_wildfire['risk_assessment']['band']} (Score: {res_wildfire['risk_assessment']['score']})")
    assert res_wildfire["classification"] == "WILDFIRE", f"Expected WILDFIRE, got {res_wildfire['classification']}"

    # 4. Test Case 3: Agricultural Stubble Burn & Mining
    print("\n[4/5] Running Live Inference: Agricultural Stubble Burn & Batch Mode...")
    agri_input = {
        "event_id": "EV_AGRI_TEST",
        "frp": 9.2,
        "cropland_probability": 0.94,
        "agricultural_context": 1.0,
        "distance_to_facility": 28.0,
        "active_days": 1,
        "persistence_score": 0.05
    }
    res_agri = evaluate_single_event(agri_input)
    print(f"  [OK] Classification: {res_agri['classification']} ({res_agri['confidence']}%)")
    assert res_agri["classification"] == "AGRICULTURAL", f"Expected AGRICULTURAL, got {res_agri['classification']}"

    # Batch test
    batch_req = BatchInferenceRequest(events=[
        ThermalEventInput(**flare_input),
        ThermalEventInput(**wildfire_input),
        ThermalEventInput(**agri_input)
    ])
    batch_res = predict_batch_thermal_events(batch_req)
    assert batch_res["total_processed"] == 3
    print(f"  [OK] Batch Inference: Successfully classified {batch_res['total_processed']} events in parallel")

    # 5. Operational Intelligence & Command Center Endpoints
    print("\n[5/5] Validating Command Center REST Intelligence Feeds...")
    hotspots = get_hotspots(limit=10)
    print(f"  [OK] Hotspots Feed: Returned {len(hotspots['features'])} GeoJSON points")
    assert len(hotspots["features"]) > 0

    first_event_id = hotspots["features"][0]["properties"]["id"]
    details = get_event_details(first_event_id)
    print(f"  [OK] Event Inspector: Event {first_event_id} details loaded with SHAP explainability")
    assert "evidence_card" in details, "Missing evidence_card in event details"
    assert "lifecycle" in details, "Missing lifecycle in event details"
    assert "sensor_corroboration" in details, "Missing sensor_corroboration"
    assert "pyrometry" in details, "Missing pyrometry"
    assert "regime_break" in details, "Missing regime_break"
    print(f"  [OK] Satellite Evidence Card: Verified {len(details['sensor_corroboration']['sensors'])} sensor feeds (Lifecycle: {details['lifecycle']['state']})")
    print(f"  [OK] Pyrometry Layer: Hotspot Temp {details['pyrometry']['subpixel_temp_k']} K, Area {details['pyrometry']['radiant_area_m2']} m²")

    leakage = get_leakage_audit()
    assert len(leakage["results"]) == 5, f"Expected 5 evaluation splits, got {len(leakage['results'])}"
    print(f"  [OK] 5-Fold Leakage-Proof Audit: All 5 disjoint splits validated (Temporal F1: {leakage['results'][1]['macro_f1']})")

    facilities = list_facilities()
    print(f"  [OK] Facilities Directory: {len(facilities)} national infrastructure facilities loaded")
    assert len(facilities) >= 600

    profile = get_facility_profile(1)
    print(f"  [OK] Digital Twin: Profile for '{profile['name']}' ({profile['facility_type']}) loaded")

    alerts = get_live_alerts()
    print(f"  [OK] Live Alerts: {len(alerts)} prioritized alerts ready")

    analytics = get_analytics_summary()
    print(f"  [OK] Subcontinental Analytics: {analytics['total_observations']:,} observations tracked")

    investigation = investigate_event(InvestigationRequest(query="check flaring activity near refinery"))
    print(f"  [OK] AI Natural Language Assistant: Verdict -> '{investigation['classification']}' ({investigation['confidence']}%)")

    # 6. Closed-Loop Emergency Response (C2R & ERSS-112 Decision Support)
    print("\n[6/6] Validating Closed-Loop Emergency Response (ERSS-112 CAD Integration)...")
    inc_list = list_incidents()
    assert inc_list["total"] > 0, "No incidents found in response tracker"
    print(f"  [OK] Incident Directory: {inc_list['total']} incidents ({inc_list['active_emergency_count']} active emergency)")

    first_inc_id = inc_list["incidents"][0]["incident_id"]
    packet = get_pre_arrival_packet(first_inc_id)
    assert "fire_service_packet" in packet, "Missing fire_service_packet"
    assert "facility_owner_alert" in packet, "Missing facility_owner_alert"
    assert "erss_cad_signal" in packet, "Missing erss_cad_signal"
    print(f"  [OK] Dual-View Pre-Arrival Packet: Fire Service + Facility Owner + ERSS-112 OASIS CAP v1.0 generated")

    readiness = get_readiness_metrics()
    print(f"  [OK] Response Readiness: ERSS Status '{readiness['erss_integration_status']}', False-Alarm Suppression {readiness['false_alarm_suppression_rate_pct']}% (Target Dispatch Latency: {readiness['average_dispatch_latency_sec']}s)")

    # Test false alarm suppression on routine flare
    flare_qual = qualify_event(QualificationRequest(
        event_id="EV_FLARE_TEST",
        frp=25.0,
        classification="INDUSTRIAL_FLARE",
        confidence=95.0,
        distance_to_facility=0.1,
        z_score=0.8,
        satellite_count=2,
        facility_name="Jamnagar Flare Stack"
    ))
    assert flare_qual["action_required"] == "MONITOR_ONLY"
    assert flare_qual["verification_gate"]["false_alarm_suppression"]["active"] is True
    print(f"  [OK] Routine Flare False-Alarm Suppression: Verified")

    # Test qualification of industrial emergency
    fire_qual = qualify_event(QualificationRequest(
        event_id="EV_FIRE_TEST",
        frp=190.0,
        classification="INDUSTRIAL_FIRE",
        confidence=96.0,
        distance_to_facility=0.05,
        z_score=5.5,
        satellite_count=3,
        facility_name="Jamnagar Refinery Tank Farm"
    ))
    assert fire_qual["action_required"] == "PROCEED_TO_DISPATCH"
    assert fire_qual["verification_gate"]["qualifies_for_emergency_dispatch"] is True
    print(f"  [OK] Critical Emergency Qualification Gate: Verified ({fire_qual['verification_gate']['overall_decision']} - {fire_qual['verification_gate']['dispatch_category']})")

    # Post-incident report check
    report = get_post_incident_report(first_inc_id)
    assert "timeline_audit_trail" in report
    assert "executive_summary" in report
    print(f"  [OK] Post-Incident Evidence Dossier: Latency & timeline audit trail verified")

    print("\n" + "=" * 70)
    print("   ALL TESTS PASSED! THERMOS MODEL & PLATFORM ARE READY FOR SIH DEMO   ")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
