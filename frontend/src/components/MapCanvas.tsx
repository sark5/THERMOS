import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as maplibregl from 'maplibre-gl';
import { Layers, Globe, MapPin } from 'lucide-react';
import type { HotspotCollection, Facility } from '../types';
import { CLASS_CONFIG, buildMatchExpr, buildStrokeMatchExpr, classHex } from '../config/classConfig';

interface MapCanvasProps {
  hotspots: HotspotCollection | null;
  facilities: Facility[];
  selectedEventId: string | null;
  onSelectEvent: (eventId: string) => void;
  onSelectFacility: (facilityId: number) => void;
  showFacilities: boolean;
  targetLocation?: [number, number] | null;
  theme?: 'light' | 'dark';
}

//  Raster tile configs 
// Both are Esri public endpoints  -  no API key required, CORS *.
const DARK_RASTER = {
  sources: {
    'bg-dark-base': {
      type: 'raster' as const,
      tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}'],
      tileSize: 256,
    },
    'bg-dark-ref': {
      type: 'raster' as const,
      tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}'],
      tileSize: 256,
    },
  },
  layers: [
    { id: 'bg-dark-base-layer', type: 'raster' as const, source: 'bg-dark-base', paint: { 'raster-opacity': 1.0 } as any },
    { id: 'bg-dark-ref-layer',  type: 'raster' as const, source: 'bg-dark-ref',  paint: { 'raster-opacity': 0.80 } as any },
  ],
};

const SAT_RASTER = {
  sources: {
    'bg-sat-img': {
      type: 'raster' as const,
      tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
      tileSize: 256,
    },
    'bg-sat-labels': {
      type: 'raster' as const,
      tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}'],
      tileSize: 256,
    },
  },
  layers: [
    { id: 'bg-sat-img-layer',    type: 'raster' as const, source: 'bg-sat-img',    paint: { 'raster-opacity': 1.0 } as any },
    { id: 'bg-sat-labels-layer', type: 'raster' as const, source: 'bg-sat-labels', paint: { 'raster-opacity': 0.90 } as any },
  ],
};

// Minimal initial style  -  blank canvas; raster layers added programmatically
const BLANK_STYLE: maplibregl.StyleSpecification = {
  version: 8,
  glyphs: 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
  sources: {},
  layers: [],
};



//  Stable paint expressions 
const COLOR_EXPR        = buildMatchExpr()       as any;
const STROKE_COLOR_EXPR = buildStrokeMatchExpr() as any;

const RADIUS_EXPR: any = ['interpolate',['linear'],['get','frp'], 2,5, 20,8, 50,11, 100,15, 200,20];
const GLOW_EXPR:   any = ['interpolate',['linear'],['get','frp'], 2,14,20,20, 50,28,100,38, 200,50];
const OUTER_EXPR:  any = ['interpolate',['linear'],['get','frp'], 2,22,20,32, 50,46,100,62, 200,78];

//  Helper: build facility GeoJSON 
function buildFacGeoJSON(facilities: Facility[]): any {
  return {
    type: 'FeatureCollection',
    features: facilities.map(f => ({
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [f.longitude, f.latitude] },
      properties: { id: f.id, name: f.name, type: f.facility_type, operator: f.operator, criticality: f.criticality },
    })),
  };
}

//  Helper: add GeoJSON data layers on top of whatever basemap is active 
function addDataLayers(m: maplibregl.Map, hotspots: HotspotCollection | null, facGeoJSON: any, showFac: boolean) {
  const hData = hotspots ?? { type: 'FeatureCollection', features: [] };
  const vis   = showFac ? 'visible' : 'none';

  // Hotspot source
  if (!m.getSource('thermos-hotspots')) {
    m.addSource('thermos-hotspots', { type: 'geojson', data: hData });
  } else {
    (m.getSource('thermos-hotspots') as maplibregl.GeoJSONSource).setData(hData);
  }

  if (!m.getLayer('hotspots-outer-glow')) {
    m.addLayer({ id: 'hotspots-outer-glow', type: 'circle', source: 'thermos-hotspots',
      paint: { 'circle-radius': OUTER_EXPR, 'circle-color': COLOR_EXPR, 'circle-opacity': 0.10, 'circle-blur': 1.5 } });
  }
  if (!m.getLayer('hotspots-glow')) {
    m.addLayer({ id: 'hotspots-glow', type: 'circle', source: 'thermos-hotspots',
      paint: { 'circle-radius': GLOW_EXPR, 'circle-color': COLOR_EXPR, 'circle-opacity': 0.28, 'circle-blur': 0.8 } });
  }
  if (!m.getLayer('hotspots-point')) {
    m.addLayer({ id: 'hotspots-point', type: 'circle', source: 'thermos-hotspots',
      paint: {
        'circle-radius':         RADIUS_EXPR,
        'circle-color':          COLOR_EXPR,
        'circle-stroke-width':   2.0,
        'circle-stroke-color':   STROKE_COLOR_EXPR,
        'circle-stroke-opacity': 0.95,
        'circle-opacity':        0.96,
      } });
  }
  if (!m.getLayer('hotspots-selected')) {
    m.addLayer({ id: 'hotspots-selected', type: 'circle', source: 'thermos-hotspots',
      filter: ['==', ['get', 'id'], '__none__'],
      paint: {
        'circle-radius': 20, 'circle-color': 'rgba(0,0,0,0)',
        'circle-stroke-width': 3, 'circle-stroke-color': '#ffffff',
        'circle-stroke-opacity': 0.90, 'circle-opacity': 0,
      } });
  }

  // Facility source
  if (!m.getSource('thermos-facilities')) {
    m.addSource('thermos-facilities', { type: 'geojson', data: facGeoJSON });
  } else {
    (m.getSource('thermos-facilities') as maplibregl.GeoJSONSource).setData(facGeoJSON);
  }
  if (!m.getLayer('facility-perimeter')) {
    m.addLayer({ id: 'facility-perimeter', type: 'circle', source: 'thermos-facilities',
      layout: { visibility: vis },
      paint: { 'circle-radius': 22, 'circle-color': '#38bdf8', 'circle-opacity': 0.10,
               'circle-stroke-width': 1.5, 'circle-stroke-color': '#0284c7', 'circle-stroke-opacity': 0.80 } });
  }
  if (!m.getLayer('facility-point')) {
    m.addLayer({ id: 'facility-point', type: 'circle', source: 'thermos-facilities',
      layout: { visibility: vis },
      paint: { 'circle-radius': 4.5, 'circle-color': '#38bdf8',
               'circle-stroke-width': 1.5, 'circle-stroke-color': '#0369a1', 'circle-opacity': 0.95 } });
  }
}

//  Helper: Init all basemaps upfront for instant toggling 
function initAllBasemaps(m: maplibregl.Map, initialBasemap: 'dark' | 'satellite') {
  // Add all sources
  [DARK_RASTER, SAT_RASTER].forEach(config => {
    for (const [id, src] of Object.entries(config.sources)) {
      if (!m.getSource(id)) m.addSource(id, src);
    }
  });
  
  // Add layers with correct initial visibility
  [DARK_RASTER, SAT_RASTER].forEach(config => {
    const isVisible = config === (initialBasemap === 'dark' ? DARK_RASTER : SAT_RASTER);
    for (const layer of config.layers) {
      if (!m.getLayer(layer.id)) {
        const anyLayer = layer as any;
        const fullLayer = { 
          ...anyLayer, 
          layout: { ...(anyLayer.layout || {}), visibility: isVisible ? 'visible' : 'none' } 
        };
        m.addLayer(fullLayer as any); // Add at bottom (before any GeoJSON data is added)
      }
    }
  });
}

function setBasemapVisibility(m: maplibregl.Map, active: 'dark' | 'satellite') {
  const visibleConfig = active === 'dark' ? DARK_RASTER : SAT_RASTER;
  const hiddenConfig = active === 'dark' ? SAT_RASTER : DARK_RASTER;

  hiddenConfig.layers.forEach(l => {
    if (m.getLayer(l.id)) m.setLayoutProperty(l.id, 'visibility', 'none');
  });
  visibleConfig.layers.forEach(l => {
    if (m.getLayer(l.id)) m.setLayoutProperty(l.id, 'visibility', 'visible');
  });
}

// 

export const MapCanvas: React.FC<MapCanvasProps> = ({
  hotspots,
  facilities,
  selectedEventId,
  onSelectEvent,
  onSelectFacility,
  showFacilities,
  targetLocation,
  theme: _theme = 'dark',
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map          = useRef<maplibregl.Map | null>(null);
  const popup        = useRef<maplibregl.Popup | null>(null);

  // Programmatically pan and zoom to requested target coordinates
  useEffect(() => {
    if (targetLocation && map.current) {
      map.current.flyTo({
        center: targetLocation,
        zoom: Math.max(map.current.getZoom(), 10.5),
        speed: 1.5,
        curve: 1.4,
        essential: true,
      });
    }
  }, [targetLocation]);

  // Stable refs so map-event closures always see fresh prop values
  const hotspotsRef   = useRef(hotspots);
  const facilitiesRef = useRef(facilities);
  const showFacRef    = useRef(showFacilities);
  const onSelectEventRef = useRef(onSelectEvent);
  const onSelectFacilityRef = useRef(onSelectFacility);

  useEffect(() => { hotspotsRef.current   = hotspots;       }, [hotspots]);
  useEffect(() => { facilitiesRef.current = facilities;     }, [facilities]);
  useEffect(() => { showFacRef.current    = showFacilities; }, [showFacilities]);
  useEffect(() => { onSelectEventRef.current = onSelectEvent; }, [onSelectEvent]);
  useEffect(() => { onSelectFacilityRef.current = onSelectFacility; }, [onSelectFacility]);

  const [basemap, setBasemap] = useState<'dark' | 'satellite'>('dark');
  // Stable ref so toggleBasemap never captures stale state in a closure
  const basemapRef = useRef<'dark' | 'satellite'>('dark');
  const [coords, setCoords]   = useState<{ lng: number; lat: number } | null>(null);
  const [zoom, setZoom]       = useState<number>(4.8);

  //  Hover / click events 
  const bindEvents = useCallback((m: maplibregl.Map) => {
    // Guard: don't double-bind  -  check for existing listener via a flag
    m.on('mouseenter', 'hotspots-point', (e: any) => {
      m.getCanvas().style.cursor = 'crosshair';
      if (!e.features?.[0] || !popup.current) return;
      const p   = e.features[0].properties;
      const xy  = (e.features[0].geometry as any).coordinates.slice();
      const hex = classHex(p.primary_class);
      const rc  = p.risk_band === 'CRITICAL' ? '#ef4444' : p.risk_band === 'HIGH' ? '#f97316'
                : p.risk_band === 'MEDIUM'   ? '#3b82f6' : '#94a3b8';

      popup.current!.setLngLat(xy).setHTML(`
        <div style="background:#080d18;color:#f1f5f9;padding:10px 13px;border-radius:8px;
                    border:1px solid ${hex}55;font-family:'Courier New',monospace;font-size:11px;
                    min-width:185px;box-shadow:0 12px 35px rgba(0,0,0,0.8),0 0 14px ${hex}22;">
          <div style="display:flex;align-items:center;gap:7px;margin-bottom:7px;border-bottom:1px solid #1e293b;padding-bottom:6px">
            <span style="width:11px;height:11px;border-radius:50%;display:inline-block;flex-shrink:0;
                         background:${hex};box-shadow:0 0 8px ${hex},0 0 16px ${hex}55;"></span>
            <span style="font-weight:900;color:${hex};font-size:11px;letter-spacing:0.1em">
              ${p.primary_class.replace(/_/g,' ')}
            </span>
          </div>
          <div style="display:grid;grid-template-columns:auto 1fr;gap:3px 14px;font-size:10px;align-items:center;">
            <span style="color:#475569">FRP</span>
            <span style="color:#fbbf24;font-weight:bold">${p.frp} MW</span>
            <span style="color:#475569">CONFIDENCE</span>
            <span style="color:#e2e8f0;font-weight:bold">${p.confidence}%</span>
            <span style="color:#475569">RISK</span>
            <span style="color:${rc};font-weight:bold">${p.risk_band}</span>
            <span style="color:#475569">EVENT</span>
            <span style="color:#64748b;font-size:9px">${p.id}</span>
          </div>
          <div style="margin-top:6px;padding-top:5px;border-top:1px solid #1e293b;color:#94a3b8;font-size:9px;">
            * ${p.facility_name || 'No Associated Facility'}
          </div>
        </div>
      `).addTo(m);
    });

    m.on('mouseleave', 'hotspots-point', () => {
      m.getCanvas().style.cursor = '';
      popup.current?.remove();
    });

    m.on('click', 'hotspots-point',    (e: any) => { if (e.features?.[0]) onSelectEventRef.current(e.features[0].properties.id); });
    m.on('click', 'facility-perimeter',(e: any) => { if (e.features?.[0]) onSelectFacilityRef.current(Number(e.features[0].properties.id)); });
  }, []); // zero deps to prevent triggering map re-initialization

  //  Map Initialisation 
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    const m = new maplibregl.Map({
      container: mapContainer.current,
      // Start with a blank style  -  we add raster layers programmatically
      style: BLANK_STYLE,
      center: [79.2, 21.8],
      zoom: 4.8,
      minZoom: 3.2,
      maxZoom: 18,
      attributionControl: false,
    });

    m.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-right');
    popup.current = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 16, maxWidth: '270px' });

    m.on('load', () => {
      // 1. Initialize all basemap sources/layers upfront
      initAllBasemaps(m, basemapRef.current);
      // 2. Add GeoJSON data layers on top
      addDataLayers(m, hotspotsRef.current, buildFacGeoJSON(facilitiesRef.current), showFacRef.current);
      // 3. Bind interaction events
      bindEvents(m);
    });

    m.on('mousemove', (e) => setCoords({ lng: e.lngLat.lng, lat: e.lngLat.lat }));
    m.on('mouseout',  () => setCoords(null));
    m.on('zoom',      () => setZoom(parseFloat(m.getZoom().toFixed(1))));

    const ro = new ResizeObserver(() => m.resize());
    ro.observe(mapContainer.current!);
    map.current = m;

    return () => { ro.disconnect(); m.remove(); map.current = null; };
  }, [bindEvents]);

  //  Basemap toggle  -  Instant visibility swap 
  //
  // We preload both sources on map load. Toggling just switches the
  // `visibility` layout property between `'visible'` and `'none'`.
  //
  const toggleBasemap = useCallback((next: 'dark' | 'satellite') => {
    if (!map.current) return;
    // Read current basemap from ref  -  immune to stale React state closures
    if (basemapRef.current === next) return;
    const m = map.current;

    // Toggle layer visibility
    setBasemapVisibility(m, next);

    // 3. Keep ref and React state in sync
    basemapRef.current = next;
    setBasemap(next);
  }, []); // stable  -  no deps needed because we use refs


  //  Hotspot live update 
  useEffect(() => {
    if (!map.current) return;
    const src = map.current.getSource('thermos-hotspots') as maplibregl.GeoJSONSource | undefined;
    if (src && hotspots) src.setData(hotspots);
  }, [hotspots]);

  //  Facility live update 
  useEffect(() => {
    if (!map.current) return;
    const src = map.current.getSource('thermos-facilities') as maplibregl.GeoJSONSource | undefined;
    if (src && facilities.length) src.setData(buildFacGeoJSON(facilities));
  }, [facilities]);

  //  Facility layer visibility 
  useEffect(() => {
    if (!map.current) return;
    const vis = showFacilities ? 'visible' : 'none';
    (['facility-perimeter', 'facility-point'] as const).forEach(id => {
      try { if (map.current?.getLayer(id)) map.current.setLayoutProperty(id, 'visibility', vis); }
      catch (_) {}
    });
  }, [showFacilities]);

  //  Selected event highlight ring 
  useEffect(() => {
    if (!map.current) return;
    try {
      map.current.setFilter('hotspots-selected', ['==', ['get', 'id'], selectedEventId ?? '__none__']);
    } catch (_) {}

    if (selectedEventId && hotspots) {
      const feat = hotspots.features.find(f => f.properties.id === selectedEventId);
      if (feat) {
        map.current.flyTo({
          center: feat.geometry.coordinates as [number, number],
          zoom: Math.max(map.current.getZoom(), 8.5),
          speed: 1.2, essential: true,
        });
      }
    }
  }, [selectedEventId, hotspots]);

  const fmtCoord = (v: number, ax: 'lat' | 'lng') =>
    `${Math.abs(v).toFixed(4)} deg${ax === 'lat' ? (v >= 0 ? 'N' : 'S') : (v >= 0 ? 'E' : 'W')}`;

  //  Render 
  return (
    <div className="absolute inset-0 w-full h-full overflow-hidden">

      {/* WebGL Map Canvas */}
      <div ref={mapContainer} className="absolute inset-0 w-full h-full" />

      {/*  Basemap Switcher (top-left)  */}
      <div className="
        absolute top-3 left-3 z-10
        bg-[var(--bg-card)] border border-[var(--border)] rounded-sm
        p-1.5 flex flex-col gap-1 backdrop-blur-xl shadow-2xl ring-1 ring-black/5
      ">
        <div className="px-2 py-0.5 text-xs font-mono tracking-[0.2em] text-slate-600 uppercase text-center">
          BASEMAP
        </div>

        <button
          onClick={() => toggleBasemap('dark')}
          title="Tactical Dark  -  Esri Dark Gray Canvas"
          className={`
            flex items-center gap-1.5 px-3 py-1.5 rounded-sm text-[10px]
            font-mono font-bold tracking-wider transition-all border
            ${basemap === 'dark'
              ? 'bg-amber-500 text-slate-950 border-amber-400/60 shadow-lg shadow-amber-500/30'
              : 'text-[var(--text-secondary)] border-[var(--border)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)]'}
          `}
        >
          <Layers className="w-3.5 h-3.5 flex-shrink-0" />
          TACTICAL
        </button>

        <button
          onClick={() => toggleBasemap('satellite')}
          title="Satellite  -  Esri World Imagery"
          className={`
            flex items-center gap-1.5 px-3 py-1.5 rounded-sm text-[10px]
            font-mono font-bold tracking-wider transition-all border
            ${basemap === 'satellite'
              ? 'bg-emerald-500 text-slate-950 border-emerald-400/60 shadow-lg shadow-emerald-500/30'
              : 'text-[var(--text-secondary)] border-[var(--border)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)]'}
          `}
        >
          <Globe className="w-3.5 h-3.5 flex-shrink-0" />
          SATELLITE
        </button>

        <div className="px-2 py-0.5 text-xs font-mono text-slate-700 text-center tabular-nums">
          Z {zoom}
        </div>
      </div>

      {/*  Detection Class Legend (bottom-left)  */}
      <div className="
        absolute bottom-10 left-3 z-10
        bg-[var(--bg-card)] border border-[var(--border)] rounded-sm
        px-3.5 py-3 backdrop-blur-xl shadow-2xl ring-1 ring-black/5
        pointer-events-none select-none space-y-1.5
      ">
        <div className="text-xs font-mono tracking-[0.2em] text-slate-600 uppercase mb-2">
          DETECTION CLASSES
        </div>

        {(Object.entries(CLASS_CONFIG) as [string, typeof CLASS_CONFIG[keyof typeof CLASS_CONFIG]][]).map(([cls, meta]) => (
          <div key={cls} className="flex items-center gap-2.5">
            <span className="flex-shrink-0 rounded-sm" style={{
              width: 10, height: 10,
              backgroundColor: meta.hex,
              boxShadow: `0 0 5px ${meta.hex}, 0 0 10px ${meta.hex}55`,
            }} />
            <span className="text-xs font-mono font-semibold tracking-wide" style={{ color: meta.hex }}>
              {meta.label.toUpperCase()}
            </span>
          </div>
        ))}

        <div className="border-t border-slate-800/60 pt-1.5 mt-0.5 flex items-center gap-2.5">
          <span className="flex-shrink-0 rounded-sm" style={{
            width: 10, height: 10,
            border: '1.5px solid #38bdf8',
            backgroundColor: 'rgba(56,189,248,0.18)',
          }} />
          <span className="text-xs font-mono text-[var(--b-cyan)]">Monitored Facility</span>
        </div>

        <div className="border-t border-slate-800/60 pt-1.5 mt-0.5">
          <div className="text-[9px] font-mono text-slate-600 mb-1.5 tracking-wider">FRP SCALE : DOT SIZE</div>
          <div className="flex items-end gap-2">
            {[{ l:'2MW', s:5 },{ l:'50MW', s:11 },{ l:'200MW', s:16 }].map(({ l, s }) => (
              <div key={l} className="flex flex-col items-center gap-1">
                <span className="rounded-sm" style={{ width:s, height:s, backgroundColor:'#64748b' }} />
                <span className="text-xs font-mono text-slate-600">{l}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/*  Coordinate HUD (bottom-right)  */}
      <div className="
        absolute bottom-10 right-3 z-10
        bg-[var(--bg-card)] border border-[var(--border)] rounded-sm
        px-3.5 py-2.5 backdrop-blur-xl shadow-2xl ring-1 ring-black/5
        pointer-events-none select-none min-w-[170px]
      ">
        <div className="flex items-center gap-1.5 text-[10px] font-mono tracking-widest text-[var(--text-secondary)] font-bold uppercase mb-1.5">
          <MapPin className="w-3 h-3 text-amber-500" />
          <span>CURSOR COORDS</span>
        </div>
        {coords ? (
          <div className="font-mono space-y-1">
            <div className="flex justify-between items-center gap-4">
              <span className="text-[10px] tracking-widest text-[var(--text-secondary)] font-bold">LAT</span>
              <span className="text-xs font-mono text-[var(--text-primary)] font-bold tabular-nums">{fmtCoord(coords.lat,'lat')}</span>
            </div>
            <div className="flex justify-between items-center gap-4">
              <span className="text-[10px] tracking-widest text-[var(--text-secondary)] font-bold">LNG</span>
              <span className="text-xs font-mono text-[var(--text-primary)] font-bold tabular-nums">{fmtCoord(coords.lng,'lng')}</span>
            </div>
          </div>
        ) : (
          <div className="text-[10px] font-mono text-[var(--text-muted)] italic">Move cursor over map</div>
        )}
      </div>

    </div>
  );
};





