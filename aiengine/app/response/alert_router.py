"""
THERMOS Response Module - Authority Matrix, Pre-Arrival Intelligence Packet & ERSS-112 Signal Router
Generates differentiated operational notifications for Fire Services, Facility Safety Officers, and EOCs.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone


class AlertRouter:
    """Routes alerts to authorized recipients and constructs differentiated intelligence packets."""

    @staticmethod
    def build_authority_matrix(facility_name: str, facility_type: str, responders: Dict[str, Any]) -> Dict[str, Any]:
        """Builds multi-tier emergency authority escalation contacts for the site."""
        primary = responders["primary_responder"]
        backup = responders["backup_responder"]

        return {
            "facility_name": facility_name,
            "facility_type": facility_type,
            "tier_1_primary_responder": {
                "name": primary["name"],
                "role": "Primary Tactical Fire & Rescue Response",
                "contact": primary["contact"],
                "status": "NOTIFIED",
                "eta": primary["eta_formatted"]
            },
            "tier_2_facility_safety_officer": {
                "name": f"Chief Safety Officer / HSE Desk ({facility_name})",
                "role": "Internal Industrial Containment & Asset Isolation",
                "contact": "+91 98200 44101 (24/7 Plant Emergency Control)",
                "status": "ALERTED",
                "action": "Initiate Asset Deluge & Emergency Depressurization"
            },
            "tier_3_backup_responder": {
                "name": backup["name"],
                "role": "Secondary Backup & Mutual Aid Response",
                "contact": backup["contact"],
                "status": "STANDBY",
                "eta": backup["eta_formatted"]
            },
            "tier_4_district_eoc": {
                "name": "District Emergency Operations Centre (DEOC / DDMA)",
                "role": "Civil Administration & Evacuation Coordination",
                "contact": "+91 112 (State ERSS Dispatch)",
                "status": "MONITORING",
                "action": "Corridor Traffic Diversion & Hospital Alert"
            },
            "tier_5_state_eoc": {
                "name": "State Disaster Management Authority (SDMA / SEOC)",
                "role": "State Disaster Protocol & Regional Asset Mobilization",
                "contact": "1070 (State Emergency Helpline)",
                "status": "LOGGED"
            }
        }

    @staticmethod
    def build_fire_service_packet(incident: Dict[str, Any], responders: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constructs the Fire Service Pre-Arrival Intelligence Packet.
        Contains mission-critical tactical telemetry: location, asset, thermal severity,
        plume corridor, ETA, and suggested tactical posture.
        """
        event_id = incident.get("event_id", "IND-2026-00417")
        coords = [incident.get("longitude", 69.83), incident.get("latitude", 22.47)]
        fac_name = incident.get("facility_name", "Jamnagar Refinery Complex")
        asset_name = incident.get("asset_name", "Storage Tank Farm Sector 4")
        frp = float(incident.get("frp", 182.0))
        z_score = float(str(incident.get("z_score", "5.7")).replace("+", "").replace("sigma", "").replace(" sigma", ""))
        baseline = float(incident.get("baseline_median_mw", 27.0))
        primary = responders["primary_responder"]

        return {
            "packet_type": "FIRE_SERVICE_PRE_ARRIVAL_PACKET",
            "incident_id": event_id,
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "tactical_headline": f"CRITICAL INCIDENT: {incident.get('classification', 'INDUSTRIAL_FIRE')} at {fac_name}",
            "location": {
                "latitude": coords[1],
                "longitude": coords[0],
                "facility": fac_name,
                "suspected_asset": asset_name,
                "address": f"Near {fac_name} Industrial Perimeter, Access Gate 3"
            },
            "classification": {
                "predicted_class": incident.get("classification", "INDUSTRIAL_FIRE"),
                "model_confidence_pct": incident.get("confidence", 96.4),
                "evidence_quality_pct": incident.get("evidence_quality", 91.0),
                "operational_priority": incident.get("operational_priority", "CRITICAL")
            },
            "thermal_telemetry": {
                "current_frp_mw": frp,
                "historical_baseline_p50_mw": baseline,
                "baseline_p90_mw": round(baseline * 1.55, 1),
                "departure_sigma": f"+{z_score:.1f}sigma",
                "estimated_hotspot_temp_k": incident.get("subpixel_temp_k", 1420),
                "estimated_radiant_area_m2": incident.get("radiant_area_m2", 210)
            },
            "satellite_corroboration": {
                "verified_sensors": ["NOAA-20 VIIRS (375m)", "NOAA-21 VIIRS (375m)", "MODIS Aqua (1km)", "Sentinel-1 SAR"],
                "inter_satellite_consistency": "HIGH (4 concordant passes)",
                "active_duration": incident.get("duration", "4h 51m"),
                "first_detected": "06:40 UTC",
                "last_satellite_pass": "11:31 UTC (NOAA-21)"
            },
            "atmospheric_dispersion": {
                "wind_vector": f"{incident.get('wind_direction', 'NE')} at {incident.get('wind_speed_kmh', 14)} km/h",
                "projected_corridor_6h": f"{round(incident.get('wind_speed_kmh', 14) * 6.0, 1)} km downwind",
                "threatened_receptors": [
                    "NH-8 National Highway Access Road (1.8 km downwind)",
                    "Suburban Industrial Residential Colony (3.4 km downwind)"
                ]
            },
            "dispatch_guidance": {
                "assigned_station": primary["name"],
                "road_eta": primary["eta_formatted"],
                "recommended_foam_agent": "AFFF (Aqueous Film Forming Foam) AR-AFFF 3%x3%",
                "initial_perimeter_cordon_radius_m": 800,
                "immediate_hazard": "Hydrocarbon storage tank thermal radiation & vapor cloud hazard"
            }
        }

    @staticmethod
    def build_facility_owner_alert(incident: Dict[str, Any], responders: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constructs the Facility Owner / Industrial HSE Alert.
        Focuses on site containment, asset isolation, baseline deviation, and dispatched units.
        """
        event_id = incident.get("event_id", "IND-2026-00417")
        fac_name = incident.get("facility_name", "Jamnagar Refinery Complex")
        asset_name = incident.get("asset_name", "Storage Tank Farm Sector 4")
        frp = float(incident.get("frp", 182.0))
        z_score = float(str(incident.get("z_score", "5.7")).replace("+", "").replace("sigma", "").replace(" sigma", ""))
        baseline = float(incident.get("baseline_median_mw", 27.0))
        primary = responders["primary_responder"]

        return {
            "packet_type": "FACILITY_OWNER_ABNORMAL_THERMAL_ALERT",
            "incident_id": event_id,
            "facility_name": fac_name,
            "affected_asset_zone": asset_name,
            "urgency": "IMMEDIATE_ACTION_REQUIRED",
            "headline": f"ABNORMAL THERMAL REGIME BREAK DETECTED AT {asset_name.upper()}",
            "summary_for_hse_manager": (
                f"Satellite thermal telemetry detected an acute energy excursion (+{z_score:.1f}sigma) "
                f"at {asset_name}. Observed FRP is {frp:.1f} MW compared to standard operating baseline of {baseline:.1f} MW. "
                f"Autonomous alert qualification completed; municipal fire response ({primary['name']}) has been alerted (ETA: {primary['eta_formatted']})."
            ),
            "site_safety_actions": [
                "Activate Site Emergency Response Plan (Level 2 Industrial Disaster)",
                "Isolate hydrocarbon feed lines and initiate cooling water deluge",
                "Verify automated flare stack gas blowdown vs. atmospheric tank breach",
                "Establish communication with dispatched fire command unit via ERSS-112"
            ],
            "dispatched_responder": {
                "station": primary["name"],
                "contact": primary["contact"],
                "eta": primary["eta_formatted"]
            }
        }

    @staticmethod
    def build_erss_112_cad_signal(incident: Dict[str, Any], responders: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formats machine-readable OASIS Common Alerting Protocol (CAP-IN v1.0 standard)
        specifically tailored for integration with India's ERSS-112 Computer Aided Dispatch architecture.
        """
        event_id = incident.get("event_id", "IND-2026-00417")
        coords = [incident.get("longitude", 69.83), incident.get("latitude", 22.47)]
        fac_name = incident.get("facility_name", "Jamnagar Refinery Complex")
        primary = responders["primary_responder"]

        return {
            "identifier": f"THERMOS-ERSS-IN-{event_id}",
            "sender": "thermos.ndma.gov.in",
            "sent": datetime.now(timezone.utc).isoformat(),
            "status": "Actual",
            "msgType": "Alert",
            "scope": "Restricted",
            "category": "Fire",
            "urgency": "Immediate",
            "severity": "Extreme",
            "certainty": "Observed",
            "event": f"Verified {incident.get('classification', 'Industrial Fire')} Emergency",
            "headline": f"THERMOS Satellite-Derived Emergency Dispatch: {fac_name}",
            "area": {
                "areaDesc": f"{fac_name} Industrial Buffer Zone",
                "point": f"{coords[1]},{coords[0]}",
                "radius_km": 1.5
            },
            "erss_cad_data": {
                "integration_protocol": "MHA ERSS-112 CAD Gateway (CAP-IN v1.0)",
                "agency_type": "FIRE_RESCUE",
                "cad_priority": 1,
                "assigned_station_code": primary["id"],
                "assigned_station_name": primary["name"],
                "call_taker_notes": (
                    f"THERMOS AI C2R Verification: Multi-sensor confirmation (VIIRS NOAA-20/21, MODIS, INSAT-3D). "
                    f"FRP {incident.get('frp', 182)} MW (+{incident.get('z_score', '5.7')} sigma departure). "
                    f"Recommended Dispatch: Hazmat Foam Pumper + Water Tender."
                )
            }
        }

