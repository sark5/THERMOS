export type ThermalClass =
  | 'INDUSTRIAL_FLARE'
  | 'INDUSTRIAL_FIRE'
  | 'MINING'
  | 'AGRICULTURAL'
  | 'WILDFIRE'
  | 'UNCLASSIFIED';

export type RiskBand = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export type LifecycleState =
  | 'DETECTED'
  | 'CORROBORATING'
  | 'CLASSIFIED'
  | 'MONITORING'
  | 'ESCALATING'
  | 'CONTAINED'
  | 'RESOLVED'
  | 'ARCHIVED';

export interface EventLifecycle {
  state: LifecycleState;
  duration_formatted: string;
  first_seen: string;
  last_seen: string;
  source_count: number;
  satellite_count: number;
  frp_growth_rate_mw_hr: number;
}

export interface DecoupledMetrics {
  classification_confidence_pct: number;
  evidence_quality_pct: number;
  operational_priority_score: number;
  operational_priority_band: RiskBand;
  ood_status: 'IN_DISTRIBUTION' | 'BORDERLINE_OOD' | 'OUT_OF_DISTRIBUTION';
  mahalanobis_distance: number;
  conformal_prediction_set: ThermalClass[];
  conformal_coverage: string;
}

export interface SensorCorroborationItem {
  sensor_name: string;
  resolution: string;
  channel_info: string;
  status: 'CONFIRMED' | 'DETECTED' | 'OBSCURED_CLOUD' | 'COMPATIBLE_SAR' | 'COARSE_RESOLUTION_LIMIT' | 'OFF_PASS';
  telemetry_snippet: string;
  timestamp_utc: string;
}

export interface SensorCorroboration {
  sensors: SensorCorroborationItem[];
  corroboration_score_pct: number;
  summary: string;
}

export interface ThermalPyrometry {
  nightfire_method: string;
  subpixel_temp_k: number;
  radiant_area_m2: number;
  radiant_heat_flux_kw_m2: number;
  uncertainty_semi_major_m: number;
  uncertainty_semi_minor_m: number;
}

export interface AssetAttribution {
  facility_name: string;
  facility_type: string;
  operator: string;
  asset_name: string;
  asset_type: string;
  distance_to_asset_m: number;
  inside_asset_boundary: boolean;
}

export interface ThermalRegimeBreak {
  baseline_median_mw: number;
  baseline_p90_mw: number;
  baseline_p99_mw: number;
  current_frp_mw: number;
  z_score_sigma: number;
  departure_pct: number;
  regime_status: 'REGIME_BREAK' | 'ELEVATED_ANOMALY' | 'NOMINAL_REGIME';
  change_point_detected: boolean;
}

export interface CounterfactualItem {
  scenario: string;
  result: string;
}

export interface EvidenceAuditTrail {
  why_evidence: string[];
  counter_evidence: string[];
  data_limitations: string[];
  counterfactuals: CounterfactualItem[];
}

export interface AtmosphericDispersion {
  wind_speed_kmh: number;
  wind_direction_cardinal: string;
  plume_heading_deg: number;
  corridor_6h_km: number;
  corridor_12h_km: number;
  corridor_24h_km: number;
  threatened_infrastructure: string[];
}

export interface ProvenanceMetadata {
  viirs_product: string;
  spatial_resolution: string;
  spectral_mwir: string;
  spectral_tir: string;
  insat_product: string;
  landcover_source: string;
  facility_registry: string;
  elevation_source: string;
}

export interface SatelliteEvidenceCard {
  event_id: string;
  lifecycle: EventLifecycle;
  decoupled_metrics: DecoupledMetrics;
  sensor_corroboration: SensorCorroboration;
  pyrometry: ThermalPyrometry;
  asset_attribution: AssetAttribution;
  regime_break: ThermalRegimeBreak;
  evidence_audit: EvidenceAuditTrail;
  dispersion_screening: AtmosphericDispersion;
  provenance: ProvenanceMetadata;
}

export interface HotspotFeature {
  type: 'Feature';
  geometry: {
    type: 'Point';
    coordinates: [number, number]; // [lon, lat]
  };
  properties: {
    id: string;
    source_id: string;
    frp: number;
    primary_class: ThermalClass;
    confidence: number;
    risk_band: RiskBand;
    risk_score: number;
    facility_name: string;
    distance_to_facility: number;
    acq_date: string;
    lifecycle_state?: LifecycleState;
    operational_priority?: RiskBand;
    asset_name?: string;
  };
}

export interface HotspotCollection {
  type: 'FeatureCollection';
  features: HotspotFeature[];
  total: number;
}

export interface ShapFactor {
  feature: string;
  impact: string;
  direction: 'positive' | 'negative';
  desc: string;
}

export interface FingerprintAnomaly {
  source_id: string;
  baseline_mean_mw: number;
  baseline_median_mw: number;
  baseline_max_mw: number;
  baseline_std_mw: number;
  current_frp_mw: number;
  deviation_percent: string;
  z_score: string;
  frp_ratio: string;
  percentile: string;
  operational_status: string;
}

export interface WildfireSpread {
  cluster_size: number;
  spatial_extent_km: number;
  spread_rate_km_day: number;
  spread_direction: string;
  fire_front_status: string;
}

export interface EventDetails {
  event_id: string;
  source_id: string;
  latitude: number;
  longitude: number;
  acquired_at: string;
  satellite: string;
  frp: number;
  bright_ti4: number;
  bright_ti5: number;
  confidence_score: number;
  classification: {
    primary_class: ThermalClass;
    confidence: number;
    calibrated_confidence?: number;
    raw_confidence?: number;
    runner_up_class: ThermalClass;
    runner_up_probability: number;
    decision_margin: number;
  };
  fingerprint_anomaly?: FingerprintAnomaly;
  facility_attribution: {
    name: string;
    type: string;
    distance_km: number;
    inside_boundary: boolean;
    operator: string;
  };
  wildfire_spread?: WildfireSpread;
  risk: {
    risk_score: number;
    risk_band: RiskBand;
  };
  shap_waterfall: ShapFactor[];
  ai_explanation: string;
  evidence_card?: SatelliteEvidenceCard;
  lifecycle?: EventLifecycle;
  decoupled_metrics?: DecoupledMetrics;
  sensor_corroboration?: SensorCorroboration;
  pyrometry?: ThermalPyrometry;
  asset_attribution?: AssetAttribution;
  regime_break?: ThermalRegimeBreak;
  evidence_audit?: EvidenceAuditTrail;
  dispersion_screening?: AtmosphericDispersion;
  provenance?: ProvenanceMetadata;
}

export interface MonthlyActivity {
  month: string;
  frp: number;
  events: number;
}

export interface SourceFingerprint {
  source_id: string;
  brand?: string;
  observation_count: number;
  active_days: number;
  historical_period?: string;
  frp_metrics?: {
    mean_mw: number;
    median_mw: number;
    max_mw: number;
    std_mw: number;
  };
  mean_frp?: number;
  max_frp?: number;
  persistence_score: number;
  stability_score: number;
  current_observation?: {
    frp_mw: number;
    deviation_percent: string;
    z_score: string;
    status: string;
  };
  recurrence_profile: string;
  monthly_activity: MonthlyActivity[];
}

export interface Facility {
  id: number;
  name: string;
  facility_type: string;
  operator: string;
  latitude: number;
  longitude: number;
  criticality: string;
}

export interface FacilityProfile {
  facility_id: number;
  name: string;
  facility_type: string;
  operator: string;
  coordinates: [number, number];
  criticality: string;
  baseline?: {
    frp_p10: number;
    frp_median: number;
    frp_p90: number;
    frp_mean: number;
    frp_max: number;
    frp_std: number;
    normal_range_mw: string;
    active_flare_stacks: number;
    monitored_sources: number;
    anomaly_status: string;
    incident_risk_index: number;
  };
  digital_twin: {
    active_hotspots_within_3km: number;
    active_flare_stacks: number;
    thermal_anomaly_status: string;
    historical_events_7yr: number;
    mean_emitted_frp_mw: number;
    peak_recorded_frp_mw: number;
    incident_risk_index: number;
  };
  annual_trend: {
    year: number;
    detections: number;
    mean_frp: number;
  }[];
}

export interface AlertItem {
  id: string;
  timestamp: string;
  level: RiskBand;
  class: ThermalClass;
  facility: string;
  message: string;
  location: [number, number];
  action_required: string;
}

export interface AnalyticsSummary {
  total_observations: number;
  total_thermal_sources: number;
  active_monitored_facilities: number;
  class_breakdown: Record<string, { count: number; percentage: number }>;
  risk_breakdown: Record<string, number>;
  state_rankings: { state: string; type: string; count: number }[];
}

export interface InvestigationResponse {
  event_id: string;
  query: string;
  classification: ThermalClass;
  confidence: number;
  primary_evidence: string[];
  operational_recommendation: string;
  system_verdict: string;
}

export interface ReviewItem {
  event_id: string;
  latitude: number;
  longitude: number;
  frp: number;
  predicted_class: ThermalClass;
  confidence: number;
  margin: number;
  facility_name: string;
  distance_to_facility: number;
  reasons: string;
  review_status: string;
  human_label?: string | null;
  reviewer?: string | null;
}

export interface LeakageAuditSplit {
  split_name: string;
  accuracy: number;
  macro_f1: number;
  ece: number;
  ood_rejection_rate: number;
  sample_count: number;
  note: string;
}

export interface LeakageAuditResponse {
  evaluation_protocol: string;
  description: string;
  results: LeakageAuditSplit[];
  summary: string;
}

export type IncidentResponseState =
  | 'UNSENT'
  | 'SENT'
  | 'DELIVERED'
  | 'ACKNOWLEDGED'
  | 'RESPONDING'
  | 'ON_SCENE'
  | 'ESCALATED'
  | 'CONTAINED'
  | 'RESOLVED';

export interface TimelineEntry {
  timestamp: string;
  stage: string;
  title: string;
  desc: string;
  status_code: string;
}

export interface ResponseIncident {
  incident_id: string;
  event_id: string;
  state: IncidentResponseState;
  created_at: string;
  facility_name: string;
  facility_type: string;
  asset_name: string;
  latitude: number;
  longitude: number;
  classification: ThermalClass;
  confidence: number;
  evidence_quality: number;
  operational_priority: RiskBand;
  frp: number;
  baseline_median_mw: number;
  z_score: number;
  subpixel_temp_k: number;
  radiant_area_m2: number;
  wind_speed_kmh: number;
  wind_direction: string;
  primary_station: string;
  primary_contact: string;
  primary_eta: string;
  backup_station: string;
  backup_eta: string;
  acknowledged_by?: string;
  readiness_score_pct: number;
  latencies: {
    detection_to_verification_sec: number;
    verification_to_dispatch_sec: number;
    dispatch_to_acknowledgement_sec: number;
    total_detection_to_response_sec: number;
  };
  timeline: TimelineEntry[];
}

export interface PreArrivalPacketData {
  incident_id: string;
  fire_service_packet: {
    packet_type: string;
    incident_id: string;
    generated_at_utc: string;
    tactical_headline: string;
    location: {
      latitude: number;
      longitude: number;
      facility: string;
      suspected_asset: string;
      address: string;
    };
    classification: {
      predicted_class: ThermalClass;
      model_confidence_pct: number;
      evidence_quality_pct: number;
      operational_priority: RiskBand;
    };
    thermal_telemetry: {
      current_frp_mw: number;
      historical_baseline_p50_mw: number;
      baseline_p90_mw: number;
      departure_sigma: string;
      estimated_hotspot_temp_k: number;
      estimated_radiant_area_m2: number;
    };
    satellite_corroboration: {
      verified_sensors: string[];
      inter_satellite_consistency: string;
      active_duration: string;
      first_detected: string;
      last_satellite_pass: string;
    };
    atmospheric_dispersion: {
      wind_vector: string;
      projected_corridor_6h: string;
      threatened_receptors: string[];
    };
    dispatch_guidance: {
      assigned_station: string;
      road_eta: string;
      recommended_foam_agent: string;
      initial_perimeter_cordon_radius_m: number;
      immediate_hazard: string;
    };
  };
  facility_owner_alert: {
    packet_type: string;
    incident_id: string;
    facility_name: string;
    affected_asset_zone: string;
    urgency: string;
    headline: string;
    summary_for_hse_manager: string;
    site_safety_actions: string[];
    dispatched_responder: {
      station: string;
      contact: string;
      eta: string;
    };
  };
  erss_cad_signal: {
    identifier: string;
    sender: string;
    sent: string;
    status: string;
    msgType: string;
    scope: string;
    category: string;
    urgency: string;
    severity: string;
    certainty: string;
    event: string;
    headline: string;
    area: {
      areaDesc: string;
      point: string;
      radius_km: number;
    };
    erss_cad_data: {
      integration_protocol: string;
      agency_type: string;
      cad_priority: number;
      assigned_station_code: string;
      assigned_station_name: string;
      call_taker_notes: string;
    };
  };
  authority_matrix: Record<string, any>;
  responders: {
    primary_responder: any;
    backup_responder: any;
    dispatch_routing: any;
  };
  readiness_score_pct: number;
}

