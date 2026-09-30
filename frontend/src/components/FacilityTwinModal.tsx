 import React, { useEffect, useState } from 'react';
import { X, Building2, TrendingUp, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import type { FacilityProfile } from '../types';
import { fetchFacilityProfile } from '../services/api';

interface FacilityTwinModalProps {
  facilityId: number | null;
  onClose: () => void;
  theme?: 'light' | 'dark';
}

export const FacilityTwinModal: React.FC<FacilityTwinModalProps> = ({ facilityId, onClose }) => {
  const [profile, setProfile] = useState<FacilityProfile | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!facilityId) return;
    setLoading(true);
    fetchFacilityProfile(facilityId)
      .then((res) => setProfile(res))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [facilityId]);

  if (!facilityId) return null;

  return (
    <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-md w-full max-w-2xl shadow-2xl ring-1 ring-black/5 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-5 border-b border-[var(--border)] flex items-center justify-between bg-[var(--bg-base)]">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-sm bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-[var(--b-cyan)]">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-sm font-bold text-[var(--text-primary)]">{profile?.name || 'FACILITY DIGITAL TWIN'}</h3>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-sky-500/15 text-[var(--b-cyan)] border border-sky-500/30 uppercase">
                  {profile?.facility_type || 'INDUSTRIAL'}
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-red-500/15 text-[var(--b-red)] border border-red-500/30">
                  {profile?.criticality} CRITICALITY
                </span>
              </div>
              <p className="text-xs font-mono text-[var(--text-secondary)] mt-0.5">
                Operator: <strong className="text-[var(--text-primary)]">{profile?.operator}</strong> * Coordinates: {profile?.coordinates[1]}, {profile?.coordinates[0]}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)]">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        {loading || !profile ? (
          <div className="p-12 text-center text-[var(--text-secondary)] font-mono text-xs">
            <div className="w-8 h-8 border-2 border-sky-500 border-t-transparent rounded-sm animate-spin mx-auto mb-3" />
            Loading Facility Telemetry & Empirical Baseline Metrics...
          </div>
        ) : (
          <div className="p-6 space-y-4 max-h-[75vh] overflow-y-auto">
            {/* Facility Baseline Card */}
            {profile.baseline && (
              <div className="bg-sky-500/10 p-4 rounded-sm border border-sky-500/30 space-y-2.5 font-mono text-xs">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-[var(--b-cyan)]">
                    <Activity className="w-4 h-4" />
                    <span className="text-[10px] font-bold uppercase tracking-wider text-[var(--b-cyan)]">
                      Facility Historical Baseline
                    </span>
                  </div>
                  <span className={`px-2.5 py-0.5 rounded text-xs font-bold ${
                    profile.baseline.anomaly_status === 'NOMINAL'
                      ? 'bg-emerald-500/20 text-[var(--b-emerald)] border border-emerald-500/30'
                      : 'bg-amber-500/20 text-[var(--b-amber)] border border-amber-500/30'
                  }`}>
                    {profile.baseline.anomaly_status}
                  </span>
                </div>

                <div className="grid grid-cols-4 gap-2 text-center pt-1">
                  <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)] shadow-sm">
                    <span className="text-[10px] text-[var(--text-secondary)] font-bold block uppercase tracking-wider">NORMAL FRP RANGE</span>
                    <span className="text-xs font-bold text-[var(--b-amber)] mt-0.5 block">{profile.baseline.normal_range_mw}</span>
                  </div>
                  <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)] shadow-sm">
                    <span className="text-[10px] text-[var(--text-secondary)] font-bold block uppercase tracking-wider">MEDIAN BASELINE</span>
                    <span className="text-xs font-bold text-[var(--text-primary)] mt-0.5 block">{profile.baseline.frp_median} MW</span>
                  </div>
                  <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)] shadow-sm">
                    <span className="text-[10px] text-[var(--text-secondary)] font-bold block uppercase tracking-wider">FRP STD DEV (sigma)</span>
                    <span className="text-xs font-bold text-[var(--text-primary)] mt-0.5 block">+/-{profile.baseline.frp_std} MW</span>
                  </div>
                  <div className="bg-[var(--bg-card)] p-2 rounded border border-[var(--border)] shadow-sm">
                    <span className="text-[10px] text-[var(--text-secondary)] font-bold block uppercase tracking-wider">RISK INDEX</span>
                    <span className="text-xs font-bold text-[var(--b-cyan)] mt-0.5 block">{profile.baseline.incident_risk_index}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Operational State Cards */}
            <div className="grid grid-cols-3 gap-3 text-xs font-mono">
              <div className="bg-[var(--bg-base)] p-3 rounded-sm border border-[var(--border)]">
                <span className="text-[var(--text-secondary)] font-bold text-[10px] uppercase tracking-wider block">HOTSPOTS WITHIN 3KM</span>
                <div className="text-xs font-bold text-[var(--b-cyan)] mt-1">
                  {profile.digital_twin.active_hotspots_within_3km} Active
                </div>
              </div>
              <div className="bg-[var(--bg-base)] p-3 rounded-sm border border-[var(--border)]">
                <span className="text-[var(--text-secondary)] font-bold text-[10px] uppercase tracking-wider block">MONITORED SOURCES</span>
                <div className="text-xs font-bold text-[var(--b-amber)] mt-1">
                  {profile.digital_twin.active_flare_stacks} Flare Units
                </div>
              </div>
              <div className="bg-[var(--bg-base)] p-3 rounded-sm border border-[var(--border)]">
                <span className="text-[var(--text-secondary)] font-bold text-[10px] uppercase tracking-wider block">PEAK HISTORICAL FRP</span>
                <div className="text-xs font-bold text-[var(--b-red)] mt-1">
                  {profile.digital_twin.peak_recorded_frp_mw} MW
                </div>
              </div>
            </div>

            {/* 7-Year Annual Trend Chart */}
            <div className="bg-[var(--bg-base)] p-4 rounded-sm border border-[var(--border)] space-y-2">
              <div className="flex items-center justify-between text-xs font-mono text-[var(--text-primary)]">
                <span className="flex items-center space-x-1.5 font-bold">
                  <TrendingUp className="w-4 h-4 text-[var(--b-cyan)]" />
                  <span>Annual Emitted Thermal Detections (2019 - 2025)</span>
                </span>
                <span className="text-sm text-[var(--text-secondary)]">Multi-Year Timeline</span>
              </div>

              <div className="h-44 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={profile.annual_trend}>
                    <XAxis dataKey="year" stroke="#64748b" fontSize={10} tickLine={false} />
                    <YAxis stroke="#64748b" fontSize={10} tickLine={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#090d16', borderColor: '#334155', fontSize: '11px', fontFamily: 'monospace' }}
                      itemStyle={{ color: '#38bdf8' }}
                    />
                    <Bar dataKey="detections" fill="#0284c7" radius={[4, 4, 0, 0]} name="Thermal Detections" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};









