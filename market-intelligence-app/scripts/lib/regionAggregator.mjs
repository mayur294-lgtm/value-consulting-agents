/**
 * Region Aggregator — region/country improvements (post-B-series)
 * ───────────────────────────────────────────────────────────────
 * Aggregates Sprint 1-5 intelligence across a SET of banks (a market/region
 * or a single country). Used by both MarketPage and CountryPage to surface
 * the same Sprint-era data the bank/portfolio pages already expose.
 *
 * Why a separate aggregator (instead of just calling existing libs):
 *   - Region-level rollups have different display semantics (top-N across
 *     banks, distribution histograms, computed-opportunity clusters)
 *   - Composes existing functions; no new ranking logic
 *   - Shared library so MarketPage and CountryPage stay DRY
 *
 * All functions are pure transformations over the existing tables. No LLM,
 * no novel scoring — just multi-bank views of what we already store.
 */

import { getPatternsForBank } from './crossReferenceEngine.mjs';
import { getStakeholderDrift } from './stakeholderDrift.mjs';

const TIER_GRADE_RANK = { A: 4, B: 3, C: 2, D: 1 };
const CONF_RANK = { high: 3, medium: 2, low: 1 };

/**
 * Resolve a region key (e.g. "nordics") to its banks via the markets table.
 * The markets.data JSON has a `countries` array; we cross-reference that
 * against banks.country to get the bank-key list.
 */
export function getBanksForRegion(db, marketKey) {
  const market = db.prepare('SELECT data FROM markets WHERE key = ?').get(marketKey);
  if (!market) return [];
  let parsed;
  try { parsed = JSON.parse(market.data); } catch { return []; }
  const countries = (parsed?.countries || []).map(c => c.name).filter(Boolean);
  if (countries.length === 0) return [];
  const placeholders = countries.map(() => '?').join(',');
  return db.prepare(`
    SELECT key, bank_name, country FROM banks
    WHERE country IN (${placeholders}) OR ${countries.map(() => 'country LIKE ?').join(' OR ')}
  `).all(...countries, ...countries.map(c => `${c}%`));
}

/**
 * Resolve a country name to its banks. Tolerant of pan-Nordic suffixes
 * ("Sweden / Pan-Nordic", "Sweden (Pan-European operations)").
 */
export function getBanksForCountry(db, countryName) {
  return db.prepare(`
    SELECT key, bank_name, country FROM banks
    WHERE country = ? OR country LIKE ?
  `).all(countryName, `${countryName}%`);
}

// ──────────────────────────────────────────────────────────────────────
// Patterns rollup — top corroborated patterns across the bank set
// ──────────────────────────────────────────────────────────────────────

/**
 * Returns top-N patterns across a set of banks, ranked by (signal_grade,
 * confidence). Shape mirrors what the per-bank patterns endpoint returns,
 * so UI components can be reused. Each pattern carries its bank_name for
 * display.
 */
export function getRegionPatterns(db, bankKeys, options = {}) {
  const { limit = 12, minConfidence = 'medium' } = options;
  if (!bankKeys || bankKeys.length === 0) return [];
  const allowedConfs = ['high', 'medium', 'low'].filter(c => CONF_RANK[c] >= CONF_RANK[minConfidence]);
  const placeholders = bankKeys.map(() => '?').join(',');
  const confPlace = allowedConfs.map(() => '?').join(',');

  const rows = db.prepare(`
    SELECT
      pm.*,
      b.bank_name,
      mf.position AS fact_position,
      mf.sentiment AS fact_sentiment,
      mf.speaker_name AS fact_speaker_name,
      mf.meeting_date AS fact_meeting_date,
      ds.title AS signal_title,
      ds.detected_at AS signal_detected_at,
      ds.source_url AS signal_source_url,
      ds.source_grade AS signal_grade,
      ds.publisher_name AS signal_publisher
    FROM pattern_matches pm
    LEFT JOIN banks b ON b.key = pm.bank_key
    LEFT JOIN meeting_facts mf ON mf.id = pm.internal_fact_id
    LEFT JOIN deal_signals ds ON ds.id = pm.external_signal_id
    WHERE pm.bank_key IN (${placeholders})
      AND pm.confidence IN (${confPlace})
    ORDER BY
      CASE ds.source_grade WHEN 'A' THEN 4 WHEN 'B' THEN 3 WHEN 'C' THEN 2 WHEN 'D' THEN 1 ELSE 0 END DESC,
      CASE pm.confidence WHEN 'high' THEN 3 WHEN 'medium' THEN 2 ELSE 1 END DESC,
      pm.detected_at DESC
    LIMIT ?
  `).all(...bankKeys, ...allowedConfs, limit);
  return rows;
}

// ──────────────────────────────────────────────────────────────────────
// Source grade distribution — A/B/C/D histogram across the bank set
// ──────────────────────────────────────────────────────────────────────

export function getRegionGradeDistribution(db, bankKeys) {
  if (!bankKeys || bankKeys.length === 0) {
    return { A: 0, B: 0, C: 0, D: 0, total: 0, ungraded: 0 };
  }
  const placeholders = bankKeys.map(() => '?').join(',');
  const rows = db.prepare(`
    SELECT source_grade AS grade, COUNT(*) AS count
    FROM deal_signals
    WHERE deal_id IN (${placeholders}) AND COALESCE(is_demo, 0) = 0
    GROUP BY source_grade
  `).all(...bankKeys);
  const out = { A: 0, B: 0, C: 0, D: 0, ungraded: 0 };
  let total = 0;
  for (const r of rows) {
    if (r.grade && out.hasOwnProperty(r.grade)) out[r.grade] = r.count;
    else out.ungraded += r.count;
    total += r.count;
  }
  return { ...out, total };
}

// ──────────────────────────────────────────────────────────────────────
// Drift heatmap — which banks have the most stakeholder drift activity
// ──────────────────────────────────────────────────────────────────────

/**
 * Returns one row per bank in the region: counts of attributed facts,
 * unique stakeholders quoted, and trend distribution. Used to spot which
 * banks have the densest meeting intelligence.
 */
export function getRegionDriftHeatmap(db, bankKeys) {
  if (!bankKeys || bankKeys.length === 0) return [];
  const placeholders = bankKeys.map(() => '?').join(',');
  const rows = db.prepare(`
    SELECT
      mf.bank_key,
      b.bank_name,
      b.country,
      COUNT(*) AS total_facts,
      COUNT(DISTINCT mf.speaker_person_id) AS attributed_speakers,
      COUNT(DISTINCT mf.topic) AS topics_touched,
      MAX(mf.meeting_date) AS last_fact_date
    FROM meeting_facts mf
    LEFT JOIN banks b ON b.key = mf.bank_key
    WHERE mf.bank_key IN (${placeholders})
    GROUP BY mf.bank_key
  `).all(...bankKeys);

  // Compute trend mix per bank using the existing drift library
  return rows.map(row => {
    const cells = getStakeholderDrift(db, row.bank_key, { includeUnattributed: false });
    const trends = { improving: 0, deteriorating: 0, mixed: 0, stable: 0, single_point: 0 };
    cells.forEach(c => { trends[c.trend] = (trends[c.trend] || 0) + 1; });
    return {
      bank_key: row.bank_key,
      bank_name: row.bank_name,
      country: row.country,
      total_facts: row.total_facts,
      attributed_speakers: row.attributed_speakers,
      topics_touched: row.topics_touched,
      last_fact_date: row.last_fact_date,
      trends,
      density_score: row.total_facts * 1.0 + row.attributed_speakers * 0.5 + row.topics_touched * 0.3,
    };
  }).sort((a, b) => b.density_score - a.density_score);
}

// ──────────────────────────────────────────────────────────────────────
// Computed opportunities — Tier 3: replace static "key opportunities"
// with data-driven clusters
// ──────────────────────────────────────────────────────────────────────

/**
 * Detects opportunity clusters from signal/pattern density. Returns a small
 * list of "data-driven" opportunities the AE should pay attention to.
 *
 * Cluster types:
 *   - REGULATORY_WAVE: ≥3 banks have urgent regulatory signals in last 60d
 *   - VENDOR_CHURN: ≥3 banks have vendor patterns (corroborates/contradicts)
 *   - LEADERSHIP_FLUX: ≥3 banks have stakeholder appointments/departures
 *   - BUDGET_THAW: ≥3 banks have positive budget meeting facts in last 60d
 *   - DETERIORATING_ENGAGEMENT: ≥2 banks with drift on engagement-relevant topics
 */
export function getComputedOpportunities(db, bankKeys, options = {}) {
  const { withinDays = 60 } = options;
  if (!bankKeys || bankKeys.length === 0) return [];
  const cutoff = new Date(); cutoff.setDate(cutoff.getDate() - withinDays);
  const cutoffISO = cutoff.toISOString();
  const placeholders = bankKeys.map(() => '?').join(',');
  const opportunities = [];

  // 1. Regulatory wave
  const regBanks = db.prepare(`
    SELECT DISTINCT deal_id AS bank_key, b.bank_name FROM deal_signals
    LEFT JOIN banks b ON b.key = deal_id
    WHERE deal_id IN (${placeholders})
      AND signal_category = 'regulatory'
      AND severity IN ('urgent', 'attention')
      AND detected_at >= ?
      AND COALESCE(is_demo, 0) = 0
  `).all(...bankKeys, cutoffISO);
  if (regBanks.length >= 3) {
    opportunities.push({
      type: 'REGULATORY_WAVE',
      title: 'Regulatory pressure cluster',
      detail: `${regBanks.length} banks have urgent/attention regulatory signals in the last ${withinDays} days. Likely AML, supervisory, or sanction wave.`,
      banks: regBanks,
      significance: Math.min(10, 5 + regBanks.length),
    });
  }

  // 2. Vendor churn
  const vendorPatterns = db.prepare(`
    SELECT DISTINCT pm.bank_key, b.bank_name FROM pattern_matches pm
    LEFT JOIN banks b ON b.key = pm.bank_key
    WHERE pm.bank_key IN (${placeholders}) AND pm.topic = 'vendors'
      AND pm.confidence IN ('high', 'medium')
  `).all(...bankKeys);
  if (vendorPatterns.length >= 2) {
    opportunities.push({
      type: 'VENDOR_CHURN',
      title: 'Vendor strategy in motion',
      detail: `${vendorPatterns.length} banks have corroborated patterns about vendor decisions. Discovery + competitive displacement window.`,
      banks: vendorPatterns,
      significance: Math.min(10, 4 + vendorPatterns.length),
    });
  }

  // 3. Leadership flux
  const apptBanks = db.prepare(`
    SELECT DISTINCT deal_id AS bank_key, b.bank_name FROM deal_signals
    LEFT JOIN banks b ON b.key = deal_id
    WHERE deal_id IN (${placeholders})
      AND signal_category = 'stakeholder'
      AND detected_at >= ?
      AND COALESCE(is_demo, 0) = 0
  `).all(...bankKeys, cutoffISO);
  if (apptBanks.length >= 3) {
    opportunities.push({
      type: 'LEADERSHIP_FLUX',
      title: 'Leadership turnover cluster',
      detail: `${apptBanks.length} banks have stakeholder signals (appointments / departures) in the last ${withinDays} days. New-relationship windows opening.`,
      banks: apptBanks,
      significance: Math.min(10, 3 + apptBanks.length),
    });
  }

  // 4. Budget signals
  const budgetBanks = db.prepare(`
    SELECT DISTINCT mf.bank_key, b.bank_name FROM meeting_facts mf
    LEFT JOIN banks b ON b.key = mf.bank_key
    WHERE mf.bank_key IN (${placeholders})
      AND mf.topic = 'budget'
      AND mf.sentiment IN ('positive', 'neutral')
      AND mf.meeting_date >= ?
  `).all(...bankKeys, cutoffISO.slice(0, 10));
  if (budgetBanks.length >= 2) {
    opportunities.push({
      type: 'BUDGET_THAW',
      title: 'Budget conversations open',
      detail: `${budgetBanks.length} banks have positive/neutral budget facts in the last ${withinDays} days. Capacity for capex conversation exists.`,
      banks: budgetBanks,
      significance: Math.min(9, 4 + budgetBanks.length),
    });
  }

  // 5. Deteriorating engagement (cross-bank stakeholder drift)
  const deterioratingPatterns = bankKeys.flatMap(bk => {
    const cells = getStakeholderDrift(db, bk, { includeUnattributed: false });
    return cells.filter(c => c.trend === 'deteriorating').map(c => ({ bank_key: bk, ...c }));
  });
  const deterioratingBanks = [...new Set(deterioratingPatterns.map(p => p.bank_key))];
  if (deterioratingBanks.length >= 2) {
    opportunities.push({
      type: 'DETERIORATING_ENGAGEMENT',
      title: 'Stakeholder positions deteriorating',
      detail: `${deterioratingBanks.length} banks show deteriorating sentiment on tracked topics. Re-engagement priority.`,
      banks: deterioratingBanks.map(bk => ({ bank_key: bk, bank_name: bk })),
      significance: Math.min(9, 4 + deterioratingBanks.length),
    });
  }

  opportunities.sort((a, b) => b.significance - a.significance);
  return opportunities;
}

// ──────────────────────────────────────────────────────────────────────
// Region rollup of pulse engagement scores
// ──────────────────────────────────────────────────────────────────────

/**
 * Reads each bank's most recent pulse for the given period and aggregates
 * engagement scores. Returns:
 *   { avg_score, n_pulses, score_change_vs_prior, banks: [{key, name, q1, q2, delta}] }
 */
export function getRegionEngagementSummary(db, bankKeys, options = {}) {
  const { from = '2026-Q1', to = '2026-Q2' } = options;
  if (!bankKeys || bankKeys.length === 0) return null;
  const placeholders = bankKeys.map(() => '?').join(',');
  const rows = db.prepare(`
    SELECT account_id AS bank_key, period_id, payload_json
    FROM pulses
    WHERE account_id IN (${placeholders}) AND period_id IN (?, ?)
  `).all(...bankKeys, from, to);

  const byBank = new Map();
  for (const row of rows) {
    let payload;
    try { payload = JSON.parse(row.payload_json); } catch { continue; }
    const score = payload?.sections?.engagement_trend?.data?.score;
    if (typeof score !== 'number') continue;
    if (!byBank.has(row.bank_key)) byBank.set(row.bank_key, { bank_key: row.bank_key });
    byBank.get(row.bank_key)[row.period_id] = score;
  }
  const banks = Array.from(byBank.values()).map(b => ({
    ...b,
    delta: (b[from] != null && b[to] != null) ? +(b[to] - b[from]).toFixed(2) : null,
  }));
  const fromScores = banks.filter(b => b[from] != null).map(b => b[from]);
  const toScores = banks.filter(b => b[to] != null).map(b => b[to]);
  const avg = arr => arr.length ? arr.reduce((s, x) => s + x, 0) / arr.length : null;
  return {
    from,
    to,
    n_pulses: banks.length,
    avg_from: fromScores.length ? +avg(fromScores).toFixed(2) : null,
    avg_to: toScores.length ? +avg(toScores).toFixed(2) : null,
    avg_delta: (fromScores.length && toScores.length) ? +(avg(toScores) - avg(fromScores)).toFixed(2) : null,
    n_improved: banks.filter(b => b.delta != null && b.delta > 0).length,
    n_deteriorated: banks.filter(b => b.delta != null && b.delta < 0).length,
    banks: banks.sort((a, b) => (b.delta ?? 0) - (a.delta ?? 0)),
  };
}
