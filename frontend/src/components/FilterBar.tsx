import React from 'react';
import { AlertTriangle, SlidersHorizontal, Search } from 'lucide-react';
import type { ThermalClass, RiskBand } from '../types';
import { CLASS_CONFIG, ALL_CLASSES } from '../config/classConfig';

interface FilterBarProps {
  selectedClass: ThermalClass | 'ALL';
  setSelectedClass: (cls: ThermalClass | 'ALL') => void;
  selectedRisk: RiskBand | 'ALL';
  setSelectedRisk: (risk: RiskBand | 'ALL') => void;
  minFrp: number;
  setMinFrp: (frp: number) => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  totalEvents: number;
  loading: boolean;
  theme?: 'light' | 'dark';
}

export const FilterBar: React.FC<FilterBarProps> = ({
  selectedClass,
  setSelectedClass,
  selectedRisk,
  setSelectedRisk,
  minFrp,
  setMinFrp,
  searchQuery,
  setSearchQuery,
  totalEvents,
  loading,
  theme = 'dark',
}) => {
  const isDark = theme === 'dark';

  const barBg = isDark ? 'bg-slate-950/95 border-slate-800/60' : 'bg-white border-slate-300 shadow-sm';
  const labelColor = isDark ? 'text-slate-400' : 'text-slate-900 font-bold';
  const dividerColor = isDark ? 'bg-[var(--bg-card-hover)]' : 'bg-slate-300';
  
  // Pill styles
  const allActive = isDark 
    ? 'bg-slate-600/30 text-slate-100 border-slate-400/40' 
    : 'bg-slate-900 text-white border-slate-900 shadow-sm font-bold';
  const pillInactive = isDark
    ? 'bg-slate-900/40 text-slate-400 border-slate-800/40 hover:text-slate-200 hover:border-slate-700/60'
    : 'bg-slate-100 text-slate-900 font-bold border-slate-300 hover:text-black hover:border-slate-500 hover:bg-slate-200';

  // Input/Control styles
  const controlBg = isDark ? 'bg-slate-900/70 border-slate-800/60' : 'bg-slate-50 border-slate-300 shadow-sm';
  const controlText = isDark ? 'text-slate-100' : 'text-black font-bold';
  const controlPlaceholder = isDark ? 'placeholder-slate-500' : 'placeholder-slate-600';

  return (
    <div className={`${barBg} px-4 h-10 flex items-center gap-3 z-20 backdrop-blur-xl transition-colors duration-200 border-b`}>
      {/*  CLASS FILTER PILLS  */}
      <div className="flex items-center gap-1 overflow-x-auto scrollbar-none flex-shrink-0">
        <span className={`text-[10px] font-mono tracking-widest uppercase mr-1.5 flex-shrink-0 ${labelColor}`}>
          CLASS
        </span>

        <button
          onClick={() => setSelectedClass('ALL')}
          className={`h-7 px-3 rounded-sm text-xs shadow-sm font-semibold tracking-wide transition-all whitespace-nowrap flex items-center gap-1.5 border flex-shrink-0 ${selectedClass === 'ALL' ? allActive : pillInactive}`}
        >
          <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${isDark ? 'bg-slate-400' : 'bg-slate-500'}`} />
          ALL
        </button>

        {(ALL_CLASSES.filter((id) => id !== 'ALL') as (keyof typeof CLASS_CONFIG)[]).map((cls) => {
          const meta = CLASS_CONFIG[cls];
          const isActive = selectedClass === cls;
          return (
            <button
              key={cls}
              onClick={() => setSelectedClass(cls as ThermalClass)}
              className={`h-7 px-3 rounded-sm text-xs shadow-sm font-semibold tracking-wide transition-all whitespace-nowrap flex items-center gap-1.5 border flex-shrink-0 ${isActive ? 'font-bold shadow-sm' : pillInactive}`}
              style={
                isActive
                  ? {
                      backgroundColor: isDark ? `${meta.hex}1A` : `${meta.hex}15`,
                      color: isDark ? meta.hex : meta.hex,
                      borderColor: `${meta.hex}44`,
                    }
                  : {}
              }
            >
              <span
                className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                style={{ backgroundColor: meta.hex }}
              />
              {meta.label}
            </button>
          );
        })}
      </div>

      {/*  DIVIDER  */}
      <div className={`h-5 w-px flex-shrink-0 ${dividerColor}`} />

      {/*  AUXILIARY CONTROLS  */}
      <div className="ml-auto flex items-center gap-2 flex-shrink-0">
        
        {/* Risk selector */}
        <div className={`flex items-center gap-1.5 h-7 border rounded px-2 transition-colors ${controlBg}`}>
          <AlertTriangle className="w-3 h-3 text-amber-500 flex-shrink-0" />
          <span className={`text-[10px] font-mono tracking-widest uppercase ${labelColor}`}>RISK</span>
          <select
            value={selectedRisk}
            onChange={(e) => setSelectedRisk(e.target.value as RiskBand | 'ALL')}
            className={`bg-transparent text-xs font-mono focus:outline-none cursor-pointer pr-1 ${controlText}`}
          >
            <option value="ALL" className={isDark ? 'bg-slate-900' : 'bg-white'}>ALL</option>
            <option value="CRITICAL" className={`${isDark ? 'bg-slate-900' : 'bg-white'} text-red-500 font-bold`}>CRITICAL</option>
            <option value="HIGH" className={`${isDark ? 'bg-slate-900' : 'bg-white'} text-amber-500 font-bold`}>HIGH</option>
            <option value="MEDIUM" className={`${isDark ? 'bg-slate-900' : 'bg-white'} text-blue-500 font-bold`}>MEDIUM</option>
            <option value="LOW" className={`${isDark ? 'bg-slate-900' : 'bg-white'} ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>LOW</option>
          </select>
        </div>

        {/* Min FRP slider */}
        <div className={`flex items-center gap-1.5 h-7 border rounded px-2 transition-colors ${controlBg}`}>
          <SlidersHorizontal className="w-3 h-3 text-cyan-500 flex-shrink-0" />
          <span className={`text-[10px] font-mono tracking-widest uppercase ${labelColor}`}>FRP&gt;=</span>
          <input
            type="range"
            min="0"
            max="120"
            step="5"
            value={minFrp}
            onChange={(e) => setMinFrp(Number(e.target.value))}
            className="w-16 accent-amber-500 cursor-pointer h-1"
          />
          <span className="text-amber-500 font-mono text-sm w-10 text-right font-bold tabular-nums">
            {minFrp}MW
          </span>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className={`w-3 h-3 absolute left-2 top-1/2 -translate-y-1/2 ${labelColor}`} />
          <input
            type="text"
            placeholder="Event ID / Facility..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className={`h-7 ${controlBg} ${controlText} ${controlPlaceholder} text-xs font-mono pl-7 pr-3 rounded border focus:outline-none focus:border-amber-500/50 w-44 transition-colors`}
          />
        </div>

        {/* Event count badge */}
        <div className={`h-7 border rounded px-2.5 flex items-center transition-colors ${controlBg}`}>
          {loading ? (
            <span className="text-[10px] font-mono text-amber-500 animate-pulse tracking-wider">SYNCING...</span>
          ) : (
            <span className="text-xs font-mono">
              <span className="text-amber-500 font-bold tabular-nums">{totalEvents.toLocaleString()}</span>
              <span className={`ml-1 tracking-widest uppercase text-sm ${labelColor}`}>Hotspots</span>
            </span>
          )}
        </div>

      </div>
    </div>
  );
};





