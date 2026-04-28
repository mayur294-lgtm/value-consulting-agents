/**
 * REST API Client — fetches data from the SQLite-backed API proxy
 *
 * Features:
 *   - Automatic timeout with clear error messages
 *   - Retry with exponential backoff for transient failures (network, 5xx, 429)
 *   - Caller-initiated abort support (e.g., search cancellation)
 */
const API_BASE = import.meta.env.VITE_API_BASE || '';
const enc = encodeURIComponent; // shorthand for URL encoding

const DEFAULT_TIMEOUT = 15000; // 15s for data reads
const AI_TIMEOUT = 150000;    // 150s for AI-powered endpoints
const MAX_RETRIES = 2;        // Up to 2 retries (3 total attempts)
const RETRY_BASE_MS = 1000;   // 1s, 2s exponential backoff

/** Check if an error is retryable (network failure, server error, rate limit) */
function isRetryable(err, status) {
  if (err.name === 'TypeError') return true;           // Network failure (fetch throws TypeError)
  if (status >= 500 && status < 600) return true;      // Server errors
  if (status === 429) return true;                     // Rate limited
  return false;
}

async function request(path, options = {}) {
  const { signal: externalSignal, timeout, retries = MAX_RETRIES, ...rest } = options;

  for (let attempt = 0; attempt <= retries; attempt++) {
    const controller = new AbortController();
    const timeoutMs = timeout || DEFAULT_TIMEOUT;
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    // Link caller's abort signal
    if (externalSignal) {
      if (externalSignal.aborted) { clearTimeout(timer); throw new DOMException('Aborted', 'AbortError'); }
      externalSignal.addEventListener('abort', () => controller.abort(), { once: true });
    }

    try {
      const res = await fetch(`${API_BASE}${path}`, {
        headers: { 'Content-Type': 'application/json', ...rest.headers },
        signal: controller.signal,
        ...rest,
      });
      clearTimeout(timer);

      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
        const error = new Error(err.error || `Request failed: ${res.status}`);
        error.status = res.status;

        // Retry on transient server errors
        if (attempt < retries && isRetryable(error, res.status)) {
          const delay = RETRY_BASE_MS * Math.pow(2, attempt);
          console.warn(`[API] ${path} failed (${res.status}), retrying in ${delay}ms... (${attempt + 1}/${retries})`);
          await new Promise(r => setTimeout(r, delay));
          continue;
        }
        throw error;
      }
      return res.json();
    } catch (err) {
      clearTimeout(timer);

      // Never retry caller-initiated aborts
      if (err.name === 'AbortError' && externalSignal?.aborted) throw err;

      // Timeout — clear message
      if (err.name === 'AbortError') {
        throw new Error(`Request timed out after ${timeoutMs / 1000}s: ${path}`);
      }

      // Retry on network errors (TypeError from fetch)
      if (attempt < retries && isRetryable(err)) {
        const delay = RETRY_BASE_MS * Math.pow(2, attempt);
        console.warn(`[API] ${path} network error, retrying in ${delay}ms... (${attempt + 1}/${retries})`);
        await new Promise(r => setTimeout(r, delay));
        continue;
      }

      throw err;
    }
  }
}

// ── Banks ──
export const fetchBanks = () => request('/api/banks');
export const fetchBank = (key) => request(`/api/banks/${encodeURIComponent(key)}`);
export const createBank = (data) => request('/api/banks', { method: 'POST', body: JSON.stringify(data) });
export const updateBank = (key, data) => request(`/api/banks/${encodeURIComponent(key)}`, { method: 'PUT', body: JSON.stringify(data) });
export const deleteBank = (key) => request(`/api/banks/${encodeURIComponent(key)}`, { method: 'DELETE' });

// ── Bank sub-resources ──
export const fetchBankQualification = (key) => request(`/api/banks/${encodeURIComponent(key)}/qualification`);
export const updateBankQualification = (key, data) => request(`/api/banks/${encodeURIComponent(key)}/qualification`, { method: 'PUT', body: JSON.stringify(data) });
export const fetchBankCx = (key) => request(`/api/banks/${encodeURIComponent(key)}/cx`);
export const fetchBankCompetition = (key) => request(`/api/banks/${encodeURIComponent(key)}/competition`);
export const fetchBankValueSelling = (key) => request(`/api/banks/${encodeURIComponent(key)}/value-selling`);
export const fetchBankSources = (key) => request(`/api/banks/${encodeURIComponent(key)}/sources`);
export const fetchBankRelationship = (key) => request(`/api/banks/${encodeURIComponent(key)}/relationships`);

// ── Markets ──
export const fetchMarkets = () => request('/api/markets');
export const fetchMarket = (key) => request(`/api/markets/${encodeURIComponent(key)}`);
export const fetchMarketBanks = (key) => request(`/api/markets/${encodeURIComponent(key)}/banks`);

// ── Countries ──
export const fetchCountries = () => request('/api/countries');
export const fetchCountry = (name) => request(`/api/countries/${encodeURIComponent(name)}`);
export const fetchCountryBanks = (name) => request(`/api/countries/${encodeURIComponent(name)}/banks`);
export const refreshCountryIntelligence = (name, data) =>
  request(`/api/countries/${encodeURIComponent(name)}/refresh-intelligence`, { method: 'POST', body: JSON.stringify(data), timeout: AI_TIMEOUT });

// ── Stats, Search & Signals ──
export const fetchStats = () => request('/api/stats');
export const fetchSignals = (limit = 8, options = {}) => {
  const params = new URLSearchParams({ limit: String(limit) });
  if (options.source) params.set('source', options.source);
  if (options.bankKey) params.set('bank_key', options.bankKey);
  if (options.type) params.set('type', options.type);
  if (options.minScore) params.set('min_score', String(options.minScore));
  return request(`/api/signals?${params}`);
};
export const refreshSignals = () => request('/api/signals/refresh', { method: 'POST', timeout: 5000 });
export const fetchSignalStatus = () => request('/api/signals/status');
export const searchAll = (query, options) => request(`/api/search?q=${encodeURIComponent(query)}`, options);

// ── Ingestion Pipeline ──
export const fetchIngestionLog = ({ bankKey, source, limit = 50 } = {}) => {
  const params = new URLSearchParams();
  if (bankKey) params.set('bank_key', bankKey);
  if (source) params.set('source', source);
  if (limit) params.set('limit', String(limit));
  return request(`/api/ingestion-log?${params}`);
};

export const fetchBankAiAnalyses = (key) => request(`/api/banks/${encodeURIComponent(key)}/ai-analyses`);

// ── Meeting Research (AI-powered — longer timeouts) ──
export const checkResearchStatus = () => request('/api/research/status');
export const researchPerson = (data) => request('/api/research/person', { method: 'POST', body: JSON.stringify(data), timeout: AI_TIMEOUT });
export const enrichContext = (data) => request('/api/research/context', { method: 'POST', body: JSON.stringify(data), timeout: AI_TIMEOUT });
export const generateMeetingPrep = (data) => request('/api/research/meeting-prep', { method: 'POST', body: JSON.stringify(data), timeout: AI_TIMEOUT });
export const generateEngagementPlan = (data) => request('/api/research/engagement-plan', { method: 'POST', body: JSON.stringify(data), timeout: AI_TIMEOUT });
export const generateAccountPlan = (data) => request('/api/research/account-plan', { method: 'POST', body: JSON.stringify(data), timeout: AI_TIMEOUT });
export const generateExecutiveBrief = (data) => request('/api/research/executive-brief', { method: 'POST', body: JSON.stringify(data), timeout: AI_TIMEOUT });
export const generateAccountPlanDoc = (data) => request('/api/generate-account-plan', { method: 'POST', body: JSON.stringify(data), timeout: AI_TIMEOUT });
export const getCachedAccountPlan = (bankKey) => request(`/api/account-plan/${encodeURIComponent(bankKey)}`);
export const generateEmailDraft = (data) => request('/api/research/email-draft', { method: 'POST', body: JSON.stringify(data), timeout: AI_TIMEOUT });

// ── Pipeline Settings / Bank Status ──
export const getPipelineSettings = () => request('/api/pipeline-settings');
export const getBankStatus = (bankKey) => request(`/api/banks/${encodeURIComponent(bankKey)}/status`);
export const updateBankStatus = (bankKey, { excluded, status, disqualify_reason } = {}) =>
  request(`/api/pipeline-settings/${encodeURIComponent(bankKey)}`, { method: 'PUT', body: JSON.stringify({ excluded, status, disqualify_reason }) });

// ── Intelligence Layer: Plays ──
export const createPlay = (dealId, data) => request(`/api/deals/${enc(dealId)}/plays`, { method: 'POST', body: JSON.stringify(data) });
export const getPlays = (dealId) => request(`/api/deals/${enc(dealId)}/plays`);
export const getPlayDetail = (dealId, playId) => request(`/api/deals/${enc(dealId)}/plays/${enc(playId)}`);
export const updatePlay = (dealId, playId, data) => request(`/api/deals/${enc(dealId)}/plays/${enc(playId)}`, { method: 'PUT', body: JSON.stringify(data) });
export const generatePlayOutputs = (dealId, playId) => request(`/api/deals/${enc(dealId)}/plays/${enc(playId)}/generate`, { method: 'POST', timeout: AI_TIMEOUT });
export const regenerateStalePlays = (dealId) => request(`/api/deals/${enc(dealId)}/plays/regenerate-stale`, { method: 'POST' });

// ── Intelligence Layer: Play Outputs ──
export const getPlayOutputs = (playId) => request(`/api/plays/${enc(playId)}/outputs`);
export const updatePlayOutput = (playId, outputId, data) => request(`/api/plays/${enc(playId)}/outputs/${enc(outputId)}`, { method: 'PUT', body: JSON.stringify(data) });
export const submitOutputFeedback = (playId, outputId, data) => request(`/api/plays/${enc(playId)}/outputs/${enc(outputId)}/feedback`, { method: 'POST', body: JSON.stringify(data) });

// ── Intelligence Layer: Signals ──
export const createSignal = (dealId, data) => request(`/api/deals/${enc(dealId)}/signals`, { method: 'POST', body: JSON.stringify(data) });
export const getSignals = (dealId, params = {}) => {
  const qs = Object.entries(params).filter(([,v]) => v).map(([k,v]) => `${k}=${encodeURIComponent(v)}`).join('&');
  return request(`/api/deals/${enc(dealId)}/signals${qs ? '?' + qs : ''}`);
};
export const updateSignal = (dealId, signalId, data) => request(`/api/deals/${enc(dealId)}/signals/${enc(signalId)}`, { method: 'PUT', body: JSON.stringify(data) });
export const getSignalSummary = (dealId) => request(`/api/deals/${enc(dealId)}/signals/summary`);
// Refresh signals for one bank — runs harvest + classify + route end-to-end. ~3-5 min.
export const refreshDealSignals = (dealId) => request(`/api/deals/${enc(dealId)}/signals/refresh`, { method: 'POST', timeout: 600000 });
// When was this bank's signal feed last refreshed? Used for the "Last updated X ago" badge.
export const getSignalFreshness = (dealId) => request(`/api/deals/${enc(dealId)}/signals/freshness`);
// Signals mentioning a specific person — for the bidirectional cross-link.
export const getSignalsForPerson = (bankKey, personId) => request(`/api/banks/${enc(bankKey)}/persons/${enc(personId)}/signals`);
// Manual signal submission (Stage 4C) — paste a URL/LinkedIn link, classify on backend.
export const submitManualSignal = (dealId, payload) => request(`/api/deals/${enc(dealId)}/signals/manual`, { method: 'POST', body: JSON.stringify(payload), timeout: 60000 });
// Live OG-fetch for the submission modal — pastes URL, returns title + description.
export const fetchOpenGraph = (url) => request('/api/og-fetch', { method: 'POST', body: JSON.stringify({ url }), timeout: 20000 });

// ── Pulse (Strategic Repositioning Sprint 1) ──
export const getReviewPeriods = () => request('/api/review-periods');
export const getBankPulses = (bankKey) => request(`/api/banks/${enc(bankKey)}/pulses`);
export const generatePulse = (bankKey, periodId = '2026-Q2') => request(`/api/banks/${enc(bankKey)}/pulses?period=${enc(periodId)}`, { method: 'POST', timeout: 60000 });
export const getPulse = (pulseId) => request(`/api/pulses/${enc(pulseId)}`);
export const overrideCell = (pulseId, payload) => request(`/api/pulses/${enc(pulseId)}/cells`, { method: 'PUT', body: JSON.stringify(payload) });
export const confirmPulse = (pulseId, aeId) => request(`/api/pulses/${enc(pulseId)}/confirm`, { method: 'POST', body: JSON.stringify({ ae_id: aeId }) });

// ── Intelligence Layer: Deal Twin ──
export const getDealTwin = (dealId) => request(`/api/deals/${enc(dealId)}/twin`);
export const recalculateDealTwin = (dealId) => request(`/api/deals/${enc(dealId)}/twin/recalculate`, { method: 'POST', timeout: AI_TIMEOUT });
export const getDealTwinHistory = (dealId) => request(`/api/deals/${enc(dealId)}/twin/history`);

// ── Strategic Account Plan: Person CRUD (stakeholder map editing) ──
export const createPerson = (bankKey, data) =>
  request(`/api/banks/${enc(bankKey)}/persons`, { method: 'POST', body: JSON.stringify(data) });
export const updatePerson = (bankKey, personId, data) =>
  request(`/api/banks/${enc(bankKey)}/persons/${enc(personId)}`, { method: 'PUT', body: JSON.stringify(data) });
export const deletePerson = (bankKey, personId) =>
  request(`/api/banks/${enc(bankKey)}/persons/${enc(personId)}`, { method: 'DELETE' });
export const updatePersonPosition = (bankKey, personId, data) =>
  request(`/api/banks/${enc(bankKey)}/persons/${enc(personId)}/position`, { method: 'PATCH', body: JSON.stringify(data) });

// ── Strategic Account Plan: AI-generated snapshot + objectives ──
export const generateStrategicSnapshot = (bankKey) =>
  request(`/api/banks/${enc(bankKey)}/strategic-snapshot`, { method: 'POST', timeout: AI_TIMEOUT });
export const generateStrategicObjectives = (bankKey) =>
  request(`/api/banks/${enc(bankKey)}/strategic-objectives`, { method: 'POST', timeout: AI_TIMEOUT });

// ── Conversation Intelligence ──
export const getConversationIntelligence = () => request('/api/conversation-intelligence');

// ── Competitive Intelligence ──
export const generateBattlecard = (data) => request('/api/research/battlecard', { method: 'POST', body: JSON.stringify(data), timeout: AI_TIMEOUT });
export const getCompetitiveLandscape = () => request('/api/competitive-landscape');

// ── Meeting Deck ──
export const generateMeetingDeck = (data) => request('/api/research/meeting-deck', { method: 'POST', body: JSON.stringify(data), timeout: AI_TIMEOUT });

// ── Morning Brief ──
export const getMorningBrief = () => request('/api/morning-brief');

// ── Deal Outcomes ──
export const recordDealOutcome = (data) => request('/api/deal-outcomes', { method: 'POST', body: JSON.stringify(data) });
export const getDealOutcomes = (bankKey) => request(bankKey ? `/api/deal-outcomes?bankKey=${encodeURIComponent(bankKey)}` : '/api/deal-outcomes');
export const getDealOutcomeStats = () => request('/api/deal-outcomes/stats');

// ── Landing Zones ──
export const fetchLandingZoneMatrix = (key) => request(`/api/banks/${encodeURIComponent(key)}/landing-zones`);
export const analyzeLandingZones = (data) => request('/api/research/landing-zones', { method: 'POST', body: JSON.stringify(data), timeout: AI_TIMEOUT });

// ── Discovery Storyline ──
export const fetchDiscoveryStoryline = (key) => request(`/api/banks/${encodeURIComponent(key)}/discovery-storyline`);
export const generateDiscoveryStoryline = (data) => request('/api/research/discovery-storyline', { method: 'POST', body: JSON.stringify(data), timeout: AI_TIMEOUT });

// ── Value Hypothesis (meeting-tailored) ──
export const generateValueHypothesis = (data) => request('/api/research/value-hypothesis', { method: 'POST', body: JSON.stringify(data), timeout: AI_TIMEOUT });

// ── Consulting Knowledge ──
export const fetchKnowledgeDomains = () => request('/api/knowledge/domains');
export const fetchDomainKnowledge = (domain) => request(`/api/knowledge/domains/${domain}`);
export const fetchDomainFile = (domain, file) => request(`/api/knowledge/domains/${domain}/${file}`);
export const fetchCapabilityTaxonomy = (domain) => request(`/api/knowledge/capability-taxonomy/${domain}`);
export const fetchPlaybookBenchmarks = (journey) =>
  journey ? request(`/api/knowledge/benchmarks-csv/${encodeURIComponent(journey)}`) : request('/api/knowledge/benchmarks-csv');
export const fetchBankKnowledge = (key, domains) => {
  const params = domains ? `?domains=${domains.join(',')}` : '';
  return request(`/api/knowledge/for-bank/${encodeURIComponent(key)}${params}`);
};
export const fetchRoiExamples = () => request('/api/knowledge/roi-examples');
export const fetchConsultingStandard = (name) => request(`/api/knowledge/standards/${name}`);

// ── Brief Feedback ──
export const submitBriefFeedback = (data) => request('/api/feedback/brief', { method: 'POST', body: JSON.stringify(data) });
export const fetchBriefFeedback = () => request('/api/feedback/brief');
export const fetchBriefFeedbackStats = () => request('/api/feedback/brief/stats');

// ── Meeting History (Layer 4) ──
export const createMeeting = (bankKey, data) => request(`/api/banks/${encodeURIComponent(bankKey)}/meetings`, { method: 'POST', body: JSON.stringify(data) });
export const getMeetings = (bankKey, { limit } = {}) => request(`/api/banks/${encodeURIComponent(bankKey)}/meetings${limit ? `?limit=${limit}` : ''}`);
export const updateMeeting = (bankKey, meetingId, data) => request(`/api/banks/${encodeURIComponent(bankKey)}/meetings/${encodeURIComponent(meetingId)}`, { method: 'PUT', body: JSON.stringify(data) });
export const extractMeetingFromTranscript = (bankKey, transcript) => request(`/api/banks/${encodeURIComponent(bankKey)}/meetings/extract`, { method: 'POST', body: JSON.stringify({ transcript }), timeout: AI_TIMEOUT });

// ── Change Detection (Layer 3) ──
export const getRecentChanges = (bankKey, { limit } = {}) => request(`/api/banks/${encodeURIComponent(bankKey)}/changes${limit ? `?limit=${limit}` : ''}`);

// ── Stakeholder Drift + Patterns (Sprint 2.3 / 2.4) ──
export const getStakeholderDrift = (bankKey, { view = 'cells', includeUnattributed = false, minFacts = 1 } = {}) => {
  const params = new URLSearchParams({ view, min_facts: String(minFacts) });
  if (includeUnattributed) params.set('include_unattributed', '1');
  return request(`/api/banks/${encodeURIComponent(bankKey)}/stakeholder-drift?${params}`);
};
export const getBankPatterns = (bankKey, { minConfidence = null, onlyUnacknowledged = false } = {}) => {
  const params = new URLSearchParams();
  if (minConfidence) params.set('min_confidence', minConfidence);
  if (onlyUnacknowledged) params.set('unack', '1');
  const qs = params.toString();
  return request(`/api/banks/${encodeURIComponent(bankKey)}/patterns${qs ? `?${qs}` : ''}`);
};
export const acknowledgePattern = (patternId, aeId) => request(`/api/patterns/${encodeURIComponent(patternId)}/acknowledge`, { method: 'POST', body: JSON.stringify({ ae_id: aeId }) });

// ── Change Feed (Sprint 4) ──
export const getBankChangeFeed = (bankKey, opts = {}) => {
  const params = new URLSearchParams();
  if (opts.lookback != null)        params.set('lookback', String(opts.lookback));
  if (opts.sort)                    params.set('sort', opts.sort);
  if (opts.minSignificance != null) params.set('min_significance', String(opts.minSignificance));
  if (opts.limit != null)           params.set('limit', String(opts.limit));
  if (opts.include?.length)         params.set('include', opts.include.join(','));
  const qs = params.toString();
  return request(`/api/banks/${encodeURIComponent(bankKey)}/change-feed${qs ? `?${qs}` : ''}`);
};
// ── Portfolio Query (Sprint 5) ──
export const runPortfolioQuery = (filter) => request('/api/portfolio/query', { method: 'POST', body: JSON.stringify({ filter }) });
export const getPortfolioQueryExamples = () => request('/api/portfolio/query/examples');
export const listPortfolioSavedViews = () => request('/api/portfolio/saved-views');
export const createPortfolioSavedView = (data) => request('/api/portfolio/saved-views', { method: 'POST', body: JSON.stringify(data) });
export const deletePortfolioSavedView = (id) => request(`/api/portfolio/saved-views/${encodeURIComponent(id)}`, { method: 'DELETE' });
// B3 — NL → predicate JSON (advisory; user reviews before running)
export const translatePortfolioQuery = (query) => request('/api/portfolio/query/translate', { method: 'POST', body: JSON.stringify({ query }), timeout: 45000 });

// ── Region/Country aggregations (post-B-series) ──
// `kind` is 'regions' or 'countries'; `identifier` is market key or country name.
export const fetchRegionIntel = (kind, identifier, opts = {}) => {
  const params = new URLSearchParams();
  if (opts.period) params.set('period', opts.period);
  if (opts.priorPeriod) params.set('prior_period', opts.priorPeriod);
  const qs = params.toString();
  return request(`/api/${kind}/${encodeURIComponent(identifier)}/intel${qs ? `?${qs}` : ''}`);
};
export const fetchRegionChangeFeed = (kind, identifier, opts = {}) => {
  const params = new URLSearchParams();
  if (opts.lookback != null)        params.set('lookback', String(opts.lookback));
  if (opts.sort)                    params.set('sort', opts.sort);
  if (opts.minSignificance != null) params.set('min_significance', String(opts.minSignificance));
  if (opts.limit != null)           params.set('limit', String(opts.limit));
  if (opts.include?.length)         params.set('include', opts.include.join(','));
  const qs = params.toString();
  return request(`/api/${kind}/${encodeURIComponent(identifier)}/change-feed${qs ? `?${qs}` : ''}`);
};
export const fetchRegionPulse = (kind, identifier, opts = {}) => {
  const params = new URLSearchParams();
  if (opts.period) params.set('period', opts.period);
  if (opts.priorPeriod) params.set('prior_period', opts.priorPeriod);
  const qs = params.toString();
  return request(`/api/${kind}/${encodeURIComponent(identifier)}/pulse${qs ? `?${qs}` : ''}`);
};

export const getPortfolioChangeFeed = (opts = {}) => {
  const params = new URLSearchParams();
  if (opts.lookback != null)        params.set('lookback', String(opts.lookback));
  if (opts.sort)                    params.set('sort', opts.sort);
  if (opts.minSignificance != null) params.set('min_significance', String(opts.minSignificance));
  if (opts.limit != null)           params.set('limit', String(opts.limit));
  if (opts.include?.length)         params.set('include', opts.include.join(','));
  const qs = params.toString();
  return request(`/api/change-feed${qs ? `?${qs}` : ''}`);
};

// ── Power Map (MEDDICC) ──
export const generatePowerMap = (bankKey, { persona } = {}) => request(`/api/banks/${encodeURIComponent(bankKey)}/power-map`, { method: 'POST', body: JSON.stringify({ persona }), timeout: AI_TIMEOUT });
export const getPowerMap = (bankKey) => request(`/api/banks/${encodeURIComponent(bankKey)}/power-map`);
