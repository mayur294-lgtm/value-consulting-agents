/**
 * Engagement State Tracker — AE↔VC bridge layer
 * ─────────────────────────────────────────────
 * Tracks VC engagement state per bank with a 5-state machine:
 *   scoping → discovery → assessment → delivered → closed
 *
 * The bridge layer's purpose: make Nova aware of when a VC engagement is
 * active on a bank, what phase it's in, what artifacts have been produced.
 * Without this, AE and VC operate in parallel silos.
 *
 * Pure deterministic library — no LLM in the loop. Read/write engagement
 * records, transition states, register artifacts, emit Nova signals on
 * state transitions so the change feed surfaces the engagement lifecycle.
 */

import { randomUUID } from 'node:crypto';

const VALID_STATES = ['scoping', 'discovery', 'assessment', 'delivered', 'closed'];
const VALID_TYPES = ['value_assessment', 'ignite_inspire', 'upgrade', 'roi_only', 'capability_assessment', 'other'];

// State machine — what's allowed
const STATE_TRANSITIONS = {
  scoping: ['discovery', 'closed'],          // can skip to closed if scoping is abandoned
  discovery: ['assessment', 'scoping', 'closed'],
  assessment: ['delivered', 'discovery', 'closed'],
  delivered: ['closed', 'assessment'],       // re-open if needed
  closed: [],                                 // terminal
};

export function listEngagements(db, options = {}) {
  const { bankKey, state, openOnly = false } = options;
  const where = [];
  const params = [];
  if (bankKey) { where.push('bank_key = ?'); params.push(bankKey); }
  if (state) { where.push('state = ?'); params.push(state); }
  if (openOnly) { where.push("state != 'closed'"); }
  const sql = `
    SELECT * FROM engagements
    ${where.length ? 'WHERE ' + where.join(' AND ') : ''}
    ORDER BY updated_at DESC
  `;
  return db.prepare(sql).all(...params);
}

export function getEngagement(db, id) {
  return db.prepare('SELECT * FROM engagements WHERE id = ?').get(id);
}

export function createEngagement(db, input) {
  const {
    bank_key, engagement_type = 'value_assessment',
    title = null, vc_lead = null, ae_lead = null,
    kickoff_date = null, target_close_date = null,
    handoff_snapshot = null, state = 'scoping',
  } = input;

  if (!bank_key) throw new Error('bank_key required');
  if (!VALID_TYPES.includes(engagement_type)) {
    throw new Error(`engagement_type must be one of: ${VALID_TYPES.join(', ')}`);
  }
  if (!VALID_STATES.includes(state)) {
    throw new Error(`state must be one of: ${VALID_STATES.join(', ')}`);
  }

  const id = randomUUID();
  db.prepare(`
    INSERT INTO engagements (
      id, bank_key, engagement_type, state, title, kickoff_date, target_close_date,
      vc_lead, ae_lead, handoff_snapshot_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    id, bank_key, engagement_type, state, title, kickoff_date, target_close_date,
    vc_lead, ae_lead, handoff_snapshot ? JSON.stringify(handoff_snapshot) : null
  );

  // Emit a Nova signal so the change feed surfaces the new engagement
  emitEngagementSignal(db, id, bank_key, 'engagement_created', `VC engagement started: ${title || engagement_type}`);

  return getEngagement(db, id);
}

export function transitionEngagement(db, id, newState, options = {}) {
  const eng = getEngagement(db, id);
  if (!eng) throw new Error(`Engagement not found: ${id}`);
  if (!VALID_STATES.includes(newState)) throw new Error(`Invalid state: ${newState}`);
  const allowedNext = STATE_TRANSITIONS[eng.state] || [];
  if (!allowedNext.includes(newState) && newState !== eng.state) {
    throw new Error(`Cannot transition from ${eng.state} to ${newState}. Allowed: ${allowedNext.join(', ')}`);
  }

  const closedAt = newState === 'closed' ? new Date().toISOString() : null;
  const outcome = options.outcome || null;

  db.prepare(`
    UPDATE engagements
    SET state = ?, updated_at = datetime('now'),
        closed_at = COALESCE(?, closed_at),
        outcome = COALESCE(?, outcome)
    WHERE id = ?
  `).run(newState, closedAt, outcome, id);

  emitEngagementSignal(db, id, eng.bank_key, 'engagement_transitioned',
    `Engagement state: ${eng.state} → ${newState}${outcome ? ` (${outcome})` : ''}`);

  return getEngagement(db, id);
}

export function registerArtifact(db, input) {
  const {
    engagement_id, artifact_type, title, summary = null,
    content_url = null, content_format = null,
    key_findings = null, published_by = null,
  } = input;

  if (!engagement_id) throw new Error('engagement_id required');
  if (!artifact_type) throw new Error('artifact_type required');
  if (!title) throw new Error('title required');

  const eng = getEngagement(db, engagement_id);
  if (!eng) throw new Error(`Engagement not found: ${engagement_id}`);

  const id = randomUUID();
  db.prepare(`
    INSERT INTO engagement_artifacts (
      id, engagement_id, bank_key, artifact_type, title, summary,
      content_url, content_format, key_findings_json, published_by
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    id, engagement_id, eng.bank_key, artifact_type, title, summary,
    content_url, content_format,
    key_findings ? JSON.stringify(key_findings) : null,
    published_by
  );

  emitEngagementSignal(db, engagement_id, eng.bank_key, 'artifact_published',
    `${artifact_type}: ${title}`);

  // Auto-advance state if appropriate (e.g., publishing first ROI → 'delivered')
  if (eng.state === 'assessment' && (artifact_type === 'roi' || artifact_type === 'roadmap')) {
    transitionEngagement(db, engagement_id, 'delivered');
  }

  return db.prepare('SELECT * FROM engagement_artifacts WHERE id = ?').get(id);
}

export function listArtifacts(db, options = {}) {
  const { engagementId, bankKey, artifactType } = options;
  const where = [];
  const params = [];
  if (engagementId) { where.push('engagement_id = ?'); params.push(engagementId); }
  if (bankKey) { where.push('bank_key = ?'); params.push(bankKey); }
  if (artifactType) { where.push('artifact_type = ?'); params.push(artifactType); }
  const sql = `
    SELECT * FROM engagement_artifacts
    ${where.length ? 'WHERE ' + where.join(' AND ') : ''}
    ORDER BY published_at DESC
  `;
  return db.prepare(sql).all(...params);
}

/**
 * Emit a Nova signal for engagement events so they surface in the change feed.
 * Uses signal_category='internal' to distinguish from external news.
 */
function emitEngagementSignal(db, engagementId, bankKey, event, headline) {
  try {
    db.prepare(`
      INSERT INTO deal_signals (
        id, deal_id, signal_category, signal_event, title, source_type,
        severity, detected_at, source_grade, publisher_name, is_demo, relevance_score
      ) VALUES (?, ?, 'internal', ?, ?, 'internal', 'attention', datetime('now'), 'A', 'VC engagement', 0, 7)
    `).run(randomUUID(), bankKey, event, headline);
  } catch (err) {
    console.warn(`[engagementTracker] Could not emit signal: ${err.message}`);
  }
}

/**
 * State summary per bank — used by Nova bank profile + change-feed filter
 * to show "active engagement" badge.
 */
export function getBankEngagementSummary(db, bankKey) {
  const all = listEngagements(db, { bankKey });
  const open = all.filter(e => e.state !== 'closed');
  const closed = all.filter(e => e.state === 'closed');
  const artifacts = listArtifacts(db, { bankKey });
  return {
    bank_key: bankKey,
    has_active_engagement: open.length > 0,
    active_count: open.length,
    closed_count: closed.length,
    active_engagements: open,
    artifact_count: artifacts.length,
    latest_artifact: artifacts[0] || null,
  };
}

export { VALID_STATES, VALID_TYPES, STATE_TRANSITIONS };
