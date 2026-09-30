"""
THERMOS Response Module - Incident Tracker, Acknowledgement, Escalation & Post-Incident Report Engine
Manages the closed-loop state machine, tracks latency metrics, and generates auditable post-incident reports.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import copy


class IncidentTracker:
    """Manages active incident response lifecycles, escalations, and audit reports."""

    def __init__(self):
        # In-memory incident repository
        self._incidents: Dict[str, Dict[str, Any]] = {}
        self._seed_default_incidents()

    def _seed_default_incidents(self):
        """Initializes realistic baseline active and historical response incidents for SIH demonstration."""
        now = datetime.now(timezone.utc)

        # Active Escalating Incident (Jamnagar Refinery Tank Farm)
        t_detect = now - timedelta(minutes=14, seconds=22)
        t_verify = now - timedelta(minutes=13, seconds=50)
        t_alert = now - timedelta(minutes=13, seconds=15)
        t_ack = now - timedelta(minutes=11, seconds=45)
        t_respond = now - timedelta(minutes=10, seconds=10)

        self._incidents["IND-2026-00417"] = {
            "incident_id": "IND-2026-00417",
            "event_id": "EV_100000",
            "state": "RESPONDING",
            "created_at": t_detect.isoformat(),
            "facility_name": "Jamnagar Refinery Complex",
            "facility_type": "refinery",
            "asset_name": "Storage Tank Farm Sector 4",
            "latitude": 22.4707,
            "longitude": 69.8320,
            "classification": "INDUSTRIAL_FIRE",
            "confidence": 96.4,
            "evidence_quality": 91.0,
            "operational_priority": "CRITICAL",
            "frp": 182.0,
            "baseline_median_mw": 27.0,
            "z_score": 5.7,
            "subpixel_temp_k": 1420,
            "radiant_area_m2": 210,
            "wind_speed_kmh": 14.0,
            "wind_direction": "NE",
            "primary_station": "Jamnagar Municipal Fire & Emergency Services (Digvijay Plot)",
            "primary_contact": "+91 288 255 0101",
            "primary_eta": "~9 min (4.9 km via road)",
            "backup_station": "Reliance Industrial Fire Brigade (Marine & SEZ Post)",
            "backup_eta": "~12 min (6.7 km via road)",
            "acknowledged_by": "Station Officer R. K. Patel (Jamnagar Fire Control)",
            "readiness_score_pct": 94,
            "latencies": {
                "detection_to_verification_sec": 32,
                "verification_to_dispatch_sec": 35,
                "dispatch_to_acknowledgement_sec": 90,
                "total_detection_to_response_sec": 157
            },
            "timeline": [
                {
                    "timestamp": t_detect.strftime("%H:%M:%S UTC"),
                    "stage": "DETECTION",
                    "title": "Satellite Thermal Anomaly Observed",
                    "desc": "VIIRS NOAA-20 pass detected acute thermal radiant emission (168 MW) at Jamnagar perimeter.",
                    "status_code": "DETECTED"
                },
                {
                    "timestamp": t_verify.strftime("%H:%M:%S UTC"),
                    "stage": "VERIFICATION",
                    "title": "3-Stage Verification Gate Cleared",
                    "desc": "Corroborated by NOAA-21 and MODIS Aqua (+5.7sigma regime break). Emergency response qualified.",
                    "status_code": "VERIFIED"
                },
                {
                    "timestamp": t_alert.strftime("%H:%M:%S UTC"),
                    "stage": "DISPATCH",
                    "title": "Pre-Arrival Intelligence Packet Dispatched",
                    "desc": "Emergency signal routed to Primary Station (Digvijay Plot) and Plant Safety Desk.",
                    "status_code": "SENT"
                },
                {
                    "timestamp": t_ack.strftime("%H:%M:%S UTC"),
                    "stage": "ACKNOWLEDGEMENT",
                    "title": "Alert Acknowledged by Primary Station",
                    "desc": "Station Officer R. K. Patel confirmed receipt via ERSS-112 CAD terminal. Latency: 90s.",
                    "status_code": "ACKNOWLEDGED"
                },
                {
                    "timestamp": t_respond.strftime("%H:%M:%S UTC"),
                    "stage": "RESPONSE",
                    "title": "Hazmat Foam Tender Dispatched",
                    "desc": "Heavy Pumper-01 and Foam Tender-02 en route to Gate 3 (Estimated travel time: 9 min).",
                    "status_code": "RESPONDING"
                }
            ]
        }

        # Second Incident: Singrauli Coal Mine Seam Fire (Acknowledged)
        t2_detect = now - timedelta(minutes=38)
        t2_verify = now - timedelta(minutes=37)
        t2_alert = now - timedelta(minutes=36)
        t2_ack = now - timedelta(minutes=34)

        self._incidents["MINE-2026-00912"] = {
            "incident_id": "MINE-2026-00912",
            "event_id": "EV_100015",
            "state": "ACKNOWLEDGED",
            "created_at": t2_detect.isoformat(),
            "facility_name": "Singrauli Jayant OCP",
            "facility_type": "coal_mine",
            "asset_name": "Open-Cast Coal Pit Sector 3 Overburden",
            "latitude": 24.1200,
            "longitude": 82.6600,
            "classification": "MINING",
            "confidence": 94.6,
            "evidence_quality": 88.0,
            "operational_priority": "HIGH",
            "frp": 164.2,
            "baseline_median_mw": 32.0,
            "z_score": 4.8,
            "subpixel_temp_k": 880,
            "radiant_area_m2": 260,
            "wind_speed_kmh": 11.0,
            "wind_direction": "E",
            "primary_station": "CISF Fire Wing - Northern Coalfields (Jayant Station)",
            "primary_contact": "+91 7805 222 101",
            "primary_eta": "~7 min (3.2 km via road)",
            "backup_station": "Singrauli Municipal Fire Station (Morwa)",
            "backup_eta": "~16 min (8.9 km via road)",
            "acknowledged_by": "Inspector V. Sharma (CISF Fire Wing)",
            "readiness_score_pct": 91,
            "latencies": {
                "detection_to_verification_sec": 45,
                "verification_to_dispatch_sec": 40,
                "dispatch_to_acknowledgement_sec": 120,
                "total_detection_to_response_sec": 205
            },
            "timeline": [
                {
                    "timestamp": t2_detect.strftime("%H:%M:%S UTC"),
                    "stage": "DETECTION",
                    "title": "Subsurface Coal Seam Excursion Detected",
                    "desc": "VIIRS MWIR observed 164 MW anomaly at central pit boundary.",
                    "status_code": "DETECTED"
                },
                {
                    "timestamp": t2_verify.strftime("%H:%M:%S UTC"),
                    "stage": "VERIFICATION",
                    "title": "Mining Thermal Verification Cleared",
                    "desc": "High persistence over 14 days and bare overburden spectral match confirmed.",
                    "status_code": "VERIFIED"
                },
                {
                    "timestamp": t2_alert.strftime("%H:%M:%S UTC"),
                    "stage": "DISPATCH",
                    "title": "Mine Safety Unit Notified",
                    "desc": "Alert sent to CISF Fire Station and Mine Director.",
                    "status_code": "SENT"
                },
                {
                    "timestamp": t2_ack.strftime("%H:%M:%S UTC"),
                    "stage": "ACKNOWLEDGEMENT",
                    "title": "Acknowledged by CISF Station",
                    "desc": "Inspector V. Sharma initiated nitrogen inerting squad standby.",
                    "status_code": "ACKNOWLEDGED"
                }
            ]
        }

    def list_incidents(self) -> List[Dict[str, Any]]:
        """Returns all registered response incidents."""
        return list(self._incidents.values())

    def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific incident record."""
        return self._incidents.get(incident_id)

    def acknowledge_incident(self, incident_id: str, responder_name: str = "Duty Dispatch Officer") -> Dict[str, Any]:
        """Transitions incident state to ACKNOWLEDGED and records latency."""
        inc = self._incidents.get(incident_id)
        if not inc:
            return {"error": "Incident not found"}

        now_str = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        inc["state"] = "ACKNOWLEDGED"
        inc["acknowledged_by"] = responder_name
        inc["timeline"].append({
            "timestamp": now_str,
            "stage": "ACKNOWLEDGEMENT",
            "title": f"Manual Acknowledgement Recorded ({responder_name})",
            "desc": f"Duty officer confirmed alert receipt. Incident clock stopped.",
            "status_code": "ACKNOWLEDGED"
        })
        return inc

    def set_responding(self, incident_id: str, unit_callsign: str = "Engine-01") -> Dict[str, Any]:
        """Transitions incident state to RESPONDING."""
        inc = self._incidents.get(incident_id)
        if not inc:
            return {"error": "Incident not found"}

        now_str = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        inc["state"] = "RESPONDING"
        inc["timeline"].append({
            "timestamp": now_str,
            "stage": "RESPONSE",
            "title": f"Units En Route ({unit_callsign})",
            "desc": f"Response units mobilized from station. Transponder tracking activated on ERSS-112 CAD.",
            "status_code": "RESPONDING"
        })
        return inc

    def trigger_escalation(self, incident_id: str) -> Dict[str, Any]:
        """Simulates automatic escalation when primary station is unacknowledged."""
        inc = self._incidents.get(incident_id)
        if not inc:
            return {"error": "Incident not found"}

        now_str = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        inc["state"] = "ESCALATED"
        inc["timeline"].append({
            "timestamp": now_str,
            "stage": "ESCALATION",
            "title": "Automatic Escalation Triggered (Unacknowledged Timeout)",
            "desc": f"Primary responder unacknowledged after 2m. Alert cascaded to Backup Responder ({inc.get('backup_station')}) and District EOC.",
            "status_code": "ESCALATED"
        })
        return inc

    def resolve_incident(self, incident_id: str, resolution_notes: str = "Thermal emission contained") -> Dict[str, Any]:
        """Resolves incident and seals the audit record."""
        inc = self._incidents.get(incident_id)
        if not inc:
            return {"error": "Incident not found"}

        now_str = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        inc["state"] = "RESOLVED"
        inc["timeline"].append({
            "timestamp": now_str,
            "stage": "RESOLUTION",
            "title": "Incident Resolved & Contained",
            "desc": f"{resolution_notes}. Thermal signature returned to historical baseline. Closed-loop cycle complete.",
            "status_code": "RESOLVED"
        })
        return inc

    def generate_post_incident_report(self, incident_id: str) -> Dict[str, Any]:
        """Generates an auditable post-incident evidence dossier."""
        inc = self._incidents.get(incident_id)
        if not inc:
            return {"error": "Incident not found"}

        return {
            "report_id": f"PIR-{incident_id}",
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "executive_summary": {
                "incident_id": incident_id,
                "facility": inc["facility_name"],
                "asset": inc["asset_name"],
                "final_classification": inc["classification"],
                "peak_frp_mw": inc["frp"],
                "baseline_excursion": f"+{inc['z_score']}sigma",
                "final_state": inc["state"],
                "total_response_latency": f"{inc['latencies']['total_detection_to_response_sec']} seconds"
            },
            "timeline_audit_trail": inc["timeline"],
            "responders_involved": [
                {"role": "Primary", "station": inc["primary_station"], "eta": inc["primary_eta"]},
                {"role": "Backup", "station": inc["backup_station"], "eta": inc["backup_eta"]}
            ],
            "data_provenance_verification": {
                "satellite_telemetry": "NASA VIIRS NOAA-20 / NOAA-21 NRT Active Fire",
                "verification_protocol": "THERMOS 3-Stage Closed-Loop Response Protocol",
                "erss_interoperability": "OASIS CAP-IN v1.0 Compliant"
            }
        }


# Singleton tracker instance
incident_tracker = IncidentTracker()

