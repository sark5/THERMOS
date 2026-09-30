import type {
  HotspotCollection,
  EventDetails,
  SourceFingerprint,
  Facility,
  FacilityProfile,
  AlertItem,
  AnalyticsSummary,
  InvestigationResponse
} from '../types';

const API_BASE = '/api/v1/intelligence';

export async function fetchHotspots(params?: {
  limit?: number;
  class_filter?: string;
  min_frp?: number;
  risk_filter?: string;
}): Promise<HotspotCollection> {
  const query = new URLSearchParams();
  if (params?.limit) query.set('limit', String(params.limit));
  if (params?.class_filter && params.class_filter !== 'ALL') query.set('class_filter', params.class_filter);
  if (params?.min_frp) query.set('min_frp', String(params.min_frp));
  if (params?.risk_filter && params.risk_filter !== 'ALL') query.set('risk_filter', params.risk_filter);

  const res = await fetch(`${API_BASE}/hotspots?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch thermal hotspots');
  return res.json();
}

export async function fetchEventDetails(eventId: string): Promise<EventDetails> {
  const res = await fetch(`${API_BASE}/events/${eventId}/details`);
  if (!res.ok) throw new Error(`Failed to fetch details for event ${eventId}`);
  return res.json();
}

export async function fetchSourceFingerprint(sourceId: string): Promise<SourceFingerprint> {
  const res = await fetch(`${API_BASE}/sources/${sourceId}/fingerprint`);
  if (!res.ok) throw new Error(`Failed to fetch fingerprint for source ${sourceId}`);
  return res.json();
}

export async function fetchFacilities(type?: string): Promise<Facility[]> {
  const query = new URLSearchParams();
  if (type && type !== 'ALL') query.set('facility_type', type);

  const res = await fetch(`${API_BASE}/facilities?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch facility records');
  return res.json();
}

export async function fetchFacilityProfile(facilityId: number): Promise<FacilityProfile> {
  const res = await fetch(`${API_BASE}/facilities/${facilityId}/profile`);
  if (!res.ok) throw new Error(`Failed to fetch profile for facility ${facilityId}`);
  return res.json();
}

export async function fetchLiveAlerts(): Promise<AlertItem[]> {
  const res = await fetch(`${API_BASE}/alerts/live`);
  if (!res.ok) throw new Error('Failed to fetch live alerts');
  return res.json();
}

export async function fetchAnalyticsSummary(): Promise<AnalyticsSummary> {
  const res = await fetch(`${API_BASE}/analytics/summary`);
  if (!res.ok) throw new Error('Failed to fetch analytics summary');
  return res.json();
}

export async function submitInvestigation(query: string, eventId?: string): Promise<InvestigationResponse> {
  const res = await fetch(`${API_BASE}/investigate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, event_id: eventId })
  });
  if (!res.ok) throw new Error('Failed to run AI investigation');
  return res.json();
}

export async function fetchReviewQueue(status: string = 'PENDING'): Promise<{ total: number; pending: number; items: any[] }> {
  const res = await fetch(`/api/v1/review/queue?status=${status}`);
  if (!res.ok) throw new Error('Failed to fetch review queue');
  return res.json();
}

export async function submitReview(payload: {
  event_id: string;
  action: string;
  assigned_label?: string;
  reviewer?: string;
  notes?: string;
}): Promise<any> {
  const res = await fetch('/api/v1/review/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to submit review');
  return res.json();
}

export async function fetchLeakageAudit(): Promise<any> {
  const res = await fetch(`${API_BASE}/evaluation/leakage-audit`);
  if (!res.ok) throw new Error('Failed to fetch leakage audit data');
  return res.json();
}

//  Closed-Loop Emergency Response API 

const RESPONSE_BASE = '/api/v1/response';

export async function fetchResponseIncidents(): Promise<{ incidents: any[]; total: number; active_emergency_count: number }> {
  const res = await fetch(`${RESPONSE_BASE}/incidents`);
  if (!res.ok) throw new Error('Failed to fetch emergency response incidents');
  return res.json();
}

export async function fetchPreArrivalPacket(incidentId: string): Promise<any> {
  const res = await fetch(`${RESPONSE_BASE}/incidents/${incidentId}/pre-arrival-packet`);
  if (!res.ok) throw new Error(`Failed to fetch pre-arrival packet for ${incidentId}`);
  return res.json();
}

export async function qualifyEventForResponse(payload: any): Promise<any> {
  const res = await fetch(`${RESPONSE_BASE}/qualify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to evaluate qualification gate');
  return res.json();
}

export async function acknowledgeResponseAlert(incidentId: string, responderName?: string): Promise<any> {
  const res = await fetch(`${RESPONSE_BASE}/incidents/${incidentId}/acknowledge`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ responder_name: responderName || 'Duty Dispatch Officer' }),
  });
  if (!res.ok) throw new Error(`Failed to acknowledge incident ${incidentId}`);
  return res.json();
}

export async function markUnitResponding(incidentId: string, callsign?: string): Promise<any> {
  const res = await fetch(`${RESPONSE_BASE}/incidents/${incidentId}/respond`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ unit_callsign: callsign || 'Heavy Pumper-01' }),
  });
  if (!res.ok) throw new Error(`Failed to mark incident ${incidentId} as responding`);
  return res.json();
}

export async function escalateResponseIncident(incidentId: string): Promise<any> {
  const res = await fetch(`${RESPONSE_BASE}/incidents/${incidentId}/escalate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) throw new Error(`Failed to escalate incident ${incidentId}`);
  return res.json();
}

export async function resolveResponseIncident(incidentId: string, notes?: string): Promise<any> {
  const res = await fetch(`${RESPONSE_BASE}/incidents/${incidentId}/resolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resolution_notes: notes || 'Thermal emission successfully contained.' }),
  });
  if (!res.ok) throw new Error(`Failed to resolve incident ${incidentId}`);
  return res.json();
}

export async function fetchPostIncidentReport(incidentId: string): Promise<any> {
  const res = await fetch(`${RESPONSE_BASE}/incidents/${incidentId}/post-incident-report`);
  if (!res.ok) throw new Error(`Failed to fetch post incident report for ${incidentId}`);
  return res.json();
}

export async function fetchResponseReadiness(): Promise<any> {
  const res = await fetch(`${RESPONSE_BASE}/readiness`);
  if (!res.ok) throw new Error('Failed to fetch response readiness metrics');
  return res.json();
}


