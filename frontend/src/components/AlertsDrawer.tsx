 import React, { useEffect, useState } from 'react';
import { X, ShieldAlert, MapPin, ArrowUpRight, Flame } from 'lucide-react';
import type { AlertItem } from '../types';
import { fetchLiveAlerts } from '../services/api';
import { classHex, CLASS_CONFIG } from '../config/classConfig';

interface AlertsDrawerProps {
  onClose: () => void;
  onLocateEvent: (coords: [number, number]) => void;
  onInvestigateEvent: (eventId: string) => void;
  theme?: 'light' | 'dark';
}

export const AlertsDrawer: React.FC<AlertsDrawerProps> = ({
  onClose,
  onLocateEvent,
  onInvestigateEvent,
}) => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLiveAlerts()
      .then((res) => setAlerts(res))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex justify-end backdrop-blur-xs">
      <div className="w-full max-w-md bg-[var(--bg-card)] border-l border-[var(--border)] h-full flex flex-col shadow-2xl ring-1 ring-black/5 animate-in slide-in-from-right duration-200">
        {/* Header */}
        <div className="p-4 border-b border-[var(--border)] flex items-center justify-between bg-[var(--bg-base)]">
          <div className="flex items-center space-x-2.5">
            <div className="w-9 h-9 rounded-sm bg-red-500/20 border border-red-500/30 flex items-center justify-center text-[var(--b-red)]">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-xs font-bold font-bold text-[var(--text-primary)]">AI-PRIORITIZED LIVE ALERTS</h3>
              <p className="text-xs font-mono text-[var(--text-secondary)]">Automated Hotspot Escalation Feed</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)]">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Alerts List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {loading ? (
            <div className="p-8 text-center text-[var(--text-secondary)] font-mono text-xs">
              <div className="w-6 h-6 border-2 border-red-500 border-t-transparent rounded-sm animate-spin mx-auto mb-2" />
              Scanning National FIRMS VIIRS Hotspots for High-Risk Escalations...
            </div>
          ) : alerts.length === 0 ? (
            <div className="p-8 text-center text-[var(--text-muted)] font-mono text-xs">
              No active critical alerts at this moment. All sources operating nominally.
            </div>
          ) : (
            alerts.map((alert) => (
              <div
                key={alert.id}
                className="bg-[var(--bg-base)] border border-[var(--border)] rounded-sm p-3.5 space-y-2.5 hover:border-[var(--border-strong)] transition-all"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-1.5">
                    <span className={`px-2 py-0.5 rounded text-xs font-mono font-bold ${
                      alert.level === 'CRITICAL' ? 'bg-red-600 text-white' : 'bg-amber-500 text-slate-950'
                    }`}>
                      {alert.level} RISK
                    </span>
                    {alert.class && (
                      <span
                        className="px-2 py-0.5 rounded text-xs font-mono font-bold border"
                        style={{
                          backgroundColor: `${classHex(alert.class)}22`,
                          color: classHex(alert.class),
                          borderColor: `${classHex(alert.class)}55`,
                        }}
                      >
                        {CLASS_CONFIG[alert.class as keyof typeof CLASS_CONFIG]?.label || alert.class}
                      </span>
                    )}
                  </div>
                  <span className="text-xs font-mono text-[var(--text-secondary)]">{alert.timestamp}</span>
                </div>

                <div>
                  <h4 className="text-xs font-bold text-[var(--text-primary)] flex items-center space-x-1.5">
                    <Flame className="w-3.5 h-3.5 text-[var(--b-amber)]" />
                    <span>{alert.facility}</span>
                  </h4>
                  <p className="text-sm text-[var(--text-primary)] mt-1 leading-snug">{alert.message}</p>
                </div>

                <div className="text-xs font-mono text-[var(--b-emerald)]/90 bg-emerald-500/10 p-2 rounded border border-emerald-500/20">
                  <strong>Protocol:</strong> {alert.action_required}
                </div>

                <div className="flex items-center space-x-2 pt-1">
                  <button
                    onClick={() => {
                      onLocateEvent(alert.location);
                      onClose();
                    }}
                    className="flex-1 flex items-center justify-center space-x-1 py-1.5 rounded-sm bg-[var(--bg-card-hover)] hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] text-xs font-mono font-semibold transition-colors"
                  >
                    <MapPin className="w-3.5 h-3.5 text-[var(--b-cyan)]" />
                    <span>Locate on Map</span>
                  </button>
                  <button
                    onClick={() => {
                      onInvestigateEvent(alert.id);
                      onClose();
                    }}
                    className="flex items-center space-x-1 px-3 py-1.5 rounded-sm bg-amber-500/20 hover:bg-amber-500/30 text-[var(--b-amber)] text-xs font-mono font-semibold border border-amber-500/30 transition-colors"
                  >
                    <span>Investigate</span>
                    <ArrowUpRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};








