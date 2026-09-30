import React, { useState, useEffect } from 'react';
import type {
  ThermalClass,
  RiskBand,
  HotspotCollection,
  Facility,
  AnalyticsSummary,
  EventDetails,
} from './types';
import {
  fetchHotspots,
  fetchFacilities,
  fetchAnalyticsSummary,
  fetchEventDetails,
} from './services/api';
import { Header } from './components/Header';
import { FilterBar } from './components/FilterBar';
import { MapCanvas } from './components/MapCanvas';
import { EventInspector } from './components/EventInspector';
import { FingerprintModal } from './components/FingerprintModal';
import { FacilityTwinModal } from './components/FacilityTwinModal';
import { InvestigationModal } from './components/InvestigationModal';
import { AlertsDrawer } from './components/AlertsDrawer';
import { AnalyticsModal } from './components/AnalyticsModal';
import { FacilitiesListModal } from './components/FacilitiesListModal';
import { TimelinePlayback } from './components/TimelinePlayback';
import { ReviewModal } from './components/ReviewModal';
import { ResponseCenterModal } from './components/ResponseCenterModal';

export const App: React.FC = () => {
  //  Theme 
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const toggleTheme = () => setTheme(t => t === 'light' ? 'dark' : 'light');

  // Apply data-theme attribute to document root
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  //  Application State 
  const [hotspots, setHotspots] = useState<HotspotCollection | null>(null);
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);

  // Filters
  const [selectedClass, setSelectedClass] = useState<ThermalClass | 'ALL'>('ALL');
  const [selectedRisk, setSelectedRisk] = useState<RiskBand | 'ALL'>('ALL');
  const [minFrp, setMinFrp] = useState<number>(0);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loadingHotspots, setLoadingHotspots] = useState<boolean>(true);

  // Inspector & Modals
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [eventDetails, setEventDetails] = useState<EventDetails | null>(null);
  const [loadingDetails, setLoadingDetails] = useState<boolean>(false);

  const [selectedSourceId, setSelectedSourceId] = useState<string | null>(null);
  const [selectedFacilityId, setSelectedFacilityId] = useState<number | null>(null);
  const [activeView, setActiveView] = useState<'map' | 'alerts' | 'analytics' | 'investigate'>('map');
  const [showFacilitiesList, setShowFacilitiesList] = useState<boolean>(false);
  const [showFacilitiesLayer, setShowFacilitiesLayer] = useState<boolean>(true);
  const [showReviewQueue, setShowReviewQueue] = useState<boolean>(false);
  const [showResponseCenter, setShowResponseCenter] = useState<boolean>(false);
  const [responseIncidentId, setResponseIncidentId] = useState<string | null>(null);
  const [targetLocation, setTargetLocation] = useState<[number, number] | null>(null);

  // Initial Data Ingestion
  useEffect(() => {
    fetchAnalyticsSummary()
      .then(res => setAnalytics(res))
      .catch(err => console.error('Failed to load analytics:', err));

    fetchFacilities()
      .then(res => setFacilities(res))
      .catch(err => console.error('Failed to load facilities:', err));
  }, []);

  // Hotspots Ingestion
  useEffect(() => {
    setLoadingHotspots(true);
    fetchHotspots({
      limit: 1500,
      class_filter: selectedClass,
      min_frp: minFrp,
      risk_filter: selectedRisk,
    })
      .then(res => setHotspots(res))
      .catch(err => console.error('Failed to load hotspots:', err))
      .finally(() => setLoadingHotspots(false));
  }, [selectedClass, selectedRisk, minFrp]);

  // Event Details Ingestion
  useEffect(() => {
    if (!selectedEventId) { setEventDetails(null); return; }
    setLoadingDetails(true);
    fetchEventDetails(selectedEventId)
      .then(res => setEventDetails(res))
      .catch(err => console.error('Failed to load event details:', err))
      .finally(() => setLoadingDetails(false));
  }, [selectedEventId]);

  // Filtered hotspots by search query
  const displayedHotspots = React.useMemo(() => {
    if (!hotspots) return null;
    if (!searchQuery.trim()) return hotspots;
    const q = searchQuery.toLowerCase();
    const filteredFeatures = hotspots.features.filter(f =>
      f.properties.id.toLowerCase().includes(q) ||
      f.properties.facility_name.toLowerCase().includes(q) ||
      f.properties.source_id.toLowerCase().includes(q)
    );
    return { ...hotspots, features: filteredFeatures, total: filteredFeatures.length };
  }, [hotspots, searchQuery]);

  const isDark = theme === 'dark';

  return (
    <div
      data-theme={theme}
      className={`flex flex-col w-screen h-screen overflow-hidden font-sans transition-colors duration-200 ${
        isDark ? 'bg-slate-950 text-slate-100' : 'bg-slate-50 text-slate-900'
      }`}
    >
      {/* Top Telemetry & Command Bar */}
      <Header
        analytics={analytics}
        activeView={activeView}
        setActiveView={setActiveView}
        onOpenFacilities={() => setShowFacilitiesList(true)}
        showFacilitiesLayer={showFacilitiesLayer}
        onToggleFacilitiesLayer={() => setShowFacilitiesLayer(!showFacilitiesLayer)}
        onOpenReviewQueue={() => setShowReviewQueue(true)}
        onOpenResponseCenter={() => {
          setResponseIncidentId(null);
          setShowResponseCenter(true);
        }}
        theme={theme}
        onToggleTheme={toggleTheme}
      />

      {/* Class & Filter Bar */}
      <FilterBar
        selectedClass={selectedClass}
        setSelectedClass={setSelectedClass}
        selectedRisk={selectedRisk}
        setSelectedRisk={setSelectedRisk}
        minFrp={minFrp}
        setMinFrp={setMinFrp}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        totalEvents={displayedHotspots?.features.length || 0}
        loading={loadingHotspots}
        theme={theme}
      />

      {/* Map Canvas Workspace */}
      <main className="relative flex-1 w-full min-h-0 overflow-hidden">
        <MapCanvas
          hotspots={displayedHotspots}
          facilities={facilities}
          selectedEventId={selectedEventId}
          onSelectEvent={(id) => setSelectedEventId(id)}
          onSelectFacility={(fid) => setSelectedFacilityId(fid)}
          showFacilities={showFacilitiesLayer}
          targetLocation={targetLocation}
          theme={theme}
        />

        {/* Slide-Over Event Inspector Panel */}
        <EventInspector
          details={eventDetails}
          loading={loadingDetails}
          onClose={() => setSelectedEventId(null)}
          onOpenFingerprint={(srcId) => setSelectedSourceId(srcId)}
          onOpenFacility={(facName) => {
            const match = facilities.find(f => f.name.toLowerCase() === facName.toLowerCase());
            if (match) setSelectedFacilityId(match.id);
            else setSelectedFacilityId(1);
          }}
          onInvestigate={(id) => {
            setSelectedEventId(id);
            setActiveView('investigate');
          }}
          onOpenResponseCenter={(evId) => {
            setResponseIncidentId(evId);
            setShowResponseCenter(true);
          }}
          theme={theme}
        />

        {/* Timeline Playback Slider */}
        <TimelinePlayback
          onDateChange={(dt) => { console.log('Scrubbing timeline to:', dt); }}
          theme={theme}
        />
      </main>

      {/* Thermal Digital Fingerprint Modal */}
      {selectedSourceId && (
        <FingerprintModal
          sourceId={selectedSourceId}
          onClose={() => setSelectedSourceId(null)}
          theme={theme}
        />
      )}

      {/* Facility Digital Twin Modal */}
      {selectedFacilityId !== null && (
        <FacilityTwinModal
          facilityId={selectedFacilityId}
          onClose={() => setSelectedFacilityId(null)}
          theme={theme}
        />
      )}

      {/* Live Alerts Drawer */}
      {activeView === 'alerts' && (
        <AlertsDrawer
          onClose={() => setActiveView('map')}
          onLocateEvent={(coords) => {
            setTargetLocation(coords);
            setActiveView('map');
          }}
          onInvestigateEvent={(evId) => {
            setSelectedEventId(evId);
            setActiveView('investigate');
          }}
          theme={theme}
        />
      )}

      {/* Subcontinental Analytics Modal */}
      {activeView === 'analytics' && (
        <AnalyticsModal onClose={() => setActiveView('map')} theme={theme} />
      )}

      {/* AI Investigation Assistant Modal */}
      {activeView === 'investigate' && (
        <InvestigationModal
          initialEventId={selectedEventId}
          onClose={() => setActiveView('map')}
          theme={theme}
        />
      )}

      {/* 643 Facilities Directory Modal */}
      {showFacilitiesList && (
        <FacilitiesListModal
          facilities={facilities}
          onClose={() => setShowFacilitiesList(false)}
          onSelectFacility={(fid) => setSelectedFacilityId(fid)}
          onLocateFacility={(coords) => {
            setTargetLocation(coords);
            setShowFacilitiesList(false);
          }}
          theme={theme}
        />
      )}

      {/* Human-in-the-Loop HITL Audit Queue */}
      {showReviewQueue && (
        <ReviewModal onClose={() => setShowReviewQueue(false)} theme={theme} />
      )}

      {/* Closed-Loop Emergency Response Center & ERSS-112 CAD Integration */}
      <ResponseCenterModal
        isOpen={showResponseCenter}
        onClose={() => setShowResponseCenter(false)}
        selectedIncidentId={responseIncidentId}
        theme={theme}
      />
    </div>
  );
};

export default App;

