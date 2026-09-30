 import React, { useEffect, useState } from 'react';
import { X, BarChart3 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { AnalyticsSummary } from '../types';
import { fetchAnalyticsSummary } from '../services/api';

interface AnalyticsModalProps {
  onClose: () => void;
  theme?: 'light' | 'dark';
}

import { classHex } from '../config/classConfig';


export const AnalyticsModal: React.FC<AnalyticsModalProps> = ({ onClose }) => {
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalyticsSummary()
      .then((res) => setData(res))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const chartData = data
    ? Object.entries(data.class_breakdown).map(([cls, info]) => ({
        name: cls.replace(/_/g, ' '),
        rawKey: cls,
        count: info.count,
        percentage: info.percentage,
      }))
    : [];

  return (
    <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-md w-full max-w-3xl shadow-2xl ring-1 ring-black/5 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-5 border-b border-[var(--border)] flex items-center justify-between bg-[var(--bg-base)]">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-sm bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <BarChart3 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-[var(--text-primary)]">SUBCONTINENTAL THERMAL ANALYTICS</h3>
              <p className="text-xs font-mono text-[var(--text-secondary)]">
                NASA FIRMS 2018 - 2026 VIIRS Master Ingestion (7,922,480 Observations)
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)]">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        {loading || !data ? (
          <div className="p-12 text-center text-[var(--text-secondary)] font-mono text-xs">
            <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-sm animate-spin mx-auto mb-3" />
            Aggregating 7.9M Records & State-Level Distributions...
          </div>
        ) : (
          <div className="p-6 space-y-5 max-h-[75vh] overflow-y-auto">
            {/* Top Cards */}
            <div className="grid grid-cols-3 gap-3 text-xs font-mono">
              <div className="bg-[var(--bg-base)] p-3.5 rounded-sm border border-[var(--border)]">
                <span className="text-[var(--text-secondary)] text-sm">TOTAL VIIRS DETECTIONS</span>
                <div className="text-sm font-bold font-bold text-[var(--text-primary)] mt-0.5">
                  {data.total_observations.toLocaleString()}
                </div>
              </div>
              <div className="bg-[var(--bg-base)] p-3.5 rounded-sm border border-[var(--border)]">
                <span className="text-[var(--text-secondary)] text-sm">PERSISTENT THERMAL SOURCES</span>
                <div className="text-sm font-bold font-bold text-[var(--b-cyan)] mt-0.5">
                  {data.total_thermal_sources.toLocaleString()}
                </div>
              </div>
              <div className="bg-[var(--bg-base)] p-3.5 rounded-sm border border-[var(--border)]">
                <span className="text-[var(--text-secondary)] text-sm">INDUSTRIAL SITES MONITORED</span>
                <div className="text-sm font-bold font-bold text-[var(--b-emerald)] mt-0.5">
                  {data.active_monitored_facilities} Facilities
                </div>
              </div>
            </div>

            {/* 6-Class Distribution Chart */}
            <div className="bg-[var(--bg-base)] p-4 rounded-sm border border-[var(--border)] space-y-2">
              <div className="flex items-center justify-between text-xs font-mono text-[var(--text-primary)]">
                <span className="font-bold">6-Class Subcontinental Breakdown</span>
                <span className="text-sm text-[var(--text-secondary)]">Total 100.0%</span>
              </div>
              <div className="h-44 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <XAxis dataKey="name" stroke="#64748b" fontSize={10} tickLine={false} />
                    <YAxis stroke="#64748b" fontSize={10} tickLine={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#090d16', borderColor: '#334155', fontSize: '11px', fontFamily: 'monospace' }}
                      formatter={(val: any) => [`${Number(val).toLocaleString()} events`, 'Count']}
                    />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={classHex(entry.rawKey)} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* State Rankings Table */}
            <div className="bg-[var(--bg-base)] p-4 rounded-sm border border-[var(--border)] space-y-2">
              <span className="text-xs font-mono font-bold text-[var(--text-primary)] block">
                Regional Hotspot Concentration Ranking
              </span>
              <div className="space-y-1.5 font-mono text-xs">
                {data.state_rankings.map((st, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between bg-[var(--bg-card)] px-3 py-2 rounded-sm border border-[var(--border)]"
                  >
                    <div className="flex items-center space-x-2">
                      <span className="w-5 text-[var(--text-muted)] font-bold">{i + 1}.</span>
                      <span className="text-[var(--text-primary)] font-semibold">{st.state}</span>
                      <span className="text-sm text-[var(--text-secondary)]">({st.type})</span>
                    </div>
                    <span className="text-[var(--b-amber)] font-bold">{st.count.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};








