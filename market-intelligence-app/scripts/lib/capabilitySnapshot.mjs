/**
 * Capability Snapshot — quick capability assessment without full engagement
 * ────────────────────────────────────────────────────────────────────────
 * Lightweight version of the parent Cortex capability-assessment agent.
 * Useful for AE qualification ("does this bank look like a fit?") or VC
 * scoping ("how big is the gap before I commit to a full engagement?").
 *
 * Composes existing Nova data:
 *   - bank.data.backbase_qualification (deal size, timing, risk)
 *   - bank.data.operational_profile (assets, customers, employees, CTI)
 *   - meeting_facts (mentioned topics → capability surface)
 *   - patterns (corroborated capability concerns)
 *   - country fintech_landscape (vendor maturity context)
 *
 * Output: a 1-page snapshot per bank with rough capability scores per
 * dimension (channels, data, AI, operations, customer, regulatory) on a
 * 1-5 maturity scale, plus 3-5 "biggest gaps" with evidence trace.
 */

const CAPABILITY_DIMENSIONS = [
  { id: 'channels', label: 'Digital channels', topics: ['technical', 'timeline'] },
  { id: 'data', label: 'Data & analytics', topics: ['technical'] },
  { id: 'ai', label: 'AI / automation', topics: ['technical', 'vendors'] },
  { id: 'operations', label: 'Operational excellence', topics: ['blockers', 'budget', 'vendors'] },
  { id: 'customer', label: 'Customer experience', topics: ['other', 'politics'] },
  { id: 'regulatory', label: 'Regulatory / risk', topics: ['blockers'] },
];

const SENTIMENT_TO_MATURITY = {
  positive: 4,   // they say it's good → likely current
  neutral:  3,
  mixed:    2,
  negative: 1,   // they raise it as a problem → gap
};

function computeDimensionScore(facts, topics) {
  const relevant = facts.filter(f => topics.includes(f.topic));
  if (relevant.length === 0) return { score: null, n_facts: 0 };
  const total = relevant.reduce((s, f) => s + (SENTIMENT_TO_MATURITY[f.sentiment] || 3), 0);
  return {
    score: +(total / relevant.length).toFixed(1),
    n_facts: relevant.length,
  };
}

export function generateCapabilitySnapshot(db, bankKey) {
  const bank = db.prepare('SELECT * FROM banks WHERE key = ?').get(bankKey);
  if (!bank) throw new Error(`Bank not found: ${bankKey}`);
  const bankData = JSON.parse(bank.data || '{}');

  // Pull all attributed facts for capability inference
  const facts = db.prepare(`
    SELECT speaker_name, topic, position, sentiment, evidence_quote, meeting_date
    FROM meeting_facts WHERE bank_key = ? AND speaker_person_id IS NOT NULL
  `).all(bankKey);

  // Pattern-derived gaps
  const patterns = db.prepare(`
    SELECT topic, summary, confidence FROM pattern_matches
    WHERE bank_key = ? AND confidence IN ('high','medium')
  `).all(bankKey);

  // Compute maturity per dimension
  const dimensions = CAPABILITY_DIMENSIONS.map(d => ({
    id: d.id,
    label: d.label,
    ...computeDimensionScore(facts, d.topics),
  }));

  // Identify biggest gaps — dimensions with low score + non-zero facts
  const gaps = dimensions
    .filter(d => d.score != null && d.score < 3)
    .sort((a, b) => a.score - b.score)
    .slice(0, 5)
    .map(g => {
      const supportingFacts = facts.filter(f =>
        CAPABILITY_DIMENSIONS.find(d => d.id === g.id).topics.includes(f.topic) &&
        ['negative', 'mixed'].includes(f.sentiment)
      ).slice(0, 2);
      const supportingPatterns = patterns.filter(p =>
        CAPABILITY_DIMENSIONS.find(d => d.id === g.id).topics.includes(p.topic)
      ).slice(0, 2);
      return {
        dimension: g.id,
        label: g.label,
        maturity_score: g.score,
        evidence_facts: supportingFacts,
        evidence_patterns: supportingPatterns,
      };
    });

  return {
    bank: {
      key: bankKey,
      name: bank.bank_name,
      country: bank.country,
      operational_profile: bankData.operational_profile || null,
      backbase_qualification: bankData.backbase_qualification || null,
    },
    snapshot_date: new Date().toISOString(),
    dimensions,
    biggest_gaps: gaps,
    facts_used: facts.length,
    patterns_used: patterns.length,
    note: facts.length === 0
      ? 'No attributed meeting facts on file — capability scores are unavailable. Log a discovery meeting first.'
      : facts.length < 5
        ? 'Limited attributed facts — capability scores are directional, not statistical.'
        : null,
  };
}
