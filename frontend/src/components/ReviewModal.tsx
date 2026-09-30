 import React, { useEffect, useState } from 'react';
import {
  X,
  UserCheck,
  CheckCircle,
  HelpCircle,
  Sparkles
} from 'lucide-react';
import type { ReviewItem, ThermalClass } from '../types';
import { fetchReviewQueue, submitReview } from '../services/api';
import { classHex } from '../config/classConfig';

interface ReviewModalProps {
  onClose: () => void;
  theme?: 'light' | 'dark';
}

const ALL_CLASSES: ThermalClass[] = [
  'INDUSTRIAL_FLARE',
  'INDUSTRIAL_FIRE',
  'MINING',
  'AGRICULTURAL',
  'WILDFIRE',
  'UNCLASSIFIED',
];

export const ReviewModal: React.FC<ReviewModalProps> = ({ onClose }) => {
  const [queue, setQueue] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<ReviewItem | null>(null);
  const [correctedClass, setCorrectedClass] = useState<ThermalClass>('INDUSTRIAL_FLARE');
  const [reviewerNotes, setReviewerNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const loadQueue = () => {
    setLoading(true);
    fetchReviewQueue('PENDING')
      .then((res) => {
        setQueue(res.items || []);
        if (res.items && res.items.length > 0) {
          setSelectedItem(res.items[0]);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadQueue();
  }, []);

  const handleAction = async (action: 'CONFIRM' | 'CORRECT' | 'UNCERTAIN' | 'REJECT') => {
    if (!selectedItem) return;
    setSubmitting(true);
    try {
      await submitReview({
        event_id: selectedItem.event_id,
        action: action,
        assigned_label: action === 'CORRECT' ? correctedClass : undefined,
        reviewer: 'Senior Earth Observation Analyst',
        notes: reviewerNotes || undefined,
      });

      setSuccessMsg(`Decision logged: ${action} for #${selectedItem.event_id}`);
      setTimeout(() => setSuccessMsg(null), 3000);

      // Remove item from queue and select next
      const nextQueue = queue.filter((item) => item.event_id !== selectedItem.event_id);
      setQueue(nextQueue);
      setSelectedItem(nextQueue.length > 0 ? nextQueue[0] : null);
      setReviewerNotes('');
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-md w-full max-w-4xl shadow-2xl ring-1 ring-black/5 overflow-hidden flex flex-col max-h-[85vh] animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-4 border-b border-[var(--border)] flex items-center justify-between bg-[var(--bg-base)]">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-sm bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-[var(--b-amber)]">
              <UserCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-sm font-bold text-[var(--text-primary)]">HUMAN-IN-THE-LOOP AUDIT QUEUE</h3>
                <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-amber-500/20 text-[var(--b-amber)] border border-amber-500/30">
                  {queue.length} PENDING AUDITS
                </span>
              </div>
              <p className="text-xs font-mono text-[var(--text-secondary)]">
                Supervised gold-standard verification for ambiguous and low-margin boundary detections
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)]">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body Split: List on left, inspection on right */}
        {loading ? (
          <div className="p-16 text-center text-[var(--text-secondary)] font-mono text-xs">
            <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-sm animate-spin mx-auto mb-3" />
            Loading Human Review Queue...
          </div>
        ) : queue.length === 0 ? (
          <div className="p-16 text-center text-[var(--text-secondary)] font-mono text-xs space-y-2">
            <CheckCircle className="w-10 h-10 text-[var(--b-emerald)] mx-auto" />
            <h4 className="text-xs font-bold font-bold text-[var(--text-primary)]">All Candidate Hotspots Verified!</h4>
            <p className="text-[var(--text-muted)]">Zero pending edge-case classifications in the queue.</p>
          </div>
        ) : (
          <div className="flex-1 flex overflow-hidden">
            {/* Left: Queue List */}
            <div className="w-1/3 border-r border-[var(--border)] overflow-y-auto p-3 space-y-2 bg-[var(--bg-card)] font-mono text-xs">
              {queue.map((item) => {
                const isSelected = selectedItem?.event_id === item.event_id;
                const col = classHex(item.predicted_class);
                return (
                  <button
                    key={item.event_id}
                    onClick={() => setSelectedItem(item)}
                    className={`w-full text-left p-3 rounded-sm border transition-all ${
                      isSelected
                        ? 'bg-[var(--bg-base)] border-amber-500/60 shadow-lg shadow-amber-500/10'
                        : 'bg-[var(--bg-card)] border-[var(--border)] hover:border-[var(--border-strong)]'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[var(--text-primary)]">#{item.event_id.slice(-8)}</span>
                      <span
                        className="px-1.5 py-0.5 rounded text-sm font-bold border"
                        style={{ backgroundColor: `${col}18`, color: col, borderColor: `${col}40` }}
                      >
                        {item.predicted_class}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm text-[var(--text-secondary)] mt-1">
                      <span>FRP: <strong className="text-[var(--b-amber)]">{item.frp} MW</strong></span>
                      <span>Margin: <strong className="text-[var(--b-cyan)]">+{Math.round(item.margin * 100)}%</strong></span>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Right: Selected Item Audit Workspace */}
            {selectedItem && (
              <div className="flex-1 p-5 overflow-y-auto space-y-4 font-mono text-xs">
                {successMsg && (
                  <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-sm text-[var(--b-emerald)] text-xs flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4" />
                    <span>{successMsg}</span>
                  </div>
                )}

                {/* Candidate Prediction Banner */}
                <div className="p-4 rounded-sm bg-[var(--bg-base)] border border-[var(--border)] space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-[10px] text-[var(--text-secondary)] uppercase">AI Model Candidate Verdict</span>
                      <h4
                        className="text-sm font-bold font-black tracking-wide"
                        style={{ color: classHex(selectedItem.predicted_class) }}
                      >
                        {selectedItem.predicted_class}
                      </h4>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-[var(--text-secondary)] uppercase">Confidence / Margin</span>
                      <div className="text-sm font-bold font-bold text-[var(--text-primary)]">
                        {Math.round(selectedItem.confidence * 100)}% <span className="text-xs text-[var(--text-secondary)] font-normal">(+{Math.round(selectedItem.margin * 100)}% margin)</span>
                      </div>
                    </div>
                  </div>

                  <div className="text-sm text-[var(--text-primary)] pt-2 border-t border-[var(--border)] flex items-center space-x-2">
                    <Sparkles className="w-3.5 h-3.5 text-[var(--b-amber)] shrink-0" />
                    <span>Trigger Reason: <strong className="text-[var(--b-amber)]">{selectedItem.reasons}</strong></span>
                  </div>
                </div>

                {/* Telemetry & Proximity Grid */}
                <div className="grid grid-cols-3 gap-2">
                  <div className="bg-[var(--bg-base)] p-3 rounded-sm border border-[var(--border)]">
                    <span className="text-sm text-[var(--text-secondary)] block">FIRE RADIATIVE POWER</span>
                    <span className="text-sm font-bold font-bold text-[var(--b-amber)]">{selectedItem.frp} MW</span>
                  </div>
                  <div className="bg-[var(--bg-base)] p-3 rounded-sm border border-[var(--border)]">
                    <span className="text-sm text-[var(--text-secondary)] block">COORDINATES</span>
                    <span className="text-xs font-bold text-[var(--text-primary)]">{selectedItem.latitude.toFixed(4)}, {selectedItem.longitude.toFixed(4)}</span>
                  </div>
                  <div className="bg-[var(--bg-base)] p-3 rounded-sm border border-[var(--border)]">
                    <span className="text-sm text-[var(--text-secondary)] block">FACILITY PROXIMITY</span>
                    <span className="text-xs font-bold text-[var(--b-cyan)]">{selectedItem.distance_to_facility.toFixed(1)} km</span>
                  </div>
                </div>

                {/* Notes Input */}
                <div className="space-y-1">
                  <label className="text-[10px] uppercase text-[var(--text-secondary)]">Analyst Justification & Verification Notes</label>
                  <input
                    type="text"
                    value={reviewerNotes}
                    onChange={(e) => setReviewerNotes(e.target.value)}
                    placeholder="e.g. Confirmed with visible flare stack on Sentinel-2 SWIR band..."
                    className="w-full bg-[var(--bg-base)] border border-[var(--border)] rounded-sm px-3 py-2 text-[var(--text-primary)] placeholder-slate-600 focus:outline-none focus:border-amber-500/60"
                  />
                </div>

                {/* Human Review Decision Actions */}
                <div className="space-y-2 pt-2">
                  <span className="text-[10px] uppercase text-[var(--text-secondary)] block">Select Verification Action:</span>
                  <div className="grid grid-cols-2 gap-2">
                    {/* Confirm AI */}
                    <button
                      disabled={submitting}
                      onClick={() => handleAction('CONFIRM')}
                      className="flex items-center justify-center space-x-2 py-2.5 rounded-sm bg-emerald-600 hover:bg-emerald-500 text-white font-bold transition-all disabled:opacity-50"
                    >
                      <CheckCircle className="w-4 h-4" />
                      <span>CONFIRM CANDIDATE ({selectedItem.predicted_class})</span>
                    </button>

                    {/* Uncertain */}
                    <button
                      disabled={submitting}
                      onClick={() => handleAction('UNCERTAIN')}
                      className="flex items-center justify-center space-x-2 py-2.5 rounded-sm bg-[var(--bg-card-hover)] hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] font-semibold border border-[var(--border-strong)] transition-all disabled:opacity-50"
                    >
                      <HelpCircle className="w-4 h-4 text-blue-400" />
                      <span>MARK AS UNCERTAIN</span>
                    </button>
                  </div>

                  {/* Correct Label Row */}
                  <div className="flex items-center space-x-2 bg-[var(--bg-base)] p-2.5 rounded-sm border border-[var(--border)]">
                    <span className="text-[var(--text-secondary)] text-sm shrink-0">CORRECT TO:</span>
                    <select
                      value={correctedClass}
                      onChange={(e) => setCorrectedClass(e.target.value as ThermalClass)}
                      className="bg-[var(--bg-card)] text-[var(--text-primary)] border border-[var(--border-strong)] rounded px-2 py-1 text-xs focus:outline-none focus:border-amber-500 flex-1"
                    >
                      {ALL_CLASSES.map((cls) => (
                        <option key={cls} value={cls}>{cls}</option>
                      ))}
                    </select>
                    <button
                      disabled={submitting}
                      onClick={() => handleAction('CORRECT')}
                      className="px-4 py-1.5 rounded-sm bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold transition-all disabled:opacity-50"
                    >
                      SUBMIT CORRECTION
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};









