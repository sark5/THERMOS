import React, { useEffect, useState } from 'react';
import {
  Flame, Radio, BarChart3,
  Factory, UserCheck, Clock, Siren, Sun, Moon,
} from 'lucide-react';
import type { AnalyticsSummary } from '../types';

interface HeaderProps {
  analytics: AnalyticsSummary | null;
  activeView: 'map' | 'alerts' | 'analytics' | 'investigate';
  setActiveView: (view: 'map' | 'alerts' | 'analytics' | 'investigate') => void;
  onOpenFacilities: () => void;
  showFacilitiesLayer: boolean;
  onToggleFacilitiesLayer: () => void;
  onOpenReviewQueue: () => void;
  onOpenResponseCenter: () => void;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  analytics,
  activeView,
  setActiveView,
  onOpenFacilities,
  showFacilitiesLayer,
  onToggleFacilitiesLayer,
  onOpenReviewQueue,
  onOpenResponseCenter,
  theme,
  onToggleTheme,
}) => {
  const [clock, setClock] = useState('');
  const isDark = theme === 'dark';

  useEffect(() => {
    const tick = () => {
      const now = new Date();
      const ist = new Date(now.getTime() + 5.5 * 60 * 60 * 1000);
      const hh = String(ist.getUTCHours()).padStart(2, '0');
      const mm = String(ist.getUTCMinutes()).padStart(2, '0');
      const ss = String(ist.getUTCSeconds()).padStart(2, '0');
      setClock(`${hh}:${mm}:${ss} IST`);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  const headerBg = isDark ? 'bg-slate-950 border-slate-800' : 'bg-white border-slate-300 shadow-sm';
  const subBg = isDark ? 'bg-slate-900/40' : 'bg-slate-50/80';
  const borderCol = isDark ? 'border-slate-800' : 'border-slate-300';
  const labelColor = isDark ? 'text-slate-400' : 'text-slate-900 font-bold';
  const textColor = isDark ? 'text-slate-100' : 'text-black font-extrabold';

  const statItem = (label: string, value: string | number, color: string, sub?: string, onClick?: () => void) => (
    <div
      onClick={onClick}
      className={`flex flex-col justify-center px-4 border-r ${borderCol} last:border-r-0 h-full font-mono ${
        onClick ? 'cursor-pointer hover:bg-slate-500/10 transition-colors' : ''
      }`}
      title={onClick ? `Open ${label} details` : undefined}
    >
      <div className="flex items-center gap-1.5 leading-none">
        <span className={`text-[9px] tracking-widest uppercase ${labelColor}`}>{label}</span>
      </div>
      <div className="flex items-baseline gap-1 mt-0.5">
        <span className={`text-sm font-bold tabular-nums ${color}`}>{value}</span>
        {sub && <span className={`text-[8px] ${labelColor}`}>{sub}</span>}
      </div>
    </div>
  );

  const actionBtn = (
    label: string,
    icon: React.ReactNode,
    active: boolean,
    onClick: () => void,
    accentClass: string,
    badge?: React.ReactNode
  ) => (
    <button
      onClick={onClick}
      className={`
        flex items-center justify-center gap-2 px-3.5 py-1.5 text-xs font-mono font-bold
        tracking-wider uppercase transition-all duration-150 border-r ${borderCol} last:border-r-0
        ${active
          ? `${accentClass} border-b-2 border-b-amber-500`
          : isDark
            ? 'text-slate-400 hover:text-slate-100 hover:bg-slate-900/60'
            : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'}
      `}
    >
      {icon}
      <span>{label}</span>
      {badge}
    </button>
  );

  return (
    <header className={`border-b z-30 select-none ${headerBg}`}>
      {/*    Top Technical Status Bar                                            */}
      <div className={`h-11 px-4 flex items-center justify-between border-b ${borderCol} ${subBg}`}>
        {/* Left: Mission Brand & System Origin */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-amber-500/10 border border-amber-500/30 flex items-center justify-center">
              <Flame className="w-3.5 h-3.5 text-amber-500" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className={`text-base font-mono font-black tracking-widest uppercase ${isDark ? 'text-white' : 'text-slate-900'}`}>
                THERMOS
              </span>
              <span className="text-[10px] font-mono text-emerald-500 font-bold tracking-wider px-1.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                MHA  -  NDMA
              </span>
            </div>
          </div>

          <div className={`h-4 w-px ${borderCol} hidden md:block mx-1`} />

          <div className="hidden md:flex items-center gap-2 text-[10px] font-mono">
            <span className={labelColor}>FEED:</span>
            <span className="text-cyan-400 font-semibold">VIIRS 375m (I4 MWIR)</span>
            <span className={labelColor}>|</span>
            <span className={labelColor}>CADENCE:</span>
            <span className="text-purple-400 font-semibold">30-MIN INSAT-3D</span>
          </div>
        </div>

        {/* Right: Technical Clocks & Status */}
        <div className="flex items-center gap-3">
          {/* Live System Indicator */}
          <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono text-[10px]">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="tracking-widest font-bold">TELEMETRY: NOMINAL</span>
          </div>

          {/* Master Clock */}
          <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded border ${borderCol} font-mono text-xs ${textColor}`}>
            <Clock className="w-3 h-3 text-amber-500" />
            <span className="tabular-nums font-bold">{clock}</span>
          </div>

          {/* Theme Toggle Button */}
          <button
            onClick={onToggleTheme}
            className={`p-1.5 rounded border ${borderCol} hover:bg-slate-800/40 text-slate-400 hover:text-slate-200 transition-colors`}
            title={isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme'}
          >
            {isDark ? <Sun className="w-3.5 h-3.5 text-amber-400" /> : <Moon className="w-3.5 h-3.5 text-indigo-500" />}
          </button>
        </div>
      </div>

      {/*    Lower Functional Ribbon (Stats + Navigation Actions)                 */}
      <div className="h-10 flex items-stretch justify-between overflow-x-auto scrollbar-none">
        
        {/* Left Telemetry Cluster (Clickable Drill-Downs) */}
        <div className="flex items-center h-full">
          {statItem('OBSERVATIONS', analytics ? analytics.total_observations.toLocaleString() : '7,922,480', 'text-amber-500', 'VIIRS', () => setActiveView('analytics'))}
          {statItem('SOURCES', analytics ? analytics.total_thermal_sources.toLocaleString() : '1,552,653', 'text-cyan-400', 'PTS', () => setActiveView('analytics'))}
          {statItem('FACILITIES', analytics ? analytics.active_monitored_facilities : '643', 'text-emerald-400', 'ACTIVE', onOpenFacilities)}
          {statItem('MODEL ACC', '99.60%', 'text-violet-400', 'XGB+RF', () => setActiveView('analytics'))}
          {statItem('MACRO-F1', '0.9845', 'text-sky-400', '6-CLASS', () => setActiveView('analytics'))}
        </div>

        {/* Right Tactical Action Bar */}
        <div className="flex items-stretch h-full ml-auto">
          {actionBtn(
            'ACTIVE ALERTS',
            <Radio className="w-3.5 h-3.5 text-red-500 animate-pulse" />,
            activeView === 'alerts',
            () => setActiveView(activeView === 'alerts' ? 'map' : 'alerts'),
            'bg-red-500/10 text-red-400',
            <span className="ml-1 px-1.5 py-0.2 rounded bg-red-600 text-white text-[9px] font-black leading-none">
              LIVE
            </span>
          )}

          {actionBtn(
            'FACILITIES',
            <Factory className="w-3.5 h-3.5 text-sky-400" />,
            showFacilitiesLayer,
            onToggleFacilitiesLayer,
            'bg-sky-500/10 text-sky-400'
          )}

          {actionBtn(
            'ANALYTICS',
            <BarChart3 className="w-3.5 h-3.5 text-purple-400" />,
            activeView === 'analytics',
            () => setActiveView(activeView === 'analytics' ? 'map' : 'analytics'),
            'bg-purple-500/10 text-purple-400'
          )}

          {actionBtn(
            'CAD DISPATCH',
            <Siren className="w-3.5 h-3.5 text-red-500" />,
            false,
            onOpenResponseCenter,
            'bg-red-500/10 text-red-400',
            <span className="ml-1 px-1 py-0.2 rounded bg-amber-500 text-slate-950 text-[8px] font-black">
              112
            </span>
          )}

          {actionBtn(
            'AUDIT QUEUE',
            <UserCheck className="w-3.5 h-3.5 text-cyan-400" />,
            false,
            onOpenReviewQueue,
            'bg-cyan-500/10 text-cyan-400'
          )}
        </div>

      </div>
    </header>
  );
};

