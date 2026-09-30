 import React, { useState } from 'react';
import { X, Building2, Search, ExternalLink, MapPin } from 'lucide-react';
import type { Facility } from '../types';

interface FacilitiesListModalProps {
  facilities: Facility[];
  onClose: () => void;
  onSelectFacility: (id: number) => void;
  onLocateFacility: (coords: [number, number]) => void;
  theme?: 'light' | 'dark';
}

export const FacilitiesListModal: React.FC<FacilitiesListModalProps> = ({
  facilities,
  onClose,
  onSelectFacility,
  onLocateFacility,
}) => {
  const [filterType, setFilterType] = useState<string>('ALL');
  const [search, setSearch] = useState('');

  const types = ['ALL', 'refinery', 'mine', 'powerplant', 'flare', 'quarry', 'industrial'];

  const filtered = facilities.filter((f) => {
    const matchType = filterType === 'ALL' || f.facility_type.toLowerCase() === filterType.toLowerCase();
    const matchSearch =
      f.name.toLowerCase().includes(search.toLowerCase()) ||
      f.operator.toLowerCase().includes(search.toLowerCase());
    return matchType && matchSearch;
  });

  return (
    <div className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-md w-full max-w-3xl shadow-2xl ring-1 ring-black/5 overflow-hidden animate-in fade-in zoom-in-95 duration-200 flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="p-5 border-b border-[var(--border)] flex items-center justify-between bg-[var(--bg-base)]">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-sm bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-[var(--b-cyan)]">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold font-bold text-[var(--text-primary)]">INDUSTRIAL & ENERGY FACILITIES DIRECTORY</h3>
              <p className="text-xs font-mono text-[var(--text-secondary)]">
                643 Monitored Refineries, Mines, Flare Hubs, Power Plants & Quarries
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)]">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Filters */}
        <div className="p-4 border-b border-[var(--border)] bg-[var(--bg-base)] flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center space-x-1.5 overflow-x-auto">
            {types.map((t) => (
              <button
                key={t}
                onClick={() => setFilterType(t)}
                className={`px-2.5 py-1 rounded-md text-[10px] font-mono font-semibold uppercase transition-all ${
                  filterType === t
                    ? 'bg-sky-500 text-slate-950 shadow-sm'
                    : 'bg-[var(--bg-base)] text-[var(--text-secondary)] hover:bg-[var(--bg-card-hover)] hover:text-white border border-[var(--border)]'
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
            <input
              type="text"
              placeholder="Search facility / operator..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-[var(--bg-base)] text-[var(--text-primary)] placeholder-slate-500 text-xs pl-8 pr-3 py-1.5 rounded-sm border border-[var(--border)] focus:outline-none focus:border-sky-500 w-56"
            />
          </div>
        </div>

        {/* Facility Cards List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {filtered.length === 0 ? (
            <div className="p-8 text-center text-[var(--text-muted)] font-mono text-xs">
              No facilities found matching current filters.
            </div>
          ) : (
            filtered.slice(0, 100).map((f) => (
              <div
                key={f.id}
                className="bg-[var(--bg-base)] border border-[var(--border)] rounded-sm p-3 flex items-center justify-between hover:border-[var(--border-strong)] transition-colors"
              >
                <div className="space-y-0.5">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-xs text-[var(--text-primary)]">{f.name}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-sky-500/15 text-[var(--b-cyan)] border border-sky-500/30 uppercase">
                      {f.facility_type}
                    </span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/15 text-[var(--b-amber)] border border-amber-500/30">
                      {f.criticality} CRITICALITY
                    </span>
                  </div>
                  <div className="text-xs font-mono text-[var(--text-secondary)]">
                    Operator: <strong className="text-[var(--text-primary)]">{f.operator}</strong> * Coordinates: {f.latitude}, {f.longitude}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => {
                      onLocateFacility([f.longitude, f.latitude]);
                      onClose();
                    }}
                    className="p-1.5 rounded-sm bg-[var(--bg-card-hover)] hover:bg-slate-500/20 text-[var(--b-cyan)] text-xs transition-colors border border-[var(--border)]"
                    title="Zoom on Map"
                  >
                    <MapPin className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => {
                      onSelectFacility(f.id);
                      onClose();
                    }}
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded-sm bg-sky-500/15 hover:bg-sky-500/25 text-[var(--b-cyan)] text-xs font-mono font-bold border border-sky-500/40 shadow-sm transition-all"
                  >
                    <span>Digital Twin</span>
                    <ExternalLink className="w-3.5 h-3.5" />
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









