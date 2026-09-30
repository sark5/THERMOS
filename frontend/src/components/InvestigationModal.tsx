 import React, { useState } from 'react';
import { X, Bot, Send, CheckCircle2, AlertTriangle, Sparkles } from 'lucide-react';
import type { InvestigationResponse } from '../types';
import { submitInvestigation } from '../services/api';

interface InvestigationModalProps {
  initialEventId?: string | null;
  onClose: () => void;
  theme?: 'light' | 'dark';
}

export const InvestigationModal: React.FC<InvestigationModalProps> = ({ initialEventId, onClose }) => {
  const [query, setQuery] = useState(
    initialEventId
      ? `Explain why event #${initialEventId} is classified as an industrial fire`
      : 'Why is the hotspot near Paradip Refinery classified as an industrial flare?'
  );
  const [response, setResponse] = useState<InvestigationResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (qText?: string) => {
    const textToSubmit = qText || query;
    if (!textToSubmit.trim()) return;
    setLoading(true);
    try {
      const res = await submitInvestigation(textToSubmit, initialEventId || undefined);
      setResponse(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-md w-full max-w-2xl shadow-2xl ring-1 ring-black/5 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-5 border-b border-[var(--border)] flex items-center justify-between bg-[var(--bg-base)]">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-sm bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-[var(--b-cyan)]">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-sm font-bold font-bold text-[var(--text-primary)]">AI INVESTIGATION ASSISTANT</h3>
                <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-cyan-500/20 text-[var(--b-cyan)] border border-cyan-500/30">
                  SHAP CORROBORATED
                </span>
              </div>
              <p className="text-xs font-mono text-[var(--text-secondary)]">
                Natural-language multi-domain causal inquiry & evidence synthesis
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)]">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Query Input Box */}
        <div className="p-5 border-b border-[var(--border)] bg-[var(--bg-base)] space-y-3">
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Ask: 'Why is this classified as X?' or 'Check anomaly at refinery Y'..."
              className="flex-1 bg-[var(--bg-base)] border border-[var(--border-strong)] rounded-sm px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500/80"
            />
            <button
              onClick={() => handleSearch()}
              disabled={loading}
              className="px-4 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 rounded-sm font-bold text-xs flex items-center space-x-1.5 transition-all shadow-lg shadow-cyan-500/20 disabled:opacity-50"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Query</span>
            </button>
          </div>

          {/* Quick Prompts */}
          <div className="flex flex-wrap gap-1.5 text-xs font-mono">
            <span className="text-[var(--text-muted)] py-0.5">Quick Queries:</span>
            {[
              'Why is this an industrial fire and not a flare?',
              'Investigate open-cast mining signature at Jharia',
              'Check wildfire expansion evidence in forest zone',
            ].map((prompt, i) => (
              <button
                key={i}
                onClick={() => {
                  setQuery(prompt);
                  handleSearch(prompt);
                }}
                className="px-2 py-0.5 rounded-md bg-[var(--bg-base)] text-[var(--text-secondary)] hover:text-[var(--b-cyan)] border border-[var(--border)] transition-colors"
              >
                "{prompt}"
              </button>
            ))}
          </div>
        </div>

        {/* Results Area */}
        <div className="p-6 max-h-[420px] overflow-y-auto space-y-4">
          {loading ? (
            <div className="py-12 text-center text-[var(--text-secondary)] font-mono text-xs">
              <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-sm animate-spin mx-auto mb-3" />
              Synthesizing 83 Canonical Features, Facility Buffers & Historical FRP Baselines...
            </div>
          ) : response ? (
            <div className="space-y-4">
              {/* Verdict Card */}
              <div className="p-4 rounded-sm bg-[var(--bg-base)] border border-[var(--border)] space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Sparkles className="w-4 h-4 text-[var(--b-cyan)]" />
                    <span className="text-[9px] font-bold text-[var(--text-primary)] uppercase tracking-wider">AI System Verdict</span>
                  </div>
                  <span className="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-emerald-500/20 text-[var(--b-emerald)] border border-emerald-500/30">
                    {response.confidence}% CONFIDENCE
                  </span>
                </div>
                <div className="text-xs font-bold font-semibold text-[var(--text-primary)]">
                  {response.system_verdict}
                </div>
              </div>

              {/* Primary Evidence */}
              <div className="space-y-2">
                <span className="text-[9px] font-bold font-mono text-[var(--text-secondary)] uppercase tracking-wider">
                  Corroborating Telemetry & Evidence:
                </span>
                <div className="space-y-1.5 font-mono text-xs">
                  {response.primary_evidence.map((ev, i) => (
                    <div key={i} className="flex items-start space-x-2 bg-[var(--bg-base)] p-2.5 rounded-sm border border-[var(--border)] text-[var(--text-primary)]">
                      <CheckCircle2 className="w-4 h-4 text-[var(--b-emerald)] shrink-0 mt-0.5" />
                      <span>{ev}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommendation */}
              <div className="p-3.5 rounded-sm bg-amber-500/10 border border-amber-500/30 flex items-start space-x-3 text-xs font-mono">
                <AlertTriangle className="w-4 h-4 text-[var(--b-amber)] shrink-0 mt-0.5" />
                <div>
                  <span className="text-[var(--b-amber)] font-bold block mb-0.5">Operational Protocol:</span>
                  <p className="text-[var(--text-primary)]">{response.operational_recommendation}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="py-10 text-center text-[var(--text-muted)] font-mono text-xs">
              Type an event ID or question above to generate an instant multi-domain AI incident report.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};








