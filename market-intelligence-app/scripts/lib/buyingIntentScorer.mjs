/**
 * Buying Intent Scorer — composite intent score per bank
 * ──────────────────────────────────────────────────────
 * Scores 0-100 based on multiple signal streams:
 *   - Recent A/B-grade signal density (up to 25 pts)
 *   - Improving stakeholder drift (up to 15 pts)
 *   - High-confidence corroborated patterns (up to 20 pts)
 *   - Recent attributed positive meeting facts (up to 20 pts)
 *   - Stakeholder appointments at decision-making roles (up to 10 pts)
 *   - Active VC engagement (up to 10 pts)
 *
 * Pure deterministic composition over existing tables — no LLM. Same
 * inputs → same score. Designed for AE morning triage: "which deals
 * to push this week".
 */

export function computeBuyingIntent(db, bankKey, options = {}) {
  const { lookbackDays = 60 } = options;
  const cutoff = new Date(); cutoff.setDate(cutoff.getDate() - lookbackDays);
  const cutoffISO = cutoff.toISOString();

  const components = {};

  // 1. Recent A/B-grade signal density
  const sigCounts = db.prepare(`
    SELECT source_grade, COUNT(*) c FROM deal_signals
    WHERE deal_id = ? AND COALESCE(is_demo, 0) = 0 AND detected_at >= ?
    GROUP BY source_grade
  `).all(bankKey, cutoffISO);
  const aCount = sigCounts.find(r => r.source_grade === 'A')?.c || 0;
  const bCount = sigCounts.find(r => r.source_grade === 'B')?.c || 0;
  components.signals = Math.min(25, aCount * 5 + bCount * 2);

  // 2. Improving stakeholder drift
  const driftRows = db.prepare(`
    SELECT mf.speaker_person_id, mf.topic,
           GROUP_CONCAT(mf.sentiment, '|') AS sentiments,
           GROUP_CONCAT(mf.meeting_date, '|') AS dates
    FROM meeting_facts mf
    WHERE mf.bank_key = ? AND mf.speaker_person_id IS NOT NULL
    GROUP BY mf.speaker_person_id, mf.topic
    HAVING COUNT(*) >= 2
  `).all(bankKey);
  const RANK = { negative: -1, mixed: 0, neutral: 0, positive: 1 };
  let improving = 0;
  for (const r of driftRows) {
    const sentiments = r.sentiments.split('|');
    const dates = r.dates.split('|');
    const paired = sentiments.map((s, i) => ({ s, d: dates[i] })).sort((a, b) => a.d.localeCompare(b.d));
    const first = RANK[paired[0].s] ?? 0;
    const last = RANK[paired[paired.length - 1].s] ?? 0;
    if (last > first) improving += 1;
  }
  components.drift_improving = Math.min(15, improving * 5);

  // 3. High-confidence corroborated patterns
  const patternCounts = db.prepare(`
    SELECT confidence, COUNT(*) c FROM pattern_matches
    WHERE bank_key = ? AND detected_at >= ?
    GROUP BY confidence
  `).all(bankKey, cutoffISO);
  const highConf = patternCounts.find(r => r.confidence === 'high')?.c || 0;
  const medConf = patternCounts.find(r => r.confidence === 'medium')?.c || 0;
  components.patterns = Math.min(20, highConf * 6 + medConf * 2);

  // 4. Recent attributed positive meeting facts
  const positiveAttribFacts = db.prepare(`
    SELECT COUNT(*) c FROM meeting_facts
    WHERE bank_key = ? AND speaker_person_id IS NOT NULL
      AND sentiment = 'positive' AND meeting_date >= ?
  `).get(bankKey, cutoffISO.slice(0, 10))?.c || 0;
  components.positive_facts = Math.min(20, positiveAttribFacts * 4);

  // 5. Decision-maker stakeholder appointments
  const apptCount = db.prepare(`
    SELECT COUNT(*) c FROM deal_signals
    WHERE deal_id = ? AND signal_category = 'stakeholder'
      AND COALESCE(is_demo, 0) = 0 AND detected_at >= ?
      AND (title LIKE '%CEO%' OR title LIKE '%CIO%' OR title LIKE '%CTO%' OR title LIKE '%CFO%')
  `).get(bankKey, cutoffISO)?.c || 0;
  components.dmu_changes = Math.min(10, apptCount * 5);

  // 6. Active VC engagement
  const activeEng = db.prepare(`
    SELECT COUNT(*) c FROM engagements
    WHERE bank_key = ? AND state != 'closed'
  `).get(bankKey)?.c || 0;
  components.active_engagement = Math.min(10, activeEng * 10);

  const total = Object.values(components).reduce((s, v) => s + v, 0);
  const tier = total >= 70 ? 'hot' : total >= 45 ? 'warm' : total >= 20 ? 'lukewarm' : 'cold';

  return {
    bank_key: bankKey,
    score: total,
    tier,
    components,
    lookback_days: lookbackDays,
  };
}

export function rankPortfolioByIntent(db, options = {}) {
  const banks = db.prepare(`SELECT key FROM banks WHERE country != '_competitor' OR country IS NULL`).all();
  return banks
    .map(b => computeBuyingIntent(db, b.key, options))
    .sort((a, b) => b.score - a.score);
}
