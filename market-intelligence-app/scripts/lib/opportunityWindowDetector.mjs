/**
 * Opportunity Window Detector — multi-stream pattern detector
 * ───────────────────────────────────────────────────────────
 * Detects co-occurring patterns that indicate a "window of opportunity"
 * has opened on a bank — multiple independent streams converging within
 * a recent time window.
 *
 * Pre-defined window types:
 *   - REPLATFORM_WINDOW: new CIO/CTO + recent regulatory pressure
 *   - VENDOR_DISPLACEMENT_WINDOW: vendor pattern + budget thaw + competitor weakness
 *   - DIGITAL_INVESTMENT_WINDOW: budget signals + leadership endorsement + deteriorating customer NPS
 *   - REGULATORY_FORCING: regulatory urgency + capability gap + active engagement
 *
 * Pure structural composition over existing tables — no LLM in detection
 * loop. Same input → same windows. Each detection cites the constituent
 * signals so AE can verify.
 */

const DEFAULT_LOOKBACK_DAYS = 90;

export function detectOpportunityWindows(db, bankKey, options = {}) {
  const { lookbackDays = DEFAULT_LOOKBACK_DAYS } = options;
  const cutoff = new Date(); cutoff.setDate(cutoff.getDate() - lookbackDays);
  const cutoffISO = cutoff.toISOString();
  const windows = [];

  // ── REPLATFORM_WINDOW: new CIO/CTO + recent regulatory pressure ──
  const newTechLeader = db.prepare(`
    SELECT id, title, source_url, detected_at FROM deal_signals
    WHERE deal_id = ? AND signal_category = 'stakeholder' AND COALESCE(is_demo, 0) = 0
      AND detected_at >= ? AND (title LIKE '%CIO%' OR title LIKE '%CTO%' OR title LIKE '%Chief Technology%' OR title LIKE '%Chief Information%' OR title LIKE '%Chief Digital%')
  `).all(bankKey, cutoffISO);
  const regulatorySignal = db.prepare(`
    SELECT id, title, source_url, detected_at FROM deal_signals
    WHERE deal_id = ? AND signal_category = 'regulatory' AND COALESCE(is_demo, 0) = 0
      AND detected_at >= ? AND severity IN ('urgent', 'attention')
  `).all(bankKey, cutoffISO);
  if (newTechLeader.length > 0 && regulatorySignal.length > 0) {
    windows.push({
      type: 'REPLATFORM_WINDOW',
      title: 'Replatform window — new tech leader + regulatory pressure',
      detail: `New CIO/CTO appointed and recent urgent/attention regulatory signal in last ${lookbackDays}d. Classic re-platform trigger combo.`,
      significance: 9,
      evidence: {
        leader_change: newTechLeader.slice(0, 2),
        regulatory: regulatorySignal.slice(0, 2),
      },
    });
  }

  // ── VENDOR_DISPLACEMENT_WINDOW: vendor pattern + budget signals ──
  const vendorPatterns = db.prepare(`
    SELECT pm.id, pm.summary, pm.detected_at, ds.source_url FROM pattern_matches pm
    LEFT JOIN deal_signals ds ON ds.id = pm.external_signal_id
    WHERE pm.bank_key = ? AND pm.topic = 'vendors' AND pm.confidence IN ('high','medium')
      AND pm.detected_at >= ?
  `).all(bankKey, cutoffISO);
  const budgetFacts = db.prepare(`
    SELECT id, position, evidence_quote, meeting_date FROM meeting_facts
    WHERE bank_key = ? AND topic = 'budget' AND sentiment IN ('positive','neutral')
      AND meeting_date >= ?
  `).all(bankKey, cutoffISO.slice(0, 10));
  if (vendorPatterns.length > 0 && budgetFacts.length > 0) {
    windows.push({
      type: 'VENDOR_DISPLACEMENT_WINDOW',
      title: 'Vendor displacement window — vendor pattern + budget capacity',
      detail: `Stakeholder talked about vendors AND positive budget signals in last ${lookbackDays}d. Capacity + intent for change.`,
      significance: 8,
      evidence: {
        vendor_patterns: vendorPatterns.slice(0, 2),
        budget_facts: budgetFacts.slice(0, 2),
      },
    });
  }

  // ── DIGITAL_INVESTMENT_WINDOW: budget + leadership endorsement + customer pain ──
  const leadershipEndorsement = db.prepare(`
    SELECT mf.id, mf.position, mf.evidence_quote, mf.meeting_date, p.role
    FROM meeting_facts mf LEFT JOIN persons p ON p.id = mf.speaker_person_id
    WHERE mf.bank_key = ? AND mf.topic IN ('technical', 'timeline')
      AND mf.sentiment = 'positive' AND mf.confidence_tier = 1
      AND mf.meeting_date >= ?
  `).all(bankKey, cutoffISO.slice(0, 10));
  if (budgetFacts.length > 0 && leadershipEndorsement.length > 0) {
    windows.push({
      type: 'DIGITAL_INVESTMENT_WINDOW',
      title: 'Digital investment window — budget + leadership endorsement',
      detail: `Positive budget signal AND attributed positive leadership stance on technical/timeline topics in last ${lookbackDays}d.`,
      significance: 7,
      evidence: {
        budget_facts: budgetFacts.slice(0, 2),
        leadership: leadershipEndorsement.slice(0, 2),
      },
    });
  }

  // ── REGULATORY_FORCING: regulatory urgency + active engagement ──
  const activeEngagements = db.prepare(`
    SELECT id, title, state FROM engagements
    WHERE bank_key = ? AND state IN ('discovery','assessment','delivered')
  `).all(bankKey);
  if (regulatorySignal.length > 0 && activeEngagements.length > 0) {
    windows.push({
      type: 'REGULATORY_FORCING',
      title: 'Regulatory forcing event — active engagement context',
      detail: `Recent regulatory urgency AND VC engagement is in motion. Forcing function for decision velocity.`,
      significance: 8,
      evidence: {
        regulatory: regulatorySignal.slice(0, 2),
        engagements: activeEngagements,
      },
    });
  }

  windows.sort((a, b) => b.significance - a.significance);
  return windows;
}

export function detectAllPortfolioWindows(db, options = {}) {
  const banks = db.prepare(`SELECT key, bank_name FROM banks WHERE country != '_competitor' OR country IS NULL`).all();
  const out = [];
  for (const b of banks) {
    const windows = detectOpportunityWindows(db, b.key, options);
    if (windows.length > 0) {
      out.push({ bank_key: b.key, bank_name: b.bank_name, windows });
    }
  }
  return out;
}
