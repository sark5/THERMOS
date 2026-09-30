 import React, { useState, useEffect } from 'react';
import {
  X,
  Radio,
  Navigation,
  FileText,
  AlertTriangle,
  RotateCcw,
  Check
} from 'lucide-react';
import type { ResponseIncident, PreArrivalPacketData } from '../types';
import {
  fetchResponseIncidents,
  fetchPreArrivalPacket,
  acknowledgeResponseAlert,
  markUnitResponding,
  escalateResponseIncident,
  resolveResponseIncident,
  fetchPostIncidentReport
} from '../services/api';

interface ResponseCenterModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedIncidentId?: string | null;
  theme?: 'light' | 'dark';
}

export const ResponseCenterModal: React.FC<ResponseCenterModalProps> = ({
  isOpen,
  onClose,
  selectedIncidentId,
}) => {
  const [incidents, setIncidents] = useState<ResponseIncident[]>([]);
  const [activeIncidentId, setActiveIncidentId] = useState<string>('IND-2026-00417');
  const [packetData, setPacketData] = useState<PreArrivalPacketData | null>(null);
  const [postReport, setPostReport] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<'fire_packet' | 'facility_alert' | 'erss_signal' | 'post_report'>('fire_packet');
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  // Load incidents list
  const loadIncidents = async () => {
    try {
      setLoading(true);
      const res = await fetchResponseIncidents();
      setIncidents(res.incidents);
      let targetId = 'IND-2026-00417';
      if (selectedIncidentId) {
        const found = res.incidents.find(
          (i) => i.incident_id === selectedIncidentId || (i as any).event_id === selectedIncidentId
        );
        if (found) {
          targetId = found.incident_id;
        } else if (selectedIncidentId.startsWith('IND-')) {
          targetId = selectedIncidentId;
        } else if (res.incidents.length > 0) {
          targetId = res.incidents[0].incident_id;
        }
      } else if (res.incidents.length > 0) {
        targetId = res.incidents[0].incident_id;
      }
      setActiveIncidentId(targetId);
    } catch (err) {
      console.error('Failed to load response incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  // Load selected incident pre-arrival packet
  const loadPacket = async (incId: string) => {
    try {
      const data = await fetchPreArrivalPacket(incId);
      setPacketData(data);
      const rep = await fetchPostIncidentReport(incId);
      setPostReport(rep);
    } catch (err) {
      console.error(`Failed to load packet for ${incId}:`, err);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadIncidents();
    }
  }, [isOpen, selectedIncidentId]);

  useEffect(() => {
    if (activeIncidentId) {
      loadPacket(activeIncidentId);
    }
  }, [activeIncidentId]);

  // Response simulation handlers
  const handleAcknowledge = async () => {
    try {
      await acknowledgeResponseAlert(activeIncidentId, 'Station Officer R. K. Patel (Jamnagar Fire Control)');
      setActionFeedback('    Alert acknowledged. Detection-to-response latency clock logged.');
      await loadIncidents();
      await loadPacket(activeIncidentId);
      setTimeout(() => setActionFeedback(null), 4000);
    } catch (err) {
      console.error('Acknowledge failed:', err);
    }
  };

  const handleRespond = async () => {
    try {
      await markUnitResponding(activeIncidentId, 'Foam Tender-01 & Heavy Pumper-02');
      setActionFeedback('    Unit mobilized. Transponder tracking linked to ERSS-112 CAD.');
      await loadIncidents();
      await loadPacket(activeIncidentId);
      setTimeout(() => setActionFeedback(null), 4000);
    } catch (err) {
      console.error('Respond failed:', err);
    }
  };

  const handleEscalate = async () => {
    try {
      await escalateResponseIncident(activeIncidentId);
      setActionFeedback('    Escalation triggered: Backup responder and District EOC notified.');
      await loadIncidents();
      await loadPacket(activeIncidentId);
      setTimeout(() => setActionFeedback(null), 4000);
    } catch (err) {
      console.error('Escalation failed:', err);
    }
  };

  const handleResolve = async () => {
    try {
      await resolveResponseIncident(activeIncidentId, 'Hydrocarbon containment established. Surface temperature normalized.');
      setActionFeedback('    Incident marked RESOLVED. Post-incident evidence dossier sealed.');
      await loadIncidents();
      await loadPacket(activeIncidentId);
      setActiveTab('post_report');
      setTimeout(() => setActionFeedback(null), 4000);
    } catch (err) {
      console.error('Resolve failed:', err);
    }
  };

  if (!isOpen) return null;

  const currentIncident = incidents.find((i) => i.incident_id === activeIncidentId) || incidents[0];

  const stateColors: Record<string, { bg: string; text: string; border: string }> = {
    RESPONDING: { bg: 'bg-amber-500/20', text: 'text-[var(--b-amber)]', border: 'border-amber-500/40' },
    ACKNOWLEDGED: { bg: 'bg-cyan-500/20', text: 'text-[var(--b-cyan)]', border: 'border-cyan-500/40' },
    ESCALATED: { bg: 'bg-red-500/20', text: 'text-red-300', border: 'border-red-500/40' },
    SENT: { bg: 'bg-purple-500/20', text: 'text-[var(--b-purple)]', border: 'border-purple-500/40' },
    RESOLVED: { bg: 'bg-emerald-500/20', text: 'text-[var(--b-emerald)]', border: 'border-emerald-500/40' },
  };

  const curStateStyle = currentIncident ? stateColors[currentIncident.state] || stateColors.RESPONDING : stateColors.RESPONDING;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-xl flex items-center justify-center p-3 sm:p-6 animate-in fade-in duration-200">
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-md w-full max-w-6xl max-h-[92vh] flex flex-col shadow-2xl ring-1 ring-black/5 overflow-hidden font-mono">
        
        {/* Top Header */}
        <div className="p-4 border-b border-[var(--border)] bg-[var(--bg-base)] flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-sm bg-red-500/20 border border-red-500/40 flex items-center justify-center">
              <Radio className="w-5 h-5 text-[var(--b-red)] animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-[10px] font-bold font-black text-[var(--text-primary)] tracking-wider">
                  THERMOS CLOSED-LOOP EMERGENCY RESPONSE (C2R)
                </h2>
                <span className="px-2 py-0.5 rounded text-sm font-bold bg-sky-500/20 text-sky-300 border border-sky-500/30">
                  ERSS-112 CAD GATEWAY
                </span>
              </div>
              <p className="text-sm text-[var(--text-secondary)]">
                Automated Decision-Support, Pre-Arrival Intelligence & Closed-Loop Alert Orchestration
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Incident Switcher */}
            <div className="flex items-center space-x-1.5 bg-[var(--bg-card)] px-2 py-1 rounded-sm border border-[var(--border)] text-xs">
              <span className="text-[10px] text-[var(--text-muted)] uppercase">Incident:</span>
              <select
                value={activeIncidentId}
                onChange={(e) => setActiveIncidentId(e.target.value)}
                className="bg-transparent text-[var(--b-amber)] font-bold focus:outline-none cursor-pointer"
              >
                {incidents.map((inc) => (
                  <option key={inc.incident_id} value={inc.incident_id} className="bg-[var(--bg-base)] text-[var(--text-primary)]">
                    {inc.incident_id} * {inc.facility_name} ({inc.state})
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={onClose}
              className="p-1.5 rounded-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)] transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Action Feedback Banner */}
        {actionFeedback && (
          <div className="bg-emerald-950/80 border-b border-emerald-500/40 px-4 py-2 text-xs text-[var(--b-emerald)] flex items-center justify-between animate-in slide-in-from-top duration-200">
            <span>{actionFeedback}</span>
            <button onClick={() => setActionFeedback(null)} className="text-[var(--b-emerald)] hover:text-[var(--text-primary)] text-xs">Dismiss</button>
          </div>
        )}

        {/* Main Content Body */}
        {loading || !currentIncident ? (
          <div className="flex-1 flex items-center justify-center p-12">
            <div className="text-center space-y-2">
              <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-sm animate-spin mx-auto" />
              <p className="text-xs text-[var(--text-secondary)]">Loading Response Orchestrator & ERSS Gateway...</p>
            </div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto grid grid-cols-1 lg:grid-cols-12 gap-4 p-4 text-xs">
            
            {/* Left 7 Columns: Incident Dossier & Differentiated Packets */}
            <div className="lg:col-span-7 space-y-3.5">
              
              {/* Active Incident Summary Header */}
              <div className="bg-[var(--bg-base)] p-4 rounded-sm border border-[var(--border)] space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold font-black text-[var(--text-primary)]">#{currentIncident.incident_id}</span>
                      <span className={`px-2 py-0.5 rounded text-sm font-bold border ${curStateStyle.bg} ${curStateStyle.text} ${curStateStyle.border}`}>
                        {currentIncident.state}
                      </span>
                      <span className="px-2 py-0.5 rounded text-sm font-bold bg-red-600 text-white">
                        {currentIncident.operational_priority} PRIORITY
                      </span>
                    </div>
                    <div className="text-xs font-bold font-bold text-[var(--text-primary)] mt-1">
                      {currentIncident.facility_name}  -  <span className="text-[var(--b-amber)]">{currentIncident.asset_name}</span>
                    </div>
                    <div className="text-sm text-[var(--text-secondary)] mt-0.5">
                      Coordinates: {currentIncident.latitude}, {currentIncident.longitude} * First Detected: {currentIncident.created_at.slice(11, 19)} UTC
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="text-[10px] text-[var(--text-secondary)] block uppercase">Response Readiness</span>
                    <span className="text-sm font-bold font-black text-[var(--b-emerald)]">{currentIncident.readiness_score_pct}%</span>
                    <span className="text-sm text-[var(--text-muted)] block">CAD Signal Ready</span>
                  </div>
                </div>

                {/* Latency Pipeline KPIs */}
                <div className="grid grid-cols-4 gap-2 pt-2 border-t border-[var(--border)] text-center">
                  <div className="bg-[var(--bg-card)] p-1.5 rounded border border-[var(--border)]">
                    <span className="text-xs text-[var(--text-secondary)] block uppercase">1. DETECT TO VERIFY</span>
                    <span className="text-xs font-bold text-[var(--text-primary)]">{currentIncident.latencies.detection_to_verification_sec}s</span>
                  </div>
                  <div className="bg-[var(--bg-card)] p-1.5 rounded border border-[var(--border)]">
                    <span className="text-xs text-[var(--text-secondary)] block uppercase">2. VERIFY TO DISPATCH</span>
                    <span className="text-xs font-bold text-[var(--text-primary)]">{currentIncident.latencies.verification_to_dispatch_sec}s</span>
                  </div>
                  <div className="bg-[var(--bg-card)] p-1.5 rounded border border-[var(--border)]">
                    <span className="text-xs text-[var(--text-secondary)] block uppercase">3. DISPATCH TO ACK</span>
                    <span className="text-xs font-bold text-[var(--b-cyan)]">{currentIncident.latencies.dispatch_to_acknowledgement_sec}s</span>
                  </div>
                  <div className="bg-[var(--bg-card)] p-1.5 rounded border border-[var(--border)]">
                    <span className="text-xs text-[var(--text-secondary)] block uppercase">TOTAL LATENCY</span>
                    <span className="text-xs font-bold text-[var(--b-amber)]">{currentIncident.latencies.total_detection_to_response_sec}s</span>
                  </div>
                </div>
              </div>

              {/* View Mode Navigation Tabs */}
              <div className="flex border-b border-[var(--border)] text-xs font-bold">
                <button
                  onClick={() => setActiveTab('fire_packet')}
                  className={`px-3.5 py-2 border-b-2 flex items-center space-x-1.5 transition-colors ${
                    activeTab === 'fire_packet' ? 'border-red-500 text-red-300 bg-red-500/10' : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>Fire Service Packet</span>
                </button>

                <button
                  onClick={() => setActiveTab('facility_alert')}
                  className={`px-3.5 py-2 border-b-2 flex items-center space-x-1.5 transition-colors ${
                    activeTab === 'facility_alert' ? 'border-amber-500 text-[var(--b-amber)] bg-amber-500/10' : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Facility Owner Alert</span>
                </button>

                <button
                  onClick={() => setActiveTab('erss_signal')}
                  className={`px-3.5 py-2 border-b-2 flex items-center space-x-1.5 transition-colors ${
                    activeTab === 'erss_signal' ? 'border-cyan-500 text-[var(--b-cyan)] bg-cyan-500/10' : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  <Radio className="w-3.5 h-3.5" />
                  <span>ERSS-112 CAD Signal</span>
                </button>

                <button
                  onClick={() => setActiveTab('post_report')}
                  className={`px-3.5 py-2 border-b-2 flex items-center space-x-1.5 transition-colors ${
                    activeTab === 'post_report' ? 'border-emerald-500 text-[var(--b-emerald)] bg-emerald-500/10' : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  <Check className="w-3.5 h-3.5" />
                  <span>Post-Incident Report</span>
                </button>
              </div>

              {/* TAB 1: Fire Service Tactical Pre-Arrival Packet */}
              {activeTab === 'fire_packet' && packetData && (
                <div className="bg-[var(--bg-base)] p-4 rounded-sm border border-[var(--border)] space-y-3.5">
                  <div className="flex items-center justify-between pb-2 border-b border-[var(--border)]">
                    <span className="text-[10px] text-[var(--text-secondary)] font-bold uppercase">
                      PRE-ARRIVAL TACTICAL PACKET * {packetData.fire_service_packet.incident_id}
                    </span>
                    <span className="text-sm text-[var(--b-cyan)]">
                      ETA: {packetData.fire_service_packet.dispatch_guidance.road_eta}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div className="bg-[var(--bg-card)] p-2.5 rounded border border-[var(--border)] space-y-1">
                      <span className="text-[10px] text-[var(--text-secondary)] uppercase block">THERMAL SEVERITY & REGIME</span>
                      <div className="text-xs font-bold font-bold text-[var(--b-amber)]">{packetData.fire_service_packet.thermal_telemetry.current_frp_mw} MW</div>
                      <div className="text-sm text-[var(--text-primary)]">
                        Departure: <strong className="text-[var(--b-red)]">{packetData.fire_service_packet.thermal_telemetry.departure_sigma}</strong> vs baseline ({packetData.fire_service_packet.thermal_telemetry.historical_baseline_p50_mw} MW)
                      </div>
                      <div className="text-sm text-[var(--text-secondary)]">
                        Hotspot Temp: ~{packetData.fire_service_packet.thermal_telemetry.estimated_hotspot_temp_k} K * Area: ~{packetData.fire_service_packet.thermal_telemetry.estimated_radiant_area_m2} m2
                      </div>
                    </div>

                    <div className="bg-[var(--bg-card)] p-2.5 rounded border border-[var(--border)] space-y-1">
                      <span className="text-[10px] text-[var(--text-secondary)] uppercase block">ATMOSPHERIC PLUME CORRIDOR</span>
                      <div className="text-xs font-bold font-bold text-teal-300">{packetData.fire_service_packet.atmospheric_dispersion.wind_vector}</div>
                      <div className="text-sm text-[var(--text-primary)]">
                        6h Exposure Corridor: <strong>{packetData.fire_service_packet.atmospheric_dispersion.projected_corridor_6h}</strong>
                      </div>
                      <div className="text-sm text-[var(--text-secondary)]">
                        {packetData.fire_service_packet.atmospheric_dispersion.threatened_receptors[0]}
                      </div>
                    </div>
                  </div>

                  <div className="bg-[var(--bg-card)] p-3 rounded border border-[var(--border)] space-y-1.5">
                    <span className="text-[10px] text-[var(--text-secondary)] uppercase block">TACTICAL DISPATCH GUIDANCE</span>
                    <div className="text-sm text-[var(--text-primary)]">
                      * Recommended Extinguishing Agent: <strong className="text-[var(--b-amber)]">{packetData.fire_service_packet.dispatch_guidance.recommended_foam_agent}</strong>
                    </div>
                    <div className="text-sm text-[var(--text-primary)]">
                      * Initial Cordon Radius: <strong className="text-[var(--b-cyan)]">{packetData.fire_service_packet.dispatch_guidance.initial_perimeter_cordon_radius_m} meters</strong>
                    </div>
                    <div className="text-sm text-red-300 bg-red-950/30 p-1.5 rounded border border-red-900/40">
                          Hazard: {packetData.fire_service_packet.dispatch_guidance.immediate_hazard}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: Facility Owner Thermal Alert */}
              {activeTab === 'facility_alert' && packetData && (
                <div className="bg-[var(--bg-base)] p-4 rounded-sm border border-[var(--border)] space-y-3">
                  <div className="p-3 bg-amber-950/20 border border-amber-500/40 rounded-sm space-y-1.5">
                    <div className="flex items-center space-x-2 text-[var(--b-amber)] font-bold text-xs">
                      <AlertTriangle className="w-4 h-4 text-[var(--b-amber)]" />
                      <span>{packetData.facility_owner_alert.headline}</span>
                    </div>
                    <p className="text-sm text-[var(--text-primary)] leading-relaxed">
                      {packetData.facility_owner_alert.summary_for_hse_manager}
                    </p>
                  </div>

                  <div className="space-y-1.5">
                    <span className="text-[10px] text-[var(--text-secondary)] uppercase font-bold">Mandated Site Emergency Actions:</span>
                    {packetData.facility_owner_alert.site_safety_actions.map((act: string, idx: number) => (
                      <div key={idx} className="p-2 rounded bg-[var(--bg-card)] border border-[var(--border)] text-sm text-[var(--text-primary)] flex items-start space-x-2">
                        <span className="text-[var(--b-amber)] font-bold shrink-0">[{idx + 1}]</span>
                        <span>{act}</span>
                      </div>
                    ))}
                  </div>

                  <div className="p-2.5 bg-[var(--bg-card)] rounded border border-[var(--border)] text-sm text-[var(--text-secondary)] flex items-center justify-between">
                    <span>Dispatched Unit: <strong className="text-[var(--text-primary)]">{packetData.facility_owner_alert.dispatched_responder.station}</strong></span>
                    <span>Direct Desk: <strong className="text-[var(--b-cyan)]">{packetData.facility_owner_alert.dispatched_responder.contact}</strong></span>
                  </div>
                </div>
              )}

              {/* TAB 3: ERSS-112 CAD Signal */}
              {activeTab === 'erss_signal' && packetData && (
                <div className="bg-[var(--bg-base)] p-4 rounded-sm border border-[var(--border)] space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-[var(--text-secondary)] font-bold uppercase">
                      MACHINE-READABLE ERSS-112 CAD INTEGRATION SIGNAL (OASIS CAP-IN v1.0)
                    </span>
                    <span className="text-sm text-[var(--b-emerald)] font-bold">PROTOCOL VALIDATED</span>
                  </div>
                  <pre className="bg-[var(--bg-card)] p-3 rounded-sm border border-[var(--border)] text-sm text-[var(--b-emerald)] overflow-x-auto max-h-[300px]">
                    {JSON.stringify(packetData.erss_cad_signal, null, 2)}
                  </pre>
                </div>
              )}

              {/* TAB 4: Post-Incident Report */}
              {activeTab === 'post_report' && postReport && (
                <div className="bg-[var(--bg-base)] p-4 rounded-sm border border-[var(--border)] space-y-3">
                  <div className="flex items-center justify-between pb-2 border-b border-[var(--border)]">
                    <span className="text-xs font-bold text-[var(--text-primary)]">
                      POST-INCIDENT EVIDENCE DOSSIER * {postReport.report_id}
                    </span>
                    <span className="text-sm text-[var(--text-secondary)]">Generated: {postReport.generated_at_utc}</span>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)]">
                      <span className="text-sm text-[var(--text-secondary)] block">FINAL STATUS</span>
                      <span className="text-xs font-bold text-[var(--b-emerald)]">{postReport.executive_summary.final_state}</span>
                    </div>
                    <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)]">
                      <span className="text-sm text-[var(--text-secondary)] block">PEAK EMISSION</span>
                      <span className="text-xs font-bold text-[var(--b-amber)]">{postReport.executive_summary.peak_frp_mw} MW</span>
                    </div>
                    <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)]">
                      <span className="text-sm text-[var(--text-secondary)] block">TOTAL RESPONSE TIME</span>
                      <span className="text-xs font-bold text-[var(--b-cyan)]">{postReport.executive_summary.total_response_latency}</span>
                    </div>
                  </div>

                  <div className="space-y-1.5 pt-2">
                    <span className="text-[10px] text-[var(--text-secondary)] uppercase font-bold">Incident Log Audit Trail:</span>
                    <div className="space-y-1">
                      {postReport.timeline_audit_trail.map((entry: any, idx: number) => (
                        <div key={idx} className="p-2 rounded bg-[var(--bg-card)] border border-[var(--border)] text-sm flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <span className="text-[var(--text-muted)] font-bold">{entry.timestamp}</span>
                            <span className="text-[var(--text-primary)] font-semibold">{entry.title}</span>
                          </div>
                          <span className="text-[var(--text-secondary)] text-sm">{entry.status_code}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Right 5 Columns: Responder Routing & Closed-Loop Controls */}
            <div className="lg:col-span-5 space-y-3.5">
              
              {/* Closed-Loop Simulation Controls */}
              <div className="bg-[var(--bg-base)] p-3.5 rounded-sm border border-[var(--border)] space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-[9px] font-bold text-[var(--text-primary)] uppercase tracking-wider">
                    Closed-Loop Dispatch Controls
                  </span>
                  <span className="text-sm text-[var(--text-secondary)]">OPERATIONAL SIMULATOR</span>
                </div>

                <div className="space-y-2">
                  <button
                    onClick={handleAcknowledge}
                    className="w-full flex items-center justify-center space-x-2 px-3 py-2 rounded-sm bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs transition-colors shadow-md shadow-cyan-600/20"
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>Acknowledge Alert (Duty Officer)</span>
                  </button>

                  <button
                    onClick={handleRespond}
                    className="w-full flex items-center justify-center space-x-2 px-3 py-2 rounded-sm bg-amber-600 hover:bg-amber-500 text-slate-950 font-bold text-xs transition-colors shadow-md shadow-amber-600/20"
                  >
                    <Navigation className="w-3.5 h-3.5" />
                    <span>Mobilize Response Unit (En Route)</span>
                  </button>

                  <button
                    onClick={handleEscalate}
                    className="w-full flex items-center justify-center space-x-2 px-3 py-2 rounded-sm bg-red-600 hover:bg-red-500 text-white font-bold text-xs transition-colors shadow-md shadow-red-600/20"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Trigger Escalation Test (Station Timeout)</span>
                  </button>

                  <button
                    onClick={handleResolve}
                    className="w-full flex items-center justify-center space-x-2 px-3 py-2 rounded-sm bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition-colors shadow-md shadow-emerald-600/20"
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>Resolve Incident & Seal Audit Dossier</span>
                  </button>
                </div>
              </div>

              {/* Nearest Responders & Route Distance */}
              {packetData?.responders && (
                <div className="bg-[var(--bg-base)] p-3.5 rounded-sm border border-[var(--border)] space-y-2.5">
                  <span className="text-[9px] font-bold text-[var(--text-primary)] uppercase tracking-wider block">
                    Nearest Emergency Responders
                  </span>

                  {/* Primary Station */}
                  <div className="p-2.5 rounded-sm bg-[var(--bg-card)] border border-amber-500/40 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-[var(--b-amber)] uppercase">PRIMARY RESPONDER</span>
                      <span className="text-sm font-bold text-[var(--b-emerald)]">
                        ETA: {packetData.responders.primary_responder.eta_formatted}
                      </span>
                    </div>
                    <div className="text-xs font-bold text-[var(--text-primary)]">
                      {packetData.responders.primary_responder.name}
                    </div>
                    <div className="text-sm text-[var(--text-secondary)]">
                      Agency: {packetData.responders.primary_responder.agency} * Line: {packetData.responders.primary_responder.contact}
                    </div>
                  </div>

                  {/* Backup Station */}
                  <div className="p-2.5 rounded-sm bg-[var(--bg-card)] border border-[var(--border)] space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-[var(--text-secondary)] uppercase">BACKUP MUTUAL AID</span>
                      <span className="text-sm font-bold text-[var(--text-primary)]">
                        ETA: {packetData.responders.backup_responder.eta_formatted}
                      </span>
                    </div>
                    <div className="text-xs font-bold text-[var(--text-primary)]">
                      {packetData.responders.backup_responder.name}
                    </div>
                    <div className="text-sm text-[var(--text-muted)]">
                      Contact: {packetData.responders.backup_responder.contact}
                    </div>
                  </div>
                </div>
              )}

              {/* Live Incident Escalation Timeline */}
              <div className="bg-[var(--bg-base)] p-3.5 rounded-sm border border-[var(--border)] space-y-2">
                <span className="text-[9px] font-bold text-[var(--text-primary)] uppercase tracking-wider block">
                  Incident Response Timeline
                </span>
                <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
                  {currentIncident.timeline.map((item, idx) => (
                    <div key={idx} className="flex items-start space-x-2 text-sm">
                      <span className="text-[var(--text-muted)] font-bold shrink-0 pt-0.5">{item.timestamp}</span>
                      <div className="border-l-2 border-[var(--border-strong)] pl-2 space-y-0.5">
                        <div className="text-[var(--text-primary)] font-semibold">{item.title}</div>
                        <div className="text-[var(--text-secondary)] text-sm leading-tight">{item.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>

          </div>
        )}

      </div>
    </div>
  );
};









