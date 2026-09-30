import React, { useState } from 'react';
import {
  X,
  Flame,
  Building2,
  Cpu,
  Fingerprint,
  ExternalLink,
  Bot,
  TrendingUp,
  Wind,
  ArrowUpRight,
  ArrowDownRight,
  Satellite,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  Clock,
  ChevronDown,
  ChevronRight,
  Radio,
  Sparkles,
  Siren
} from 'lucide-react';
import type { EventDetails, LifecycleState } from '../types';
import { CLASS_CONFIG } from '../config/classConfig';

interface EventInspectorProps {
  details: EventDetails | null;
  loading: boolean;
  onClose: () => void;
  onOpenFingerprint: (sourceId: string) => void;
  onOpenFacility: (facilityName: string) => void;
  onInvestigate: (eventId: string) => void;
  onOpenResponseCenter?: (eventId: string) => void;
  theme?: 'light' | 'dark';
}

const CLASS_BADGES = Object.fromEntries(
  Object.entries(CLASS_CONFIG).map(([k, v]) => [k, v.badge])
) as Record<string, { bg: string; text: string; border: string }>;

const RISK_BADGES: Record<string, { bg: string; text: string; border: string }> = {
  CRITICAL: { bg: 'bg-red-600', text: 'text-white', border: 'border-red-500' },
  HIGH: { bg: 'bg-amber-500', text: 'text-slate-950 font-bold', border: 'border-amber-400' },
  MEDIUM: { bg: 'bg-blue-600', text: 'text-white', border: 'border-blue-500' },
  LOW: { bg: 'bg-slate-700', text: 'text-[var(--text-primary)]', border: 'border-slate-600' },
};

const LIFECYCLE_BADGES: Record<LifecycleState, { bg: string; text: string; dot: string }> = {
  ESCALATING: { bg: 'bg-red-500/20 border-red-500/50', text: 'text-[var(--b-red)]', dot: 'bg-red-400 animate-ping' },
  MONITORING: { bg: 'bg-cyan-500/20 border-cyan-500/50', text: 'text-[var(--b-cyan)]', dot: 'bg-cyan-400' },
  CLASSIFIED: { bg: 'bg-emerald-500/20 border-emerald-500/50', text: 'text-[var(--b-emerald)]', dot: 'bg-emerald-400' },
  CORROBORATING: { bg: 'bg-amber-500/20 border-amber-500/50', text: 'text-[var(--b-amber)]', dot: 'bg-amber-400 animate-pulse' },
  DETECTED: { bg: 'bg-purple-500/20 border-purple-500/50', text: 'text-[var(--b-purple)]', dot: 'bg-purple-400' },
  CONTAINED: { bg: 'bg-indigo-500/20 border-indigo-500/50', text: 'text-[var(--b-indigo)]', dot: 'bg-indigo-400' },
  RESOLVED: { bg: 'bg-slate-700/40 border-slate-600', text: 'text-[var(--text-primary)]', dot: 'bg-slate-400' },
  ARCHIVED: { bg: 'bg-[var(--bg-card-hover)] border-[var(--border-strong)]', text: 'text-[var(--text-secondary)]', dot: 'bg-slate-500' },
};

export const EventInspector: React.FC<EventInspectorProps> = ({
  details,
  loading,
  onClose,
  onOpenFingerprint,
  onOpenFacility,
  onInvestigate,
  onOpenResponseCenter,
}) => {
  // Collapsible Accordion States
  const [openSections, setOpenSections] = useState<{
    sensors: boolean;
    pyrometry: boolean;
    regime: boolean;
    why: boolean;
    counter: boolean;
    limitations: boolean;
    counterfactuals: boolean;
    dispersion: boolean;
  }>({
    sensors: true,
    pyrometry: true,
    regime: true,
    why: true,
    counter: false,
    limitations: true,
    counterfactuals: false,
    dispersion: false,
  });

  const toggleSection = (key: keyof typeof openSections) => {
    setOpenSections((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  if (!details && !loading) return null;

  const card = details?.evidence_card;
  const metrics = card?.decoupled_metrics || details?.decoupled_metrics;
  const lifecycle = card?.lifecycle || details?.lifecycle;
  const corroboration = card?.sensor_corroboration || details?.sensor_corroboration;
  const pyrometry = card?.pyrometry || details?.pyrometry;
  const asset = card?.asset_attribution || details?.asset_attribution;
  const regime = card?.regime_break || details?.regime_break;
  const audit = card?.evidence_audit || details?.evidence_audit;
  const dispersion = card?.dispersion_screening || details?.dispersion_screening;
  const provenance = card?.provenance || details?.provenance;

  const lifecycleState: LifecycleState = lifecycle?.state || (details?.risk.risk_band === 'CRITICAL' ? 'ESCALATING' : 'MONITORING');
  const lifecycleConfig = LIFECYCLE_BADGES[lifecycleState] || LIFECYCLE_BADGES.MONITORING;

  return (
    <div className="absolute top-16 right-0 bottom-12 w-full sm:w-[500px] bg-[var(--bg-card)] border-l border-[var(--border)] shadow-2xl ring-1 ring-black/5 z-20 flex flex-col backdrop-blur-2xl transition-all duration-300">
      {/* Evidence Card Top Header */}
      <div className="p-3.5 border-b border-[var(--border)] bg-[var(--bg-base)] flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-sm bg-amber-500/20 border border-amber-500/30 flex items-center justify-center">
            <Satellite className="w-4 h-4 text-[var(--b-amber)]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono font-bold text-xs text-[var(--text-primary)] tracking-wider">
                {details ? `#${details.event_id}` : 'Loading...'}
              </span>
              {/* Lifecycle State Badge */}
              <div className={`flex items-center space-x-1.5 px-2 py-0.5 rounded border text-[10px] font-mono font-bold ${lifecycleConfig.bg} ${lifecycleConfig.text}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${lifecycleConfig.dot}`} />
                <span>{lifecycleState}</span>
              </div>
              {/* Priority Band */}
              {details && (
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${RISK_BADGES[details.risk.risk_band]?.bg} ${RISK_BADGES[details.risk.risk_band]?.text}`}>
                  {details.risk.risk_band}
                </span>
              )}
            </div>
            <div className="text-xs font-mono text-[var(--text-secondary)] mt-0.5 flex items-center space-x-2">
              <span className="flex items-center space-x-1">
                <Clock className="w-3 h-3 text-[var(--text-muted)]" />
                <span>{lifecycle?.duration_formatted ? `Active ${lifecycle.duration_formatted}` : details?.acquired_at}</span>
              </span>
              <span>*</span>
              <span className="text-[var(--text-primary)] font-semibold">{asset?.asset_name || details?.facility_attribution.name}</span>
            </div>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)] transition-colors"
          title="Close Evidence Inspector"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-2">
            <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-sm animate-spin mx-auto" />
            <p className="text-xs font-mono text-[var(--text-secondary)]">Assembling Multi-Sensor Satellite Evidence Card...</p>
          </div>
        </div>
      ) : details ? (
        <div className="flex-1 overflow-y-auto p-4 space-y-3.5 text-xs font-mono">
          
          {/* Classification & Conformal Prediction Banner */}
          <div className={`p-4 rounded-sm border ${CLASS_BADGES[details.classification.primary_class]?.border} ${CLASS_BADGES[details.classification.primary_class]?.bg} relative overflow-hidden shadow-lg`}>
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-[var(--text-secondary)] flex items-center space-x-1.5">
                  <ShieldAlert className="w-3.5 h-3.5 text-[var(--b-amber)]" />
                  <span>Validated Classification</span>
                </span>
                <h3 className={`text-base font-black tracking-wide mt-0.5 ${CLASS_BADGES[details.classification.primary_class]?.text}`}>
                  {details.classification.primary_class}
                </h3>
                {metrics?.conformal_prediction_set && (
                  <div className="mt-1 text-[11px] text-[var(--text-primary)] flex items-center space-x-1.5">
                    <span className="text-[var(--text-secondary)]">Prediction Set:</span>
                    <span className="px-1.5 py-0.2 rounded bg-black/40 border border-[var(--border-strong)] font-bold text-[var(--b-cyan)]">
                      {`{ ${metrics.conformal_prediction_set.join(', ')} }`}
                    </span>
                    <span className="text-[10px] text-[var(--text-secondary)]">({metrics.conformal_coverage})</span>
                  </div>
                )}
              </div>
              <div className="text-right">
                <span className="text-[10px] font-mono uppercase tracking-wider text-[var(--text-secondary)]">
                  Calibrated Confidence
                </span>
                <div className="text-xl font-black text-[var(--text-primary)]">
                  {details.classification.calibrated_confidence || details.classification.confidence}%
                </div>
                {metrics && (
                  <span className={`inline-block mt-0.5 text-[10px] font-bold px-1.5 py-0.2 rounded ${
                    metrics.ood_status === 'IN_DISTRIBUTION'
                      ? 'bg-emerald-500/20 text-[var(--b-emerald)] border border-emerald-500/30'
                      : 'bg-amber-500/20 text-[var(--b-amber)] border border-amber-500/30'
                  }`}>
                    {metrics.ood_status} (d_m: {metrics.mahalanobis_distance})
                  </span>
                )}
              </div>
            </div>

            {/* Decision Margin vs Runner Up */}
            <div className="mt-3 pt-2.5 border-t border-[var(--border)] flex items-center justify-between text-sm">
              <span className="text-[var(--text-secondary)]">
                Runner-up: <strong className="text-[var(--text-primary)]">{details.classification.runner_up_class}</strong> ({details.classification.runner_up_probability}%)
              </span>
              <span className="text-slate-600">|</span>
              <span className="text-[var(--text-secondary)]">
                Decision Margin: <strong className="text-[var(--b-cyan)]">+{details.classification.decision_margin}%</strong>
              </span>
              <span className="text-slate-600">|</span>
              <span className="text-[var(--text-secondary)]">
                Raw XGBoost: <strong className="text-[var(--text-primary)]">{details.classification.raw_confidence || details.classification.confidence}%</strong>
              </span>
            </div>
          </div>

          {/* Decoupled 3-Tier Operational Metrics Bar */}
          {metrics && (
            <div className="bg-[var(--bg-base)] p-3 rounded-sm border border-[var(--border)] grid grid-cols-3 gap-2 text-center">
              <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)]">
                <span className="text-[10px] text-[var(--text-secondary)] uppercase tracking-wider block">1. AI CONFIDENCE</span>
                <span className="text-xs font-bold font-black text-[var(--text-primary)]">{metrics.classification_confidence_pct}%</span>
                <span className="text-xs text-[var(--text-muted)] block">Model diagnosis</span>
              </div>
              <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)]">
                <span className="text-[10px] text-[var(--text-secondary)] uppercase tracking-wider block">2. EVIDENCE QUALITY</span>
                <span className="text-xs font-bold font-black text-[var(--b-cyan)]">{metrics.evidence_quality_pct}%</span>
                <span className="text-xs text-[var(--text-muted)] block">Sensor fidelity</span>
              </div>
              <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)]">
                <span className="text-[10px] text-[var(--text-secondary)] uppercase tracking-wider block">3. OPERATIONAL PRIORITY</span>
                <span className={`text-xs font-bold font-black ${metrics.operational_priority_band === 'CRITICAL' ? 'text-[var(--b-red)]' : 'text-[var(--b-amber)]'}`}>
                  {metrics.operational_priority_band} ({metrics.operational_priority_score})
                </span>
                <span className="text-xs text-[var(--text-muted)] block">Action urgency</span>
              </div>
            </div>
          )}

          {/* Thermal Regime Break & Asset Baseline Card */}
          {regime && (
            <div className="bg-[var(--bg-base)] rounded-sm border border-[var(--border)] overflow-hidden">
              <button
                onClick={() => toggleSection('regime')}
                className="w-full p-3 flex items-center justify-between text-left hover:bg-[var(--bg-card-hover)] transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <TrendingUp className="w-4 h-4 text-[var(--b-amber)]" />
                  <span className="text-[9px] font-bold text-[var(--text-primary)] uppercase tracking-wider">
                    Thermal Regime Break & Baseline
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-0.5 rounded text-sm font-bold ${
                    regime.regime_status === 'REGIME_BREAK'
                      ? 'bg-red-500/20 text-[var(--b-red)] border border-red-500/40'
                      : regime.regime_status === 'ELEVATED_ANOMALY'
                      ? 'bg-amber-500/20 text-[var(--b-amber)] border border-amber-500/40'
                      : 'bg-emerald-500/20 text-[var(--b-emerald)] border border-emerald-500/30'
                  }`}>
                    {regime.regime_status}
                  </span>
                  {openSections.regime ? <ChevronDown className="w-4 h-4 text-[var(--text-secondary)]" /> : <ChevronRight className="w-4 h-4 text-[var(--text-secondary)]" />}
                </div>
              </button>

              {openSections.regime && (
                <div className="p-3 pt-0 space-y-2 border-t border-[var(--border)]">
                  <div className="grid grid-cols-4 gap-2 text-center pt-2">
                    <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)]">
                      <span className="text-sm text-[var(--text-secondary)] block">HIST P50</span>
                      <span className="text-xs font-bold text-[var(--text-primary)]">{regime.baseline_median_mw} MW</span>
                    </div>
                    <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)]">
                      <span className="text-sm text-[var(--text-secondary)] block">HIST P90</span>
                      <span className="text-xs font-bold text-[var(--text-primary)]">{regime.baseline_p90_mw} MW</span>
                    </div>
                    <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)]">
                      <span className="text-sm text-[var(--text-secondary)] block">HIST P99</span>
                      <span className="text-xs font-bold text-[var(--b-purple)]">{regime.baseline_p99_mw} MW</span>
                    </div>
                    <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)]">
                      <span className="text-sm text-[var(--text-secondary)] block">CURRENT FRP</span>
                      <span className="text-xs font-bold text-[var(--b-amber)]">{regime.current_frp_mw} MW</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-sm p-2 bg-[var(--bg-card)] rounded border border-[var(--border)]">
                    <span className="text-[var(--text-secondary)]">
                      Statistical Departure: <strong className={regime.z_score_sigma > 2.5 ? 'text-[var(--b-red)]' : 'text-[var(--b-amber)]'}>{regime.z_score_sigma > 0 ? `+${regime.z_score_sigma}` : regime.z_score_sigma}sigma</strong> ({regime.departure_pct > 0 ? `+${regime.departure_pct}` : regime.departure_pct}%)
                    </span>
                    <span className="text-[var(--text-secondary)]">
                      Change-point: <strong className={regime.change_point_detected ? 'text-[var(--b-red)]' : 'text-[var(--b-emerald)]'}>{regime.change_point_detected ? 'DETECTED' : 'NOMINAL'}</strong>
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Multi-Sensor Corroboration Matrix */}
          {corroboration && (
            <div className="bg-[var(--bg-base)] rounded-sm border border-[var(--border)] overflow-hidden">
              <button
                onClick={() => toggleSection('sensors')}
                className="w-full p-3 flex items-center justify-between text-left hover:bg-[var(--bg-card-hover)] transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <Radio className="w-4 h-4 text-[var(--b-cyan)]" />
                  <span className="text-[9px] font-bold text-[var(--text-primary)] uppercase tracking-wider">
                    Multi-Sensor Corroboration ({corroboration.corroboration_score_pct}%)
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-[var(--b-cyan)] font-bold bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30">
                    {corroboration.sensors.filter(s => s.status === 'CONFIRMED' || s.status === 'COMPATIBLE_SAR').length}/{corroboration.sensors.length} ACTIVE
                  </span>
                  {openSections.sensors ? <ChevronDown className="w-4 h-4 text-[var(--text-secondary)]" /> : <ChevronRight className="w-4 h-4 text-[var(--text-secondary)]" />}
                </div>
              </button>

              {openSections.sensors && (
                <div className="p-3 pt-0 space-y-1.5 border-t border-[var(--border)]">
                  <p className="text-sm text-[var(--text-secondary)] italic pt-1 pb-1">
                    {corroboration.summary}
                  </p>
                  <div className="space-y-1.5">
                    {corroboration.sensors.map((s, idx) => (
                      <div key={idx} className="p-2 rounded bg-[var(--bg-card)] border border-[var(--border)] flex items-center justify-between text-sm">
                        <div className="space-y-0.5">
                          <div className="flex items-center space-x-1.5">
                            <span className="font-bold text-[var(--text-primary)]">{s.sensor_name}</span>
                            <span className="text-sm text-[var(--text-muted)]">({s.resolution})</span>
                            <span className="text-sm text-[var(--text-secondary)]">* {s.channel_info}</span>
                          </div>
                          <div className="text-[var(--text-secondary)] text-sm">{s.telemetry_snippet}</div>
                        </div>
                        <div className="text-right shrink-0 pl-2">
                          <span className={`px-1.5 py-0.5 rounded text-sm font-bold ${
                            s.status === 'CONFIRMED'
                              ? 'bg-emerald-500/20 text-[var(--b-emerald)] border border-emerald-500/30'
                              : s.status === 'COMPATIBLE_SAR'
                              ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
                              : s.status === 'DETECTED'
                              ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                              : s.status === 'OBSCURED_CLOUD'
                              ? 'bg-amber-500/20 text-[var(--b-amber)] border border-amber-500/30'
                              : 'bg-[var(--bg-card-hover)] text-[var(--text-secondary)] border border-[var(--border-strong)]'
                          }`}>
                            {s.status}
                          </span>
                          <span className="block text-xs text-[var(--text-muted)] mt-0.5">{s.timestamp_utc}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Nightfire-Inspired Pyrometry & Sub-pixel Physics */}
          {pyrometry && (
            <div className="bg-[var(--bg-base)] rounded-sm border border-[var(--border)] overflow-hidden">
              <button
                onClick={() => toggleSection('pyrometry')}
                className="w-full p-3 flex items-center justify-between text-left hover:bg-[var(--bg-card-hover)] transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <Flame className="w-4 h-4 text-orange-400" />
                  <span className="text-[9px] font-bold text-[var(--text-primary)] uppercase tracking-wider">
                    Pyrometry & Sub-Pixel Physics
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-[var(--b-orange)] font-bold bg-orange-500/10 px-2 py-0.5 rounded border border-orange-500/30">
                    PLANCK FIT
                  </span>
                  {openSections.pyrometry ? <ChevronDown className="w-4 h-4 text-[var(--text-secondary)]" /> : <ChevronRight className="w-4 h-4 text-[var(--text-secondary)]" />}
                </div>
              </button>

              {openSections.pyrometry && (
                <div className="p-3 pt-0 space-y-2 border-t border-[var(--border)]">
                  <p className="text-sm text-[var(--text-secondary)] italic pt-1">
                    Dual-temperature Planck fitting across VIIRS I4 (~3.7   m) and I5 (~11   m) bands.
                  </p>
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)]">
                      <span className="text-sm text-[var(--text-secondary)] block">EST. TEMPERATURE</span>
                      <span className="text-xs font-bold text-orange-400">{pyrometry.subpixel_temp_k} K</span>
                      <span className="text-xs text-[var(--text-muted)] block">Hotspot emitter</span>
                    </div>
                    <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)]">
                      <span className="text-sm text-[var(--text-secondary)] block">RADIANT AREA</span>
                      <span className="text-xs font-bold text-[var(--b-cyan)]">~{pyrometry.radiant_area_m2} m2</span>
                      <span className="text-xs text-[var(--text-muted)] block">Sub-pixel source</span>
                    </div>
                    <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)]">
                      <span className="text-sm text-[var(--text-secondary)] block">RADIANT FLUX</span>
                      <span className="text-xs font-bold text-[var(--b-amber)]">{pyrometry.radiant_heat_flux_kw_m2} kW/m22</span>
                      <span className="text-xs text-[var(--text-muted)] block">Radiant power</span>
                    </div>
                  </div>
                  <div className="text-sm text-[var(--text-secondary)] flex items-center justify-between p-1.5 bg-[var(--bg-card)] rounded border border-[var(--border)]">
                    <span>Uncertainty Ellipse: <strong>{pyrometry.uncertainty_semi_major_m} m x {pyrometry.uncertainty_semi_minor_m} m</strong></span>
                    <span>Footprint: <strong>375 m nominal at nadir</strong></span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Evidence-Based Attribution: "Why?" & Counter-Evidence */}
          {audit && (
            <div className="bg-[var(--bg-base)] rounded-sm border border-[var(--border)] overflow-hidden space-y-0">
              {/* "Why This Diagnosis?" */}
              <div className="border-b border-[var(--border)]">
                <button
                  onClick={() => toggleSection('why')}
                  className="w-full p-3 flex items-center justify-between text-left hover:bg-[var(--bg-card-hover)] transition-colors"
                >
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-[var(--b-emerald)]" />
                    <span className="text-[9px] font-bold text-[var(--text-primary)] uppercase tracking-wider">
                      Why {details.classification.primary_class}? (Primary Evidence)
                    </span>
                  </div>
                  {openSections.why ? <ChevronDown className="w-4 h-4 text-[var(--text-secondary)]" /> : <ChevronRight className="w-4 h-4 text-[var(--text-secondary)]" />}
                </button>
                {openSections.why && (
                  <div className="p-3 pt-0 space-y-1.5">
                    {audit.why_evidence.map((item, idx) => (
                      <div key={idx} className="flex items-start space-x-2 text-sm text-[var(--text-primary)]">
                        <span className="text-[var(--b-emerald)] font-bold shrink-0">[+]</span>
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Counter-Evidence & Uncertainties */}
              <div className="border-b border-[var(--border)]">
                <button
                  onClick={() => toggleSection('counter')}
                  className="w-full p-3 flex items-center justify-between text-left hover:bg-[var(--bg-card-hover)] transition-colors"
                >
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className="w-4 h-4 text-[var(--b-amber)]" />
                    <span className="text-[9px] font-bold text-[var(--text-primary)] uppercase tracking-wider">
                      Counter-Evidence & Uncertainties
                    </span>
                  </div>
                  {openSections.counter ? <ChevronDown className="w-4 h-4 text-[var(--text-secondary)]" /> : <ChevronRight className="w-4 h-4 text-[var(--text-secondary)]" />}
                </button>
                {openSections.counter && (
                  <div className="p-3 pt-0 space-y-1.5">
                    {audit.counter_evidence.map((item, idx) => (
                      <div key={idx} className="flex items-start space-x-2 text-sm text-[var(--text-secondary)]">
                        <span className="text-[var(--b-amber)] font-bold shrink-0">[-]</span>
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Failure Awareness: What We Don't Know */}
              <div className="border-b border-[var(--border)]">
                <button
                  onClick={() => toggleSection('limitations')}
                  className="w-full p-3 flex items-center justify-between text-left hover:bg-[var(--bg-card-hover)] transition-colors"
                >
                  <div className="flex items-center space-x-2">
                    <HelpCircle className="w-4 h-4 text-[var(--b-cyan)]" />
                    <span className="text-[9px] font-bold text-sky-200 uppercase tracking-wider">
                      Data Limitations & Failure Awareness
                    </span>
                  </div>
                  {openSections.limitations ? <ChevronDown className="w-4 h-4 text-[var(--text-secondary)]" /> : <ChevronRight className="w-4 h-4 text-[var(--text-secondary)]" />}
                </button>
                {openSections.limitations && (
                  <div className="p-3 pt-0 space-y-1.5 bg-[var(--bg-card)] p-2.5 rounded m-2.5 border border-sky-500/20">
                    {audit.data_limitations.map((item, idx) => (
                      <div key={idx} className="flex items-start space-x-2 text-sm text-[var(--text-primary)]">
                        <span className="text-[var(--b-cyan)] font-bold shrink-0">   </span>
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Counterfactual "What-If" Reasoning */}
              <div>
                <button
                  onClick={() => toggleSection('counterfactuals')}
                  className="w-full p-3 flex items-center justify-between text-left hover:bg-[var(--bg-card-hover)] transition-colors"
                >
                  <div className="flex items-center space-x-2">
                    <Sparkles className="w-4 h-4 text-purple-400" />
                    <span className="text-[9px] font-bold text-purple-200 uppercase tracking-wider">
                      Counterfactual What-If Reasoning
                    </span>
                  </div>
                  {openSections.counterfactuals ? <ChevronDown className="w-4 h-4 text-[var(--text-secondary)]" /> : <ChevronRight className="w-4 h-4 text-[var(--text-secondary)]" />}
                </button>
                {openSections.counterfactuals && (
                  <div className="p-3 pt-0 space-y-2">
                    {audit.counterfactuals.map((cf, idx) => (
                      <div key={idx} className="p-2 rounded bg-[var(--bg-card)] border border-purple-900/40 text-sm space-y-1">
                        <div className="text-[var(--b-purple)] font-semibold">{cf.scenario}</div>
                        <div className="text-[var(--text-secondary)] text-sm pl-3 border-l border-purple-500/30"> -  {cf.result}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Atmospheric Dispersion Screening (HYSPLIT-inspired) */}
          {dispersion && (
            <div className="bg-[var(--bg-base)] rounded-sm border border-[var(--border)] overflow-hidden">
              <button
                onClick={() => toggleSection('dispersion')}
                className="w-full p-3 flex items-center justify-between text-left hover:bg-[var(--bg-card-hover)] transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <Wind className="w-4 h-4 text-teal-400" />
                  <span className="text-[9px] font-bold text-[var(--text-primary)] uppercase tracking-wider">
                    Atmospheric Dispersion Screening
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-teal-300 font-bold bg-teal-500/10 px-2 py-0.5 rounded border border-teal-500/30">
                    {dispersion.wind_speed_kmh} km/h {dispersion.wind_direction_cardinal}
                  </span>
                  {openSections.dispersion ? <ChevronDown className="w-4 h-4 text-[var(--text-secondary)]" /> : <ChevronRight className="w-4 h-4 text-[var(--text-secondary)]" />}
                </div>
              </button>

              {openSections.dispersion && (
                <div className="p-3 pt-0 space-y-2 border-t border-[var(--border)]">
                  <div className="grid grid-cols-3 gap-2 text-center pt-2">
                    <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)]">
                      <span className="text-sm text-[var(--text-secondary)] block">6-HR CORRIDOR</span>
                      <span className="text-xs font-bold text-teal-300">{dispersion.corridor_6h_km} km</span>
                    </div>
                    <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)]">
                      <span className="text-sm text-[var(--text-secondary)] block">12-HR CORRIDOR</span>
                      <span className="text-xs font-bold text-[var(--b-amber)]">{dispersion.corridor_12h_km} km</span>
                    </div>
                    <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)]">
                      <span className="text-sm text-[var(--text-secondary)] block">24-HR CORRIDOR</span>
                      <span className="text-xs font-bold text-[var(--b-red)]">{dispersion.corridor_24h_km} km</span>
                    </div>
                  </div>
                  <div className="space-y-1 pt-1">
                    <span className="text-[10px] text-[var(--text-secondary)] uppercase tracking-wider">Vulnerable Downwind Receptors:</span>
                    {dispersion.threatened_infrastructure.map((inf, idx) => (
                      <div key={idx} className="text-sm text-[var(--text-primary)] flex items-center space-x-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
                        <span>{inf}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Supporting SHAP Attribution Waterfall */}
          <div className="bg-[var(--bg-base)] p-3.5 rounded-sm border border-[var(--border)] space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Cpu className="w-4 h-4 text-purple-400" />
                <span className="text-xs font-bold text-[var(--text-primary)]">SHAP Waterfall Attribution</span>
              </div>
              <span className="text-xs font-mono text-purple-400">86 FEATURES</span>
            </div>

            <div className="space-y-1.5 pt-1 font-mono text-sm">
              {details.shap_waterfall.map((factor, idx) => (
                <div key={idx} className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)] flex items-center justify-between">
                  <div className="space-y-0.5 flex-1 pr-2">
                    <div className="flex items-center space-x-1.5">
                      {factor.direction === 'positive' ? (
                        <ArrowUpRight className="w-3 h-3 text-[var(--b-emerald)]" />
                      ) : (
                        <ArrowDownRight className="w-3 h-3 text-[var(--b-red)]" />
                      )}
                      <span className="text-[var(--text-primary)] font-semibold">{factor.feature}</span>
                    </div>
                    <div className="text-sm text-[var(--text-muted)] pl-4">{factor.desc}</div>
                  </div>
                  <span className={`font-bold px-1.5 py-0.5 rounded text-sm shrink-0 ${
                    factor.direction === 'positive'
                      ? 'bg-emerald-500/20 text-[var(--b-emerald)] border border-emerald-500/30'
                      : 'bg-red-500/20 text-[var(--b-red)] border border-red-500/30'
                  }`}>
                    {factor.impact}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Auditable Data Provenance */}
          {provenance && (
            <div className="bg-[var(--bg-base)] p-3 rounded-sm border border-[var(--border)] space-y-1.5 text-xs font-mono text-[var(--text-secondary)]">
              <span className="font-bold text-[var(--text-primary)] uppercase tracking-wider block">Auditable Data Provenance</span>
              <div className="grid grid-cols-2 gap-1.5 pt-1">
                <div>Sensor: <span className="text-[var(--text-primary)] font-semibold">{provenance.viirs_product}</span></div>
                <div>Cadence: <span className="text-[var(--text-primary)] font-semibold">{provenance.insat_product}</span></div>
                <div>Spatial Res: <span className="text-[var(--text-primary)] font-semibold">{provenance.spatial_resolution}</span></div>
                <div>Spectral: <span className="text-[var(--text-primary)] font-semibold">{provenance.spectral_mwir}</span></div>
                <div>Land Cover: <span className="text-[var(--text-primary)] font-semibold">{provenance.landcover_source}</span></div>
                <div>Registry: <span className="text-[var(--text-primary)] font-semibold">{provenance.facility_registry}</span></div>
              </div>
            </div>
          )}

          {/* Quick Action Navigation */}
          <div className="space-y-2 pt-1 pb-4">
            {/* Emergency Decision-Support & Alert Orchestration */}
            <button
              onClick={() => onOpenResponseCenter && onOpenResponseCenter(details.event_id)}
              className="w-full flex items-center justify-between px-3.5 py-2.5 rounded-sm bg-gradient-to-r from-red-950/80 via-red-900/60 to-rose-950/80 hover:from-red-900 hover:to-rose-900 border border-red-600/50 text-xs font-mono text-red-200 transition-all group shadow-md"
            >
              <span className="flex items-center space-x-2">
                <Siren className="w-4 h-4 text-[var(--b-red)] group-hover:animate-pulse" />
                <span className="font-bold text-[var(--text-primary)]">EMERGENCY RESPONSE WORKFLOW</span>
              </span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-black bg-red-600 text-white tracking-widest">
                ERSS-112
              </span>
            </button>

            <button
              onClick={() => onOpenFingerprint(details.source_id)}
              className="w-full flex items-center justify-between px-3.5 py-2.5 rounded-sm bg-[var(--bg-base)] hover:bg-[var(--bg-card-hover)] border border-[var(--border-strong)] text-xs font-mono text-[var(--b-cyan)] transition-all group"
            >
              <span className="flex items-center space-x-2">
                <Fingerprint className="w-4 h-4 text-[var(--b-cyan)]" />
                <span>THERMAL DIGITAL FINGERPRINT   </span>
              </span>
              <ExternalLink className="w-3.5 h-3.5 text-[var(--text-muted)] group-hover:text-[var(--b-cyan)]" />
            </button>

            <button
              onClick={() => onOpenFacility(details.facility_attribution.name)}
              className="w-full flex items-center justify-between px-3.5 py-2.5 rounded-sm bg-[var(--bg-base)] hover:bg-[var(--bg-card-hover)] border border-[var(--border-strong)] text-xs font-mono text-sky-300 transition-all group"
            >
              <span className="flex items-center space-x-2">
                <Building2 className="w-4 h-4 text-[var(--b-cyan)]" />
                <span>FACILITY DIGITAL TWIN PROFILE</span>
              </span>
              <ExternalLink className="w-3.5 h-3.5 text-[var(--text-muted)] group-hover:text-sky-300" />
            </button>

            <button
              onClick={() => onInvestigate(details.event_id)}
              className="w-full flex items-center justify-center space-x-2 px-3.5 py-2.5 rounded-sm bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs font-mono transition-all shadow-lg shadow-amber-500/20"
            >
              <Bot className="w-4 h-4" />
              <span>LAUNCH AI INVESTIGATION ASSISTANT</span>
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
};









