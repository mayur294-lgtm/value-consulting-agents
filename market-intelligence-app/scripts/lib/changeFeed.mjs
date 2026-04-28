/**
 * Change Feed — Sprint 4.1
 * ────────────────────────
 * Unified delta stream that surfaces "what changed" across all of Nova's
 * persistence layers. The reframe behind Sprint 4: the default view of a
 * bank (and of the AE's portfolio) shouldn't be "what is" — it should be
 * "what changed since you last looked." Static profiles become one click away;
 * the change feed becomes the front door.
 *
 * Six source streams composed into ChangeEvent[]:
 *   1. NEW_SIGNAL          — high-grade signals detected since cutoff
 *   2. NEW_MEETING_FACT    — extracted facts (T1 attributed only by default)
 *   3. NEW_PATTERN         — corroborated cross-reference patterns
 *   4. PULSE_DIFF          — per-section deltas from pulseDiffer
 *   5. STAKEHOLDER_DRIFT   — sentiment ladder transitions (improving/deteriorating)
 *   6. ENTITY_HISTORY      — field-level edits to bank/persons/qualification
 *
 * Each event:
 *   {
 *     id: stable hash,
 *     type: 'NEW_SIGNAL' | 'NEW_MEETING_FACT' | ...,
 *     bank_key: string,
 *     timestamp: ISO datetime,
 *     significance: 0..10 (calibrated weight),
 *     headline: string (single-sentence summary, no LLM),
 *     detail: object (type-specific payload),
 *     source_grade: 'A'|'B'|'C'|'D'|null,
 *     confidence_tier: 1|2|3|null,
 *     citation: { url?, label?, evidence_quote? },
 *   }
 *
 * Significance is structural (not LLM):
 *   - NEW_SIGNAL grade-A or urgent severity → 8-10
 *   - NEW_PATTERN high confidence + grade A/B → 7-9
 *   - NEW_MEETING_FACT T1 attributed to high-influence person → 6-8
 *   - PULSE_DIFF score change ≥ 1.0 → 5-7
 *   - STAKEHOLDER_DRIFT improving/deteriorating with n≥2 → 5-7
 *   - NEW_SIGNAL grade-C or below → 2-4
 *   - ENTITY_HISTORY low-impact field → 1-3
 *
 * The entire library is a deterministic transformation of DB rows. Re-running
 * the same range produces the same feed. No LLM in the loop.
 */

import { createHash } from 'node:crypto';

const DEFAULT_LOOKBACK_DAYS = 30;

function hashId(parts) {
  return createHash('sha256').update(parts.join('|')).digest('hex').slice(0, 16);
}

function withinLookback(dateStr, cutoffISO) {
  if (!dateStr || !cutoffISO) return true; // no cutoff = include all
  return String(dateStr).slice(0, 19) >= cutoffISO.slice(0, 19);
}

/**
 * Build a SQL fragment for bank scoping. Supports three modes:
 *   - bankKey: single bank      → "<col> = ?"
 *   - bankKeys: array of banks  → "<col> IN (?, ?, ?)"
 *   - neither:                  → no clause (portfolio-wide)
 *
 * Region/country pages pass bankKeys; bank pages pass bankKey; portfolio
 * surfaces pass neither. Single helper, used by every stream loader.
 */
function bankScopeClause(col, { bankKey, bankKeys }) {
  if (bankKey) return { sql: `${col} = ?`, params: [bankKey] };
  if (Array.isArray(bankKeys) && bankKeys.length > 0) {
    return { sql: `${col} IN (${bankKeys.map(() => '?').join(',')})`, params: [...bankKeys] };
  }
  return { sql: null, params: [] };
}

// ──────────────────────────────────────────────────────────────────────
// Stream 1: NEW_SIGNAL
// ──────────────────────────────────────────────────────────────────────
function loadSignalEvents(db, { bankKey, bankKeys, cutoffISO, limit = 50 }) {
  const where = ['COALESCE(is_demo, 0) = 0'];
  const params = [];
  const scope = bankScopeClause('deal_id', { bankKey, bankKeys });
  if (scope.sql) { where.push(scope.sql); params.push(...scope.params); }
  if (cutoffISO) { where.push('detected_at >= ?'); params.push(cutoffISO); }
  const rows = db.prepare(`
    SELECT id, deal_id AS bank_key, signal_category, signal_event, title, description,
           source_url, source_type, severity, detected_at, source_grade, publisher_name,
           relevance_score, evidence_quote
    FROM deal_signals
    WHERE ${where.join(' AND ')}
    ORDER BY detected_at DESC
    LIMIT ?
  `).all(...params, limit);

  return rows.map(s => {
    // Significance = severity * weight + grade boost
    const sevWeight = s.severity === 'urgent' ? 7 : s.severity === 'attention' ? 5 : 3;
    const gradeBoost = { A: 3, B: 2, C: 1, D: 0 }[s.source_grade] || 0;
    const relScore = (s.relevance_score || 5) / 2; // 0-5 scale
    const significance = Math.min(10, Math.round(sevWeight + gradeBoost + relScore - 3));
    return {
      id: hashId(['signal', s.id]),
      type: 'NEW_SIGNAL',
      bank_key: s.bank_key,
      timestamp: s.detected_at,
      significance,
      headline: s.title || `${s.signal_category} signal`,
      detail: {
        category: s.signal_category,
        event: s.signal_event,
        severity: s.severity,
        description: s.description,
      },
      source_grade: s.source_grade,
      confidence_tier: s.relevance_score >= 7 ? 1 : 2,
      citation: {
        url: s.source_url,
        // Sprint 4 audit fix: A-grade signals without a parsed publisher
        // (e.g., bank-press URLs whose titles lack a "- Publisher" pattern)
        // got "news" as label, which is misleading. Use a contextual label
        // based on the grade so the AE knows it's a primary source.
        label: s.publisher_name
          ? s.publisher_name
          : s.source_grade === 'A' ? 'Primary source'
          : s.source_grade === 'B' ? 'Tier-1 press'
          : s.source_grade === 'C' ? 'Trade press'
          : s.source_grade === 'D' ? 'Low-authority source'
          : (s.source_type || 'source'),
        evidence_quote: s.evidence_quote,
      },
    };
  });
}

// ──────────────────────────────────────────────────────────────────────
// Stream 2: NEW_MEETING_FACT
// ──────────────────────────────────────────────────────────────────────
function loadMeetingFactEvents(db, { bankKey, bankKeys, cutoffISO, attributedOnly = true, limit = 50 }) {
  const where = [];
  const params = [];
  const scope = bankScopeClause('mf.bank_key', { bankKey, bankKeys });
  if (scope.sql) { where.push(scope.sql); params.push(...scope.params); }
  if (cutoffISO) { where.push('mf.meeting_date >= ?'); params.push(cutoffISO.slice(0, 10)); }
  if (attributedOnly) where.push('mf.speaker_person_id IS NOT NULL');
  const sql = `
    SELECT mf.id, mf.bank_key, mf.speaker_person_id, mf.speaker_name, mf.topic,
           mf.position, mf.sentiment, mf.evidence_quote, mf.meeting_date,
           mf.confidence_tier, p.role AS speaker_role, p.influence_score
    FROM meeting_facts mf
    LEFT JOIN persons p ON p.id = mf.speaker_person_id
    ${where.length ? 'WHERE ' + where.join(' AND ') : ''}
    ORDER BY mf.meeting_date DESC
    LIMIT ?
  `;
  const rows = db.prepare(sql).all(...params, limit);

  return rows.map(f => {
    const influence = f.influence_score || 0;
    // Significance = influence * 0.6 + sentiment-extremity boost
    const sentimentBoost = (f.sentiment === 'negative' || f.sentiment === 'positive') ? 2 : 0;
    const significance = Math.min(10, Math.round(influence * 0.6 + sentimentBoost + 1));
    return {
      id: hashId(['fact', f.id]),
      type: 'NEW_MEETING_FACT',
      bank_key: f.bank_key,
      timestamp: f.meeting_date + 'T12:00:00Z', // synthetic time mid-day
      significance,
      headline: `${f.speaker_name || 'Stakeholder'} on ${f.topic}: ${f.position?.slice(0, 80)}`,
      detail: {
        speaker: f.speaker_name,
        speaker_role: f.speaker_role,
        topic: f.topic,
        sentiment: f.sentiment,
        position: f.position,
      },
      source_grade: 'A', // meeting facts are AE-witnessed primary
      confidence_tier: f.confidence_tier,
      citation: {
        evidence_quote: f.evidence_quote,
        label: 'Meeting note',
      },
    };
  });
}

// ──────────────────────────────────────────────────────────────────────
// Stream 3: NEW_PATTERN
// ──────────────────────────────────────────────────────────────────────
function loadPatternEvents(db, { bankKey, bankKeys, cutoffISO, minConfidence = 'medium', limit = 30 }) {
  const where = [];
  const params = [];
  const scope = bankScopeClause('pm.bank_key', { bankKey, bankKeys });
  if (scope.sql) { where.push(scope.sql); params.push(...scope.params); }
  if (cutoffISO) { where.push('pm.detected_at >= ?'); params.push(cutoffISO); }
  const order = { high: 0, medium: 1, low: 2 };
  const allowedConfs = ['high', 'medium', 'low'].filter(c => order[c] <= order[minConfidence]);
  where.push(`pm.confidence IN (${allowedConfs.map(() => '?').join(',')})`);
  params.push(...allowedConfs);

  const rows = db.prepare(`
    SELECT pm.*, ds.source_grade AS signal_grade, ds.publisher_name AS signal_publisher,
           ds.source_url AS signal_url, ds.title AS signal_title,
           mf.speaker_name AS fact_speaker, mf.evidence_quote AS fact_quote
    FROM pattern_matches pm
    LEFT JOIN deal_signals ds ON ds.id = pm.external_signal_id
    LEFT JOIN meeting_facts mf ON mf.id = pm.internal_fact_id
    WHERE ${where.join(' AND ')}
    ORDER BY pm.detected_at DESC
    LIMIT ?
  `).all(...params, limit);

  // Sprint 4 audit fix: signal-side duplication amplifies in the feed when
  // multiple news outlets cover the same underlying event. We dedupe by
  // (fact_id, topic, pattern_type), keeping the variant with the highest
  // signal_grade (A > B > C > D), then by confidence (high > medium > low).
  // This collapses "CEO accelerating after [Omni / Computer Weekly / FinTech]"
  // into one canonical "CEO accelerating after [best-grade source]" event.
  const GRADE_RANK = { A: 4, B: 3, C: 2, D: 1 };
  const CONF_RANK = { high: 3, medium: 2, low: 1 };
  const dedupKey = (p) => `${p.internal_fact_id || ''}|${p.topic || ''}|${p.pattern_type || ''}`;
  const bestByKey = new Map();
  let dedupedCount = 0;
  for (const p of rows) {
    const key = dedupKey(p);
    if (!key.includes('||')) { // require both fact + topic + type for collapse
      const existing = bestByKey.get(key);
      if (!existing) { bestByKey.set(key, p); continue; }
      const a = (GRADE_RANK[p.signal_grade] || 0) * 10 + (CONF_RANK[p.confidence] || 0);
      const b = (GRADE_RANK[existing.signal_grade] || 0) * 10 + (CONF_RANK[existing.confidence] || 0);
      if (a > b) bestByKey.set(key, p);
      dedupedCount += 1;
    } else {
      // Pattern lacks fact_id or topic — surface as-is, no dedup
      bestByKey.set(p.id, p);
    }
  }

  return Array.from(bestByKey.values()).map(p => {
    const confBase = { high: 7, medium: 5, low: 3 }[p.confidence] || 3;
    const gradeBoost = { A: 2, B: 1, C: 0, D: -1 }[p.signal_grade] || 0;
    const significance = Math.min(10, Math.max(1, confBase + gradeBoost));
    return {
      id: hashId(['pattern', p.id]),
      type: 'NEW_PATTERN',
      bank_key: p.bank_key,
      timestamp: p.detected_at,
      significance,
      headline: p.summary,
      detail: {
        pattern_type: p.pattern_type,
        topic: p.topic,
        confidence: p.confidence,
        gap_days: p.time_gap_days,
        speaker: p.fact_speaker,
        signal_publisher: p.signal_publisher,
      },
      source_grade: p.signal_grade,
      confidence_tier: p.confidence === 'high' ? 1 : p.confidence === 'medium' ? 2 : 3,
      citation: {
        url: p.signal_url,
        label: `${p.fact_speaker || 'Stakeholder'} (meeting) × ${p.signal_publisher || 'signal'}`,
        evidence_quote: p.fact_quote,
      },
    };
  });
}

// ──────────────────────────────────────────────────────────────────────
// Stream 4: PULSE_DIFF — section-level deltas between consecutive pulses
// ──────────────────────────────────────────────────────────────────────
function loadPulseDiffEvents(db, { bankKey, bankKeys, cutoffISO, limit = 20 }) {
  // Pulses already store diff_summary in payload; we surface only diffs
  // generated since cutoffISO (using pulse.generated_at).
  const where = [];
  const params = [];
  const scope = bankScopeClause('account_id', { bankKey, bankKeys });
  if (scope.sql) { where.push(scope.sql); params.push(...scope.params); }
  if (cutoffISO) { where.push('generated_at >= ?'); params.push(cutoffISO); }
  const rows = db.prepare(`
    SELECT id, account_id AS bank_key, period_id, payload_json, generated_at
    FROM pulses
    ${where.length ? 'WHERE ' + where.join(' AND ') : ''}
    ORDER BY generated_at DESC
    LIMIT ?
  `).all(...params, limit);

  const events = [];
  for (const row of rows) {
    let payload;
    try { payload = JSON.parse(row.payload_json); } catch { continue; }
    const sections = payload.sections || {};
    for (const [sectionKey, section] of Object.entries(sections)) {
      const diff = section.diff_vs_previous;
      if (!diff || /no prior|first capture/i.test(diff)) continue;
      // Heuristic: significance from keyword density in diff text
      const isAdditive = /\bnew\b|\badded\b|\bgained\b|\bup\b/i.test(diff);
      const isLoss = /\blost\b|\bdropped\b|\bremoved\b|\bdown\b/i.test(diff);
      const significance = isLoss ? 6 : isAdditive ? 5 : 4;
      events.push({
        id: hashId(['pulsediff', row.id, sectionKey]),
        type: 'PULSE_DIFF',
        bank_key: row.bank_key,
        timestamp: row.generated_at,
        significance,
        headline: `${sectionKey.replace(/_/g, ' ')}: ${diff}`,
        detail: {
          period: row.period_id,
          section: sectionKey,
          diff,
        },
        source_grade: null,
        confidence_tier: null,
        citation: { label: `Pulse ${row.period_id}` },
      });
    }
  }
  return events;
}

// ──────────────────────────────────────────────────────────────────────
// Stream 5: STAKEHOLDER_DRIFT — sentiment ladder transitions
// ──────────────────────────────────────────────────────────────────────
function loadStakeholderDriftEvents(db, { bankKey, bankKeys, cutoffISO }) {
  // We compute drift cells whose latest fact falls within the lookback window.
  // The trend label itself is the event headline.
  const where = ['mf.speaker_person_id IS NOT NULL'];
  const params = [];
  const scope = bankScopeClause('mf.bank_key', { bankKey, bankKeys });
  if (scope.sql) { where.push(scope.sql); params.push(...scope.params); }
  if (cutoffISO) { where.push('mf.meeting_date >= ?'); params.push(cutoffISO.slice(0, 10)); }
  // Only emit drift events when a stakeholder has ≥2 facts on the same topic
  // (otherwise the change is just "new fact", already surfaced as NEW_MEETING_FACT)
  const rows = db.prepare(`
    SELECT mf.bank_key, mf.speaker_person_id, mf.speaker_name, mf.topic,
           p.role AS speaker_role, p.influence_score,
           COUNT(*) AS n_facts,
           MAX(mf.meeting_date) AS last_seen,
           MIN(mf.meeting_date) AS first_seen,
           GROUP_CONCAT(mf.sentiment, '|') AS sentiments_concat,
           GROUP_CONCAT(mf.meeting_date, '|') AS dates_concat
    FROM meeting_facts mf
    LEFT JOIN persons p ON p.id = mf.speaker_person_id
    WHERE ${where.join(' AND ')}
    GROUP BY mf.speaker_person_id, mf.topic
    HAVING COUNT(*) >= 2
  `).all(...params);

  const SENTIMENT_RANK = { negative: -1, mixed: 0, neutral: 0, positive: 1 };
  return rows.map(r => {
    const sentiments = r.sentiments_concat.split('|');
    const dates = r.dates_concat.split('|');
    const paired = sentiments.map((s, i) => ({ s, d: dates[i] }))
      .sort((a, b) => a.d.localeCompare(b.d));
    const first = SENTIMENT_RANK[paired[0].s] ?? 0;
    const last = SENTIMENT_RANK[paired[paired.length - 1].s] ?? 0;
    const delta = last - first;
    const trend = delta > 0 ? 'improving' : delta < 0 ? 'deteriorating' : 'stable';
    if (trend === 'stable') return null; // not an event-worthy delta
    const influence = r.influence_score || 0;
    const significance = Math.min(9, Math.round(5 + Math.abs(delta) + influence * 0.4));
    return {
      id: hashId(['drift', r.bank_key, r.speaker_person_id, r.topic, r.last_seen]),
      type: 'STAKEHOLDER_DRIFT',
      bank_key: r.bank_key,
      timestamp: r.last_seen + 'T12:00:00Z',
      significance,
      headline: `${r.speaker_name} ${trend} on ${r.topic} (n=${r.n_facts})`,
      detail: {
        speaker: r.speaker_name,
        speaker_role: r.speaker_role,
        topic: r.topic,
        trend,
        n_facts: r.n_facts,
        first_seen: r.first_seen,
        last_seen: r.last_seen,
      },
      source_grade: 'A',
      confidence_tier: 1,
      citation: { label: `${r.n_facts} attributed facts` },
    };
  }).filter(Boolean);
}

// ──────────────────────────────────────────────────────────────────────
// Stream 6: ENTITY_HISTORY — low-level field edits
// ──────────────────────────────────────────────────────────────────────
function loadEntityHistoryEvents(db, { bankKey, bankKeys, cutoffISO, limit = 30 }) {
  const where = [];
  const params = [];
  if (bankKey) {
    where.push('(entity_key = ? OR entity_key LIKE ?)');
    params.push(bankKey, `${bankKey}%`);
  } else if (Array.isArray(bankKeys) && bankKeys.length > 0) {
    // Match either exact entity_key or LIKE prefix for any bank in the list
    const clauses = bankKeys.flatMap(() => ['entity_key = ?', 'entity_key LIKE ?']);
    where.push(`(${clauses.join(' OR ')})`);
    bankKeys.forEach(bk => { params.push(bk, `${bk}%`); });
  }
  if (cutoffISO) { where.push('changed_at >= ?'); params.push(cutoffISO); }
  let rows = [];
  try {
    rows = db.prepare(`
      SELECT id, entity_type, entity_key, field_path, old_value, new_value, changed_at, source
      FROM entity_history
      ${where.length ? 'WHERE ' + where.join(' AND ') : ''}
      ORDER BY changed_at DESC
      LIMIT ?
    `).all(...params, limit);
  } catch { return []; }

  return rows.map(h => {
    // Heuristic: significance based on field criticality
    const critical = /role|title|status|score|stage|engagement/i.test(h.field_path);
    const significance = critical ? 4 : 2;
    const oldVal = (h.old_value || '').slice(0, 30);
    const newVal = (h.new_value || '').slice(0, 30);
    return {
      id: hashId(['history', h.id]),
      type: 'ENTITY_HISTORY',
      bank_key: h.entity_key, // approximation; for person rows this is the bank if entity_key encodes it
      timestamp: h.changed_at,
      significance,
      headline: `${h.entity_type}.${h.field_path}: ${oldVal || '(empty)'} → ${newVal}`,
      detail: {
        entity_type: h.entity_type,
        entity_key: h.entity_key,
        field_path: h.field_path,
        old_value: h.old_value,
        new_value: h.new_value,
        source: h.source,
      },
      source_grade: 'A',
      confidence_tier: 1,
      citation: { label: `Edit by ${h.source || 'system'}` },
    };
  });
}

// ──────────────────────────────────────────────────────────────────────
// Public API
// ──────────────────────────────────────────────────────────────────────

/**
 * Get the unified change feed for one bank, or for the whole portfolio if
 * bankKey is null. Events are sorted DESC by timestamp by default; pass
 * `sort='significance'` to rank by significance instead.
 *
 * @param {Database} db
 * @param {object} options
 *   bankKey:       string|null (null = portfolio-wide)
 *   lookbackDays:  number       (default 30)
 *   minSignificance: number     (default 0)
 *   sort:          'time'|'significance' (default 'time')
 *   limit:         number       (default 100)
 *   include:       array of stream names — defaults to all 6
 * @returns {Array<ChangeEvent>}
 */
export function getChangeFeed(db, options = {}) {
  const {
    bankKey = null,
    bankKeys = null, // Region/country pages pass a list of banks here
    lookbackDays = DEFAULT_LOOKBACK_DAYS,
    minSignificance = 0,
    sort = 'time',
    limit = 100,
    include = ['NEW_SIGNAL', 'NEW_MEETING_FACT', 'NEW_PATTERN', 'PULSE_DIFF', 'STAKEHOLDER_DRIFT', 'ENTITY_HISTORY'],
  } = options;

  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - lookbackDays);
  const cutoffISO = cutoff.toISOString();

  const scope = { bankKey, bankKeys, cutoffISO };
  const events = [];
  if (include.includes('NEW_SIGNAL'))        events.push(...loadSignalEvents(db, scope));
  if (include.includes('NEW_MEETING_FACT'))  events.push(...loadMeetingFactEvents(db, scope));
  if (include.includes('NEW_PATTERN'))       events.push(...loadPatternEvents(db, scope));
  if (include.includes('PULSE_DIFF'))        events.push(...loadPulseDiffEvents(db, scope));
  if (include.includes('STAKEHOLDER_DRIFT')) events.push(...loadStakeholderDriftEvents(db, scope));
  if (include.includes('ENTITY_HISTORY'))    events.push(...loadEntityHistoryEvents(db, scope));

  const filtered = events.filter(e => e.significance >= minSignificance);
  filtered.sort((a, b) => {
    if (sort === 'significance') return b.significance - a.significance || (b.timestamp || '').localeCompare(a.timestamp || '');
    return (b.timestamp || '').localeCompare(a.timestamp || '');
  });
  return filtered.slice(0, limit);
}

/**
 * Per-type counts for the lookback window. Useful as a "header strip" on the
 * change feed UI: "12 new signals · 3 patterns · 5 facts · 8 pulse diffs".
 */
export function getChangeFeedCounts(db, options = {}) {
  const events = getChangeFeed(db, { ...options, limit: 10000 });
  const counts = { total: events.length };
  for (const e of events) counts[e.type] = (counts[e.type] || 0) + 1;
  return counts;
}
