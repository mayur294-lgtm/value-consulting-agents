/**
 * Engagement & Execution Timeline — forward-looking action plan per bank
 * ─────────────────────────────────────────────────────────────────────
 * Generates a 60/90-day execution timeline by composing all intelligence
 * Nova has accumulated about a bank:
 *   - Power map (persons + influence + engagement_status)
 *   - Landing zones (4×5 matrix scores)
 *   - Account plan (strategic priorities)
 *   - Signals (recent grade-A/B events)
 *   - Meeting facts (verbatim stakeholder positions)
 *   - Corroborated patterns (fact↔signal pairings)
 *   - Stakeholder drift (sentiment trajectories)
 *   - Buying intent score (composite)
 *   - Opportunity windows (multi-stream)
 *   - Country regulatory pressure
 *   - Active VC engagement state
 *
 * Output: structured action list across 4 categories × 2 horizons.
 * Each action carries evidence_refs back to source records.
 *
 * Categories:
 *   workshop              — engagement / landing zone workshops
 *   stakeholder_outreach  — reach out to specific persons
 *   marketing_event       — co-hosted events / roundtables
 *   partner_led           — system integrator / consulting partner intros
 *
 * Pure deterministic — same inputs → same actions. The LLM is NOT in the
 * generation loop. (Optional polish layer can be added later.)
 */

import { randomUUID } from 'node:crypto';
import { computeBuyingIntent } from './buyingIntentScorer.mjs';
import { detectOpportunityWindows } from './opportunityWindowDetector.mjs';
import { getBankEngagementSummary } from './engagementTracker.mjs';

const CATEGORIES = ['workshop', 'stakeholder_outreach', 'marketing_event', 'partner_led'];
const HORIZONS = ['60d', '90d'];
const VALID_STATUSES = ['planned', 'in_progress', 'done', 'dropped'];

// ──────────────────────────────────────────────────────────────────────
// Input gathering — pulls everything needed for action generation
// ──────────────────────────────────────────────────────────────────────

function gatherInputs(db, bankKey) {
  const bank = db.prepare('SELECT * FROM banks WHERE key = ?').get(bankKey);
  if (!bank) throw new Error(`Bank not found: ${bankKey}`);
  const bankData = JSON.parse(bank.data || '{}');

  // Bank-scoped exclusions — array of keyword strings filtered against
  // landing zone names + meeting fact text + action titles. Set via
  // banks.data.timeline_exclusions = ["bancassurance", "wealth", ...].
  const exclusions = Array.isArray(bankData.timeline_exclusions)
    ? bankData.timeline_exclusions.map(s => String(s).toLowerCase()).filter(Boolean)
    : [];

  function isExcluded(text) {
    if (!exclusions.length || !text) return false;
    const lower = String(text).toLowerCase();
    return exclusions.some(kw => lower.includes(kw));
  }

  // Power map / persons — sorted by influence, with engagement state
  const persons = db.prepare(`
    SELECT id, canonical_name, role, role_category, lob, influence_score,
           engagement_status, support_status, note
    FROM persons WHERE bank_key = ? ORDER BY influence_score DESC
  `).all(bankKey);

  // Landing zones — normalized rows (zone_name, fit_score, rationale, entry_strategy)
  let landingZones = [];
  try {
    landingZones = db.prepare(`
      SELECT id, zone_name, fit_score, rationale, entry_strategy, details, source_url
      FROM landing_zones WHERE bank_key = ? ORDER BY fit_score ASC
    `).all(bankKey);
    // Apply bank-scoped exclusions — drop zones whose name/details match an
    // excluded keyword (e.g. "bancassurance" for a bank that explicitly
    // doesn't want insurance-related actions on the plan).
    if (exclusions.length > 0) {
      landingZones = landingZones.filter(z => !isExcluded(`${z.zone_name} ${z.details || ''}`));
    }
  } catch { /* table may not exist */ }

  // Qualification (account plan inputs)
  const qual = db.prepare('SELECT data FROM qualification WHERE bank_key = ?').get(bankKey);
  const qualData = qual ? JSON.parse(qual.data) : {};

  // Recent A/B-grade signals (60 days)
  const cutoff60 = new Date(); cutoff60.setDate(cutoff60.getDate() - 60);
  const cutoff60ISO = cutoff60.toISOString();
  const signals = db.prepare(`
    SELECT id, signal_category, title, source_url, source_grade, publisher_name,
           detected_at, severity, evidence_quote
    FROM deal_signals
    WHERE deal_id = ? AND COALESCE(is_demo, 0) = 0
      AND source_grade IN ('A', 'B') AND detected_at >= ?
    ORDER BY detected_at DESC
  `).all(bankKey, cutoff60ISO);

  // Meeting facts — sentiments per topic
  const facts = db.prepare(`
    SELECT mf.id, mf.speaker_person_id, mf.speaker_name, mf.topic, mf.position,
           mf.sentiment, mf.evidence_quote, mf.meeting_date, mf.confidence_tier,
           p.role, p.influence_score
    FROM meeting_facts mf
    LEFT JOIN persons p ON p.id = mf.speaker_person_id
    WHERE mf.bank_key = ?
    ORDER BY mf.meeting_date DESC
  `).all(bankKey);

  // Patterns
  const patterns = db.prepare(`
    SELECT pm.*, ds.title AS signal_title, ds.source_url AS signal_url
    FROM pattern_matches pm
    LEFT JOIN deal_signals ds ON ds.id = pm.external_signal_id
    WHERE pm.bank_key = ? AND pm.confidence IN ('high','medium')
  `).all(bankKey);

  // Composite intelligence
  const intent = computeBuyingIntent(db, bankKey, { lookbackDays: 60 });
  const windows = detectOpportunityWindows(db, bankKey, { lookbackDays: 90 });
  const engagement = getBankEngagementSummary(db, bankKey);

  // Country context (regulatory pressure indicator)
  let country = null;
  if (bank.country) {
    const ctyRow = db.prepare(`SELECT data FROM countries WHERE name = ?`).get(bank.country.split(' /')[0].split(' (')[0].trim());
    if (ctyRow) country = JSON.parse(ctyRow.data || '{}');
  }

  // Stakeholder drift cells
  const driftRows = db.prepare(`
    SELECT mf.speaker_person_id, mf.speaker_name, mf.topic,
           GROUP_CONCAT(mf.sentiment, '|') AS sentiments,
           GROUP_CONCAT(mf.meeting_date, '|') AS dates,
           p.role, p.influence_score
    FROM meeting_facts mf
    LEFT JOIN persons p ON p.id = mf.speaker_person_id
    WHERE mf.bank_key = ? AND mf.speaker_person_id IS NOT NULL
    GROUP BY mf.speaker_person_id, mf.topic
    HAVING COUNT(*) >= 2
  `).all(bankKey);
  const SENTIMENT_RANK = { negative: -1, mixed: 0, neutral: 0, positive: 1 };
  const drift = driftRows.map(r => {
    const sents = r.sentiments.split('|');
    const dates = r.dates.split('|');
    const paired = sents.map((s, i) => ({ s, d: dates[i] })).sort((a, b) => a.d.localeCompare(b.d));
    const first = SENTIMENT_RANK[paired[0].s] ?? 0;
    const last = SENTIMENT_RANK[paired[paired.length - 1].s] ?? 0;
    const trend = last > first ? 'improving' : last < first ? 'deteriorating' : 'stable';
    return { ...r, trend, n_facts: sents.length };
  });

  return {
    bank, bankData, persons, landingZones, qualData,
    signals, facts, patterns, intent, windows, engagement,
    country, drift, exclusions, isExcluded,
  };
}

// ──────────────────────────────────────────────────────────────────────
// Action rules — each returns Array<actionDraft>
// ──────────────────────────────────────────────────────────────────────

/**
 * Workshop actions: landing zone with low maturity + corroborating evidence
 * = recommend a workshop on that zone.
 */
function ruleWorkshops(inputs) {
  const actions = [];
  const lzs = inputs.landingZones || [];

  // Trigger workshop on any landing zone with fit_score >= 6 (these are
  // strong-fit zones worth a structured workshop). The lower the score
  // the lower the priority of bringing it forward — high-fit zones with
  // good evidence are the prime candidates.
  // Note on score semantics: fit_score is "how good a fit is this zone for Backbase
  // at this bank", so HIGH score = primary candidate for workshop.
  // Take top 4 by fit_score with score >= 6 (or >= 5 if intent is hot).
  const threshold = inputs.intent.score >= 50 ? 5 : 6;
  const candidateZones = lzs
    .filter(z => (z.fit_score || 0) >= threshold)
    .sort((a, b) => (b.fit_score || 0) - (a.fit_score || 0))
    .slice(0, 4);

  for (const zone of candidateZones) {
    const zoneName = zone.zone_name || '';
    // Find supporting facts mentioning related topics in the zone name
    const zoneToken = zoneName.toLowerCase().split(/\s+/)[0];
    const supportingFacts = inputs.facts.filter(f =>
      f.position && zoneToken && f.position.toLowerCase().includes(zoneToken)
    ).slice(0, 2);

    // High fit-score zones (≥8) get scheduled in 60d — they're the
    // highest-conviction Backbase plays and shouldn't wait. Mid-fit zones
    // go 60d if active engagement exists (workshop fits the discovery /
    // assessment cadence), 90d otherwise.
    const hasActiveEng = inputs.engagement?.has_active_engagement;
    const horizon = (zone.fit_score >= 8) ? '60d'
      : (hasActiveEng) ? '60d'
      : '90d';
    actions.push({
      category: 'workshop',
      horizon,
      priority: Math.min(10, Math.round((zone.fit_score || 5) - 2)),
      title: `Landing zone workshop: ${zoneName}`,
      rationale: `Fit score ${zone.fit_score}/10. ${supportingFacts.length > 0
        ? `Stakeholders touched related themes in ${supportingFacts.length} meeting fact${supportingFacts.length === 1 ? '' : 's'}.`
        : zone.rationale ? `${zone.rationale.slice(0, 150)}` : 'Co-design session validates fit and surfaces bank-specific scope.'}`,
      evidence_refs: {
        landing_zones: [zone.id],
        facts: supportingFacts.map(f => f.id),
      },
    });
  }

  // If patterns exist with topic='technical' and high confidence → architecture workshop
  const techPatterns = inputs.patterns.filter(p => p.topic === 'technical' && p.confidence === 'high');
  if (techPatterns.length > 0) {
    actions.push({
      category: 'workshop',
      horizon: '60d',
      priority: 7,
      title: 'Architecture deep-dive workshop',
      rationale: `${techPatterns.length} high-confidence corroborated pattern${techPatterns.length === 1 ? '' : 's'} on technical topics indicate stakeholder appetite for architectural conversation.`,
      evidence_refs: { patterns: techPatterns.map(p => p.id) },
    });
  }

  // If active VC engagement in 'discovery' state → discovery synthesis workshop
  if (inputs.engagement?.has_active_engagement) {
    const discoveryEng = inputs.engagement.active_engagements.find(e => e.state === 'discovery');
    if (discoveryEng) {
      actions.push({
        category: 'workshop',
        horizon: '60d',
        priority: 8,
        title: `Discovery synthesis workshop (engagement: ${discoveryEng.title || discoveryEng.engagement_type})`,
        rationale: `Active VC engagement is in discovery state. Workshop to synthesize findings and align on capability priorities before assessment phase.`,
        evidence_refs: { engagements: [discoveryEng.id] },
      });
    }
  }

  return actions;
}

/**
 * Stakeholder reach-out: high-influence uncontacted, deteriorating drift,
 * recent appointments.
 */
function ruleStakeholderOutreach(inputs) {
  const actions = [];

  // High-influence not-yet-warm: includes neutral, aware, unknown, cold.
  // Excludes already-engaged (engaged, supportive, champion, ally).
  const ENGAGED_STATES = new Set(['engaged', 'supportive', 'champion', 'ally', 'advocate']);
  const highInfluenceUncontacted = inputs.persons.filter(p =>
    (p.influence_score || 0) >= 7 &&
    !ENGAGED_STATES.has((p.engagement_status || '').toLowerCase())
  );
  for (const p of highInfluenceUncontacted.slice(0, 5)) {
    // C-level / influence ≥9 always 60d (highest leverage, can't wait)
    // Influence 7-8: 60d if intent is warm+, 90d otherwise (still warrants action)
    const isCLevel = (p.influence_score || 0) >= 9 ||
      /\b(CEO|CTO|CIO|CFO|CDO|COO|Chair|Group)\b/i.test(p.role || '');
    const horizon = isCLevel ? '60d'
      : (inputs.intent.score >= 35) ? '60d' : '90d';
    actions.push({
      category: 'stakeholder_outreach',
      horizon,
      priority: Math.min(10, p.influence_score),
      title: `Open relationship with ${p.canonical_name}`,
      rationale: `Influence ${p.influence_score}/10 · ${p.role || 'role unknown'} · current engagement: ${p.engagement_status || 'none'}. ${isCLevel ? 'C-level / executive — highest leverage.' : 'Decision-maker not yet in our orbit.'}`,
      evidence_refs: { persons: [p.id] },
    });
  }

  // Deteriorating drift speakers — re-engage
  const deteriorating = inputs.drift.filter(d => d.trend === 'deteriorating' && (d.influence_score || 0) >= 5);
  for (const d of deteriorating.slice(0, 3)) {
    actions.push({
      category: 'stakeholder_outreach',
      horizon: '60d',
      priority: 9,
      title: `Re-engage ${d.speaker_name} on ${d.topic}`,
      rationale: `Sentiment trajectory deteriorating across ${d.n_facts} facts. ${d.role || 'Stakeholder'} (influence ${d.influence_score || '—'}) — direct touch needed before pattern hardens.`,
      evidence_refs: { persons: d.speaker_person_id ? [d.speaker_person_id] : [], facts: [] },
    });
  }

  // Recent appointment signals — congratulatory/discovery reach-out
  const apptSignals = inputs.signals.filter(s =>
    s.signal_category === 'stakeholder' &&
    /\b(appointed|named|joins as|new|hires|hired)\b/i.test(s.title || '')
  );
  for (const s of apptSignals.slice(0, 2)) {
    actions.push({
      category: 'stakeholder_outreach',
      horizon: '60d',
      priority: 8,
      title: `Congratulate + intro to new appointee`,
      rationale: `Recent stakeholder change: "${s.title}". Window to introduce Backbase before priorities solidify.`,
      evidence_refs: { signals: [s.id] },
    });
  }

  return actions;
}

/**
 * Marketing & events: country-level opportunity windows, regulatory clusters,
 * peer-bank patterns to co-host roundtables on themes.
 */
function ruleMarketingEvents(inputs) {
  const actions = [];

  // Opportunity windows that benefit from awareness/peer signal
  for (const w of inputs.windows) {
    if (w.type === 'REPLATFORM_WINDOW' || w.type === 'REGULATORY_FORCING') {
      actions.push({
        category: 'marketing_event',
        horizon: '90d',
        priority: w.significance,
        title: `Co-host roundtable: "${w.title}"`,
        rationale: `${w.detail} An invite-only roundtable creates peer-validation context for the bank's leadership.`,
        evidence_refs: {
          windows: [w.type],
          signals: [w.evidence?.regulatory?.[0]?.id, w.evidence?.leader_change?.[0]?.id].filter(Boolean),
        },
      });
    }
  }

  // Regulatory pressure in country → executive briefing
  if (inputs.country?.regulatory_environment?.key_regulations?.length > 0) {
    const urgentRegs = inputs.country.regulatory_environment.key_regulations.filter(r =>
      r.relevance === 'high' && (r.status === 'in_progress' || r.status === 'planned')
    );
    if (urgentRegs.length > 0) {
      actions.push({
        category: 'marketing_event',
        horizon: '90d',
        priority: 7,
        title: `Executive briefing on ${urgentRegs[0].name} compliance pathway`,
        rationale: `${urgentRegs.length} high-relevance regulation${urgentRegs.length === 1 ? '' : 's'} in ${inputs.bank.country}. Pre-compliance briefing positions Backbase as the answer to a forced question.`,
        evidence_refs: {
          regulations: urgentRegs.map(r => r.name),
        },
      });
    }
  }

  // High intent + few existing engagements → analyst event invite
  if (inputs.intent.score >= 50 && (inputs.engagement?.active_count || 0) === 0) {
    actions.push({
      category: 'marketing_event',
      horizon: '90d',
      priority: 6,
      title: 'Invite to Backbase Engage / analyst event',
      rationale: `Buying intent ${inputs.intent.score}/100 (${inputs.intent.tier}) with no active VC engagement. Event invite is a low-pressure way to deepen relationship before formal handoff.`,
      evidence_refs: { intent_score: inputs.intent.score, intent_tier: inputs.intent.tier },
    });
  }

  return actions;
}

/**
 * Partner-led initiatives: SI/consulting partner intros where the bank's
 * profile suggests delivery-arm involvement adds credibility/capacity.
 */
function rulePartnerLed(inputs) {
  const actions = [];

  // Active engagement in discovery/assessment → SI partner intro
  const inDiscovery = inputs.engagement?.active_engagements?.find(e =>
    ['discovery', 'assessment'].includes(e.state)
  );
  if (inDiscovery) {
    actions.push({
      category: 'partner_led',
      horizon: '60d',
      priority: 8,
      title: 'System integrator partner introduction',
      rationale: `Engagement in ${inDiscovery.state} state. SI partner intro brings delivery confidence + complementary discovery muscle. Reduces customer perceived risk.`,
      evidence_refs: { engagements: [inDiscovery.id] },
    });
  }

  // Vendor pattern detected → competitive displacement partner play
  const vendorPatterns = inputs.patterns.filter(p => p.topic === 'vendors' && p.confidence !== 'low');
  if (vendorPatterns.length > 0) {
    actions.push({
      category: 'partner_led',
      horizon: '90d',
      priority: 7,
      title: 'Co-engage with displacement-experienced consulting partner',
      rationale: `${vendorPatterns.length} vendor-topic pattern${vendorPatterns.length === 1 ? '' : 's'} corroborated. A consulting partner with replatforming case studies adds peer evidence the bank trusts.`,
      evidence_refs: { patterns: vendorPatterns.map(p => p.id) },
    });
  }

  // High-grade competitive signals + no active engagement → channel partner alert
  const competitiveSignals = inputs.signals.filter(s =>
    s.signal_category === 'competitive' && (s.source_grade === 'A' || s.source_grade === 'B')
  );
  if (competitiveSignals.length >= 2 && (inputs.engagement?.active_count || 0) === 0) {
    actions.push({
      category: 'partner_led',
      horizon: '60d',
      priority: 7,
      title: 'Brief channel partner network on this account',
      rationale: `${competitiveSignals.length} grade-A/B competitive signals detected. Pre-empt with partners who have warm relationships at this bank.`,
      evidence_refs: { signals: competitiveSignals.slice(0, 3).map(s => s.id) },
    });
  }

  // Country has high fintech competitive density → ecosystem event with local partner
  if (inputs.country?.fintech_landscape?.maturity_level === 'advanced' ||
      inputs.country?.fintech_landscape?.maturity_level === 'mature') {
    actions.push({
      category: 'partner_led',
      horizon: '90d',
      priority: 5,
      title: `Local partner-hosted ecosystem event in ${inputs.bank.country}`,
      rationale: `${inputs.bank.country} fintech maturity is ${inputs.country.fintech_landscape.maturity_level}. Local partner-hosted event taps dense ecosystem with low Backbase exposure cost.`,
      evidence_refs: { country: inputs.bank.country },
    });
  }

  return actions;
}

// ──────────────────────────────────────────────────────────────────────
// Public API
// ──────────────────────────────────────────────────────────────────────

/**
 * Generate timeline action drafts (does NOT persist).
 * Returns array of { category, horizon, title, rationale, evidence_refs, priority }.
 */
export function generateTimelineActions(db, bankKey) {
  const inputs = gatherInputs(db, bankKey);
  let drafts = [
    ...ruleWorkshops(inputs),
    ...ruleStakeholderOutreach(inputs),
    ...ruleMarketingEvents(inputs),
    ...rulePartnerLed(inputs),
  ];

  // Belt-and-braces exclusion filter: scrub any action whose title or
  // rationale text matches an excluded keyword (catches anything that
  // slipped past per-rule input filtering).
  if (inputs.exclusions.length > 0) {
    drafts = drafts.filter(d => !inputs.isExcluded(`${d.title} ${d.rationale || ''}`));
  }

  // Stable sort by priority desc, category for grouping
  drafts.sort((a, b) => (b.priority || 0) - (a.priority || 0) || a.category.localeCompare(b.category));
  return {
    bank_key: bankKey,
    bank_name: inputs.bank.bank_name,
    intent: inputs.intent,
    summary: {
      total_actions: drafts.length,
      by_category: CATEGORIES.reduce((acc, c) => {
        acc[c] = drafts.filter(d => d.category === c).length;
        return acc;
      }, {}),
      by_horizon: HORIZONS.reduce((acc, h) => {
        acc[h] = drafts.filter(d => d.horizon === h).length;
        return acc;
      }, {}),
    },
    drafts,
  };
}

/**
 * Generate + persist timeline. Replaces only auto-generated `planned`
 * actions from prior runs — preserves user-added actions and any action
 * with status != 'planned' (in_progress, done, dropped).
 */
export function regenerateTimeline(db, bankKey) {
  const result = generateTimelineActions(db, bankKey);
  const runId = randomUUID();

  const txn = db.transaction(() => {
    // Delete only auto-generated actions still in planned state
    db.prepare(`
      DELETE FROM engagement_timeline_actions
      WHERE bank_key = ? AND is_auto_generated = 1 AND status = 'planned'
    `).run(bankKey);

    // Insert fresh drafts
    const insert = db.prepare(`
      INSERT INTO engagement_timeline_actions (
        id, bank_key, generation_run_id, horizon, category, title, rationale,
        evidence_json, status, is_auto_generated, priority
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'planned', 1, ?)
    `);
    for (const d of result.drafts) {
      insert.run(
        randomUUID(), bankKey, runId, d.horizon, d.category, d.title, d.rationale,
        JSON.stringify(d.evidence_refs || {}), d.priority || 5
      );
    }
  });
  txn();

  return { ...result, generation_run_id: runId };
}

/**
 * Get the current timeline for a bank, joined with evidence resolution
 * (so UI can render provenance chips for cited sources).
 */
export function getBankTimeline(db, bankKey) {
  const rows = db.prepare(`
    SELECT * FROM engagement_timeline_actions
    WHERE bank_key = ?
    ORDER BY
      CASE horizon WHEN '60d' THEN 0 WHEN '90d' THEN 1 ELSE 2 END,
      CASE status
        WHEN 'in_progress' THEN 0 WHEN 'planned' THEN 1
        WHEN 'done' THEN 2 WHEN 'dropped' THEN 3 ELSE 4 END,
      priority DESC
  `).all(bankKey);

  return rows.map(r => ({
    ...r,
    evidence: r.evidence_json ? JSON.parse(r.evidence_json) : {},
  }));
}

/**
 * Update a single action — typically status / owner / due_date.
 */
export function updateAction(db, actionId, updates) {
  const allowed = ['status', 'owner', 'due_date', 'priority', 'title', 'rationale'];
  const fields = [];
  const params = [];
  for (const [k, v] of Object.entries(updates)) {
    if (!allowed.includes(k)) continue;
    if (k === 'status' && !VALID_STATUSES.includes(v)) {
      throw new Error(`Invalid status: ${v}`);
    }
    fields.push(`${k} = ?`);
    params.push(v);
  }
  if (fields.length === 0) return null;
  fields.push(`updated_at = datetime('now')`);
  if (updates.status === 'done') fields.push(`completed_at = datetime('now')`);
  params.push(actionId);
  db.prepare(`UPDATE engagement_timeline_actions SET ${fields.join(', ')} WHERE id = ?`).run(...params);
  return db.prepare('SELECT * FROM engagement_timeline_actions WHERE id = ?').get(actionId);
}

/**
 * Add a custom (user-authored) action.
 */
export function addCustomAction(db, bankKey, input) {
  const { category, horizon, title, rationale = null, owner = null, due_date = null, priority = 5 } = input;
  if (!CATEGORIES.includes(category)) throw new Error(`Invalid category: ${category}`);
  if (!HORIZONS.includes(horizon)) throw new Error(`Invalid horizon: ${horizon}`);
  if (!title) throw new Error('title required');
  const id = randomUUID();
  db.prepare(`
    INSERT INTO engagement_timeline_actions (
      id, bank_key, horizon, category, title, rationale,
      status, is_auto_generated, owner, due_date, priority
    ) VALUES (?, ?, ?, ?, ?, ?, 'planned', 0, ?, ?, ?)
  `).run(id, bankKey, horizon, category, title, rationale, owner, due_date, priority);
  return db.prepare('SELECT * FROM engagement_timeline_actions WHERE id = ?').get(id);
}

export function deleteAction(db, actionId) {
  db.prepare('DELETE FROM engagement_timeline_actions WHERE id = ?').run(actionId);
  return { deleted: true };
}

export { CATEGORIES, HORIZONS, VALID_STATUSES };
