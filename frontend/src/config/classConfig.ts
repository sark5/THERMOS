 /**
 * THERMOS  -  Single source of truth for all 6 thermal class colors.
 *
 * Every component (MapCanvas, FilterBar, EventInspector, AnalyticsPanel, etc.)
 * imports from here so the legend, map dots, badges, and charts are always
 * pixel-perfectly consistent.
 *
 * Color palette designed for high-contrast visibility on:
 *   * Dark tactical basemap (dark background)
 *   * Esri satellite imagery (mixed earth tones)
 */

export type ThermalClassKey =
  | 'INDUSTRIAL_FLARE'
  | 'INDUSTRIAL_FIRE'
  | 'MINING'
  | 'AGRICULTURAL'
  | 'WILDFIRE'
  | 'UNCLASSIFIED';

export interface ClassMeta {
  /** Raw hex  -  used for MapLibre WebGL paint expressions */
  hex: string;
  /** Tailwind utility for a solid dot / circle (bg-*) */
  dot: string;
  /** Tailwind badge styles: bg + text + border */
  badge: { bg: string; text: string; border: string };
  /** Short human label */
  label: string;
  /** One-line description shown in tooltips / inspector */
  description: string;
}

export const CLASS_CONFIG: Record<ThermalClassKey, ClassMeta> = {
  INDUSTRIAL_FLARE: {
    hex: '#FACC15',                 // bright amber-yellow
    dot: 'bg-yellow-400',
    badge: { bg: 'bg-yellow-400/15', text: 'text-[var(--b-yellow)]', border: 'border-yellow-400/40' },
    label: 'Industrial Flare',
    description: 'Routine gas flaring from refineries, petrochemical plants & LNG terminals',
  },
  INDUSTRIAL_FIRE: {
    hex: '#EF4444',                 // vivid red
    dot: 'bg-red-500',
    badge: { bg: 'bg-red-500/20', text: 'text-[var(--b-red)]', border: 'border-red-500/40' },
    label: 'Industrial Fire',
    description: 'Uncontrolled fires within industrial / factory perimeters',
  },
  MINING: {
    hex: '#FB923C',                 // orange (distinct from yellow flare)
    dot: 'bg-orange-400',
    badge: { bg: 'bg-orange-400/15', text: 'text-[var(--b-orange)]', border: 'border-orange-400/40' },
    label: 'Mining',
    description: 'Open-cast mines, coal seam fires & overburden dump smouldering',
  },
  AGRICULTURAL: {
    hex: '#22C55E',                 // bright green
    dot: 'bg-green-500',
    badge: { bg: 'bg-green-500/15', text: 'text-[var(--b-green)]', border: 'border-green-500/30' },
    label: 'Agricultural',
    description: 'Post-harvest residue burning & controlled field clearing',
  },
  WILDFIRE: {
    hex: '#C026D3',                 // magenta-purple
    dot: 'bg-fuchsia-600',
    badge: { bg: 'bg-fuchsia-600/15', text: 'text-[var(--b-purple)]', border: 'border-fuchsia-500/40' },
    label: 'Wildfire',
    description: 'Uncontrolled forest, grassland & savanna fires',
  },
  UNCLASSIFIED: {
    hex: '#94A3B8',                 // slate-blue (neutral)
    dot: 'bg-slate-400',
    badge: { bg: 'bg-slate-500/15', text: 'text-slate-400', border: 'border-slate-500/30' },
    label: 'Unclassified',
    description: 'Low-confidence detections without definitive class assignment',
  },
};

/** Ordered list of ALL class keys (ALL selector + the 6 classes) */
export const ALL_CLASSES: Array<'ALL' | ThermalClassKey> = [
  'ALL',
  'INDUSTRIAL_FLARE',
  'INDUSTRIAL_FIRE',
  'MINING',
  'AGRICULTURAL',
  'WILDFIRE',
  'UNCLASSIFIED',
];

/** Quick hex lookup  -  returns the class hex or a neutral gray as fallback */
export function classHex(cls: string): string {
  return (CLASS_CONFIG as Record<string, ClassMeta>)[cls]?.hex ?? '#94A3B8';
}

/**
 * Builds the MapLibre GL JS `match` expression for circle-color.
 * Explicitly enumerates all 6 class strings exactly as the backend sends them.
 * Usage inside a paint property:
 *   'circle-color': buildMatchExpr() as any
 */
export function buildMatchExpr(): unknown[] {
  return [
    'match',
    ['get', 'primary_class'],
    'INDUSTRIAL_FLARE', CLASS_CONFIG.INDUSTRIAL_FLARE.hex,
    'INDUSTRIAL_FIRE',  CLASS_CONFIG.INDUSTRIAL_FIRE.hex,
    'MINING',           CLASS_CONFIG.MINING.hex,
    'AGRICULTURAL',     CLASS_CONFIG.AGRICULTURAL.hex,
    'WILDFIRE',         CLASS_CONFIG.WILDFIRE.hex,
    'UNCLASSIFIED',     CLASS_CONFIG.UNCLASSIFIED.hex,
    '#94A3B8', // fallback
  ];
}

/**
 * Builds a MapLibre `match` expression for circle-stroke-color.
 * Each class gets a lighter contrasting stroke for better visibility.
 */
export function buildStrokeMatchExpr(): unknown[] {
  return [
    'match',
    ['get', 'primary_class'],
    'INDUSTRIAL_FLARE', '#FEF08A',  // light yellow
    'INDUSTRIAL_FIRE',  '#FCA5A5',  // light red
    'MINING',           '#FDBA74',  // light orange
    'AGRICULTURAL',     '#86EFAC',  // light green
    'WILDFIRE',         '#F0ABFC',  // light magenta
    'UNCLASSIFIED',     '#CBD5E1',  // light slate
    '#ffffff',
  ];
}



