 import React, { useEffect, useState } from 'react';
import { X, Fingerprint, BarChart2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import type { SourceFingerprint } from '../types';
import { fetchSourceFingerprint } from '../services/api';

interface FingerprintModalProps {
  sourceId: string | null;
  onClose: () => void;
  theme?: 'light' | 'dark';
}

export const FingerprintModal: React.FC<FingerprintModalProps> = ({ sourceId, onClose }) => {
  const [data, setData] = useState<SourceFingerprint | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!sourceId) return;
    setLoading(true);
    fetchSourceFingerprint(sourceId)
      .then((res) => setData(res))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [sourceId]);

  if (!sourceId) return null;

  return (
    <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-md w-full max-w-2xl shadow-2xl ring-1 ring-black/5 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-5 border-b border-[var(--border)] flex items-center justify-between bg-[var(--bg-base)]">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-sm bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-[var(--b-cyan)]">
              <Fingerprint className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-sm font-bold font-bold text-[var(--text-primary)]">THERMAL DIGITAL FINGERPRINT</h3>
                <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-cyan-500/20 text-[var(--b-cyan)] border border-cyan-500/30">
                  {data?.recurrence_profile || 'ANALYZING'}
                </span>
              </div>
              <p className="text-xs font-mono text-[var(--text-secondary)]">Source ID: {sourceId}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)]">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        {loading || !data ? (
          <div className="p-12 text-center text-[var(--text-secondary)] font-mono text-xs">
            <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-sm animate-spin mx-auto mb-3" />
            Compiling Multi-Year Source Behavior & FRP Baselines...
          </div>
        ) : (
          <div className="p-6 space-y-5">
            {/* Metric Cards */}
            <div className="grid grid-cols-4 gap-3 text-xs font-mono">
              <div className="bg-[var(--bg-base)] p-3 rounded-sm border border-[var(--border)]">
                <span className="text-[var(--text-secondary)] text-sm">TOTAL DETECTIONS</span>
                <div className="text-sm font-bold font-bold text-[var(--text-primary)] mt-0.5">{data.observation_count}</div>
              </div>
              <div className="bg-[var(--bg-base)] p-3 rounded-sm border border-[var(--border)]">
                <span className="text-[var(--text-secondary)] text-sm">ACTIVE DAYS</span>
                <div className="text-sm font-bold font-bold text-[var(--b-cyan)] mt-0.5">{data.active_days}</div>
              </div>
              <div className="bg-[var(--bg-base)] p-3 rounded-sm border border-[var(--border)]">
                <span className="text-[var(--text-secondary)] text-sm">MEAN BASELINE FRP</span>
                <div className="text-sm font-bold font-bold text-[var(--b-amber)] mt-0.5">{data.mean_frp} MW</div>
              </div>
              <div className="bg-[var(--bg-base)] p-3 rounded-sm border border-[var(--border)]">
                <span className="text-[var(--text-secondary)] text-sm">PEAK RECORDED FRP</span>
                <div className="text-sm font-bold font-bold text-[var(--b-red)] mt-0.5">{data.max_frp} MW</div>
              </div>
            </div>

            {/* Behavioral Scores */}
            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="bg-[var(--bg-base)] p-3 rounded-sm border border-[var(--border)] space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-[var(--text-secondary)]">Persistence Score:</span>
                  <span className="text-[var(--b-cyan)] font-bold">{Math.round(data.persistence_score * 100)}%</span>
                </div>
                <div className="w-full h-2 bg-[var(--bg-card)] rounded-sm overflow-hidden">
                  <div className="h-full bg-cyan-400 rounded-sm" style={{ width: `${data.persistence_score * 100}%` }} />
                </div>
              </div>
              <div className="bg-[var(--bg-base)] p-3 rounded-sm border border-[var(--border)] space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-[var(--text-secondary)]">FRP Stability Index:</span>
                  <span className="text-[var(--b-emerald)] font-bold">{Math.round(data.stability_score * 100)}%</span>
                </div>
                <div className="w-full h-2 bg-[var(--bg-card)] rounded-sm overflow-hidden">
                  <div className="h-full bg-emerald-400 rounded-sm" style={{ width: `${data.stability_score * 100}%` }} />
                </div>
              </div>
            </div>

            {/* Recharts Seasonality Curve */}
            <div className="bg-[var(--bg-base)] p-4 rounded-sm border border-[var(--border)] space-y-2">
              <div className="flex items-center justify-between text-xs font-mono text-[var(--text-primary)]">
                <span className="flex items-center space-x-1.5 font-bold">
                  <BarChart2 className="w-4 h-4 text-[var(--b-amber)]" />
                  <span>12-Month Historical Activity & FRP Intensity Profile</span>
                </span>
                <span className="text-sm text-[var(--text-secondary)]">Seasonal Pattern</span>
              </div>

              <div className="h-44 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.monthly_activity}>
                    <XAxis dataKey="month" stroke="#64748b" fontSize={10} tickLine={false} />
                    <YAxis stroke="#64748b" fontSize={10} tickLine={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#090d16', borderColor: '#334155', fontSize: '11px', fontFamily: 'monospace' }}
                      itemStyle={{ color: '#fbbf24' }}
                    />
                    <Bar dataKey="frp" fill="#f59e0b" radius={[4, 4, 0, 0]} name="Mean FRP (MW)" />
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








