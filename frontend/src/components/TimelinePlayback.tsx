 import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, Calendar, Clock } from 'lucide-react';

interface TimelinePlaybackProps {
  onDateChange?: (date: string) => void;
  theme?: 'light' | 'dark';
}

const TIMELINE_STEPS = [
  '2018-04-15',
  '2019-10-20',
  '2020-05-12',
  '2021-11-05',
  '2022-03-30',
  '2023-04-18',
  '2024-03-15',
  '2025-04-10',
  '2026-09-01',
];

const fmt = (d: string) => {
  const [y, m] = d.split('-');
  const months = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];
  return `${months[parseInt(m, 10) - 1]} ${y}`;
};

export const TimelinePlayback: React.FC<TimelinePlaybackProps> = ({ onDateChange }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [stepIndex, setStepIndex] = useState(6); // default 2024
  const [speed, setSpeed] = useState<number>(1);

  useEffect(() => {
    let timer: ReturnType<typeof setInterval>;
    if (isPlaying) {
      timer = setInterval(() => {
        setStepIndex((prev) => {
          const next = prev + 1 >= TIMELINE_STEPS.length ? 0 : prev + 1;
          if (onDateChange) onDateChange(TIMELINE_STEPS[next]);
          return next;
        });
      }, 1500 / speed);
    }
    return () => clearInterval(timer);
  }, [isPlaying, speed, onDateChange]);

  return (
    <div
      className="
        absolute bottom-4 left-1/2 -translate-x-1/2 z-20
        bg-[var(--bg-card)] border border-[var(--border)] rounded-md
        px-5 py-2.5 flex items-center gap-4
        shadow-2xl ring-1 ring-black/5 shadow-black/60 backdrop-blur-xl
        font-mono text-xs select-none
        min-w-[460px]
      "
    >
      {/* Label */}
      <div className="flex flex-col items-center flex-shrink-0">
        <div className="flex items-center gap-1 text-xs tracking-[0.18em] text-slate-600 uppercase mb-0.5">
          <Clock className="w-2.5 h-2.5" />
          TEMPORAL SCAN
        </div>
        <div className="flex items-center gap-1.5">
          <Calendar className="w-3 h-3 text-[var(--b-amber)] flex-shrink-0" />
          <span className="text-[var(--b-amber)] font-bold text-[9px] font-bold tabular-nums tracking-widest">
            {fmt(TIMELINE_STEPS[stepIndex])}
          </span>
        </div>
      </div>

      {/* Divider */}
      <div className="h-8 w-px bg-[var(--bg-card-hover)] flex-shrink-0" />

      {/* Scrub slider */}
      <div className="flex-1 flex flex-col gap-1 min-w-0">
        <input
          type="range"
          min="0"
          max={TIMELINE_STEPS.length - 1}
          value={stepIndex}
          onChange={(e) => {
            const val = Number(e.target.value);
            setStepIndex(val);
            if (onDateChange) onDateChange(TIMELINE_STEPS[val]);
          }}
          className="w-full accent-amber-500 cursor-pointer h-1.5 rounded-sm"
        />
        {/* Tick labels */}
        <div className="flex justify-between text-xs text-slate-700 tracking-wide px-0.5">
          <span>2018</span>
          <span>2020</span>
          <span>2022</span>
          <span>2024</span>
          <span>2026</span>
        </div>
      </div>

      {/* Divider */}
      <div className="h-8 w-px bg-[var(--bg-card-hover)] flex-shrink-0" />

      {/* Speed */}
      <div className="flex items-center gap-1 bg-[var(--bg-base)] border border-[var(--border)] rounded-sm px-2 py-1 flex-shrink-0">
        <span className="text-[9px] text-slate-600 tracking-widest mr-0.5">SPD</span>
        {[1, 2, 5].map((s) => (
          <button
            key={s}
            onClick={() => setSpeed(s)}
            className={`px-1.5 py-0.5 rounded text-sm font-bold transition-all ${
              speed === s
                ? 'bg-amber-500/20 text-[var(--b-amber)]'
                : 'text-slate-600 hover:text-[var(--text-primary)]'
            }`}
          >
            {s}x
          </button>
        ))}
      </div>

      {/* Play/Pause */}
      <button
        onClick={() => setIsPlaying(!isPlaying)}
        className={`
          w-9 h-9 rounded-sm flex items-center justify-center flex-shrink-0
          transition-all duration-150
          ${isPlaying
            ? 'bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/30'
            : 'bg-[var(--bg-card-hover)] text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)]'}
        `}
      >
        {isPlaying
          ? <Pause className="w-4 h-4 fill-current" />
          : <Play  className="w-4 h-4 fill-current ml-0.5" />}
      </button>

      {/* Reset */}
      <button
        onClick={() => { setStepIndex(0); if (onDateChange) onDateChange(TIMELINE_STEPS[0]); }}
        className="p-2 rounded-sm text-slate-600 hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)] transition-all flex-shrink-0"
        title="Reset to 2018"
      >
        <RotateCcw className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};









