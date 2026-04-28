/**
 * Engagement Similarity Finder — find prior engagements similar to a bank
 * ──────────────────────────────────────────────────────────────────────
 * For a target bank, finds prior CLOSED engagements (won + lost) at OTHER
 * banks with similar signal/pattern/drift profiles. Knowledge re-use for
 * VCs: "we've seen this situation before — here's what worked."
 *
 * Similarity vector (per bank):
 *   - Country (exact match = +3)
 *   - Topic mix from meeting_facts (cosine similarity over topic vector)
 *   - Pattern types observed (jaccard over {corroborates, contradicts, evolves})
 *   - Operational scale (similar asset size = +1)
 *
 * Pure deterministic — no LLM. Same inputs → same matches.
 */

const TOPICS = ['budget', 'vendors', 'timeline', 'politics', 'technical', 'blockers', 'other'];

function buildBankProfile(db, bankKey) {
  const bank = db.prepare('SELECT * FROM banks WHERE key = ?').get(bankKey);
  if (!bank) return null;
  const bankData = JSON.parse(bank.data || '{}');

  // Topic vector from facts
  const topicCounts = {};
  TOPICS.forEach(t => { topicCounts[t] = 0; });
  const facts = db.prepare(`SELECT topic FROM meeting_facts WHERE bank_key = ?`).all(bankKey);
  for (const f of facts) {
    if (topicCounts[f.topic] != null) topicCounts[f.topic] += 1;
  }
  const totalFacts = facts.length || 1;
  const topicVector = TOPICS.map(t => topicCounts[t] / totalFacts);

  // Pattern type set
  const patterns = db.prepare(`SELECT DISTINCT pattern_type FROM pattern_matches WHERE bank_key = ?`).all(bankKey);
  const patternTypes = new Set(patterns.map(p => p.pattern_type));

  // Operational scale
  const op = bankData.operational_profile || {};
  const assetsLog = op.total_assets ? Math.log10(parseFloat(String(op.total_assets).replace(/[^\d.]/g, '')) || 1) : null;

  return {
    bank_key: bankKey,
    bank_name: bank.bank_name,
    country: bank.country,
    topic_vector: topicVector,
    pattern_types: patternTypes,
    assets_log10: assetsLog,
  };
}

function cosineSim(a, b) {
  if (!a || !b || a.length !== b.length) return 0;
  let dot = 0, na = 0, nb = 0;
  for (let i = 0; i < a.length; i++) { dot += a[i]*b[i]; na += a[i]*a[i]; nb += b[i]*b[i]; }
  if (na === 0 || nb === 0) return 0;
  return dot / (Math.sqrt(na) * Math.sqrt(nb));
}

function jaccard(a, b) {
  if (!(a instanceof Set) || !(b instanceof Set)) return 0;
  const intersect = [...a].filter(x => b.has(x)).length;
  const union = new Set([...a, ...b]).size;
  return union === 0 ? 0 : intersect / union;
}

function similarity(target, candidate) {
  let score = 0;
  const reasons = [];
  if (target.country && candidate.country && target.country === candidate.country) {
    score += 3; reasons.push(`same country (${target.country})`);
  }
  const topicSim = cosineSim(target.topic_vector, candidate.topic_vector);
  score += topicSim * 4;
  if (topicSim > 0.5) reasons.push(`topic mix similarity ${(topicSim * 100).toFixed(0)}%`);

  const patternSim = jaccard(target.pattern_types, candidate.pattern_types);
  score += patternSim * 2;
  if (patternSim > 0.3) reasons.push(`pattern type overlap ${(patternSim * 100).toFixed(0)}%`);

  if (target.assets_log10 != null && candidate.assets_log10 != null) {
    const diff = Math.abs(target.assets_log10 - candidate.assets_log10);
    if (diff < 0.5) { score += 1; reasons.push('similar asset scale'); }
  }
  return { score: +score.toFixed(2), reasons };
}

/**
 * Find similar engagements (closed) to the target bank's situation.
 * Scope: banks with engagements in state='closed' and outcome set.
 */
export function findSimilarEngagements(db, targetBankKey, options = {}) {
  const { maxResults = 5, includeOpen = false } = options;
  const target = buildBankProfile(db, targetBankKey);
  if (!target) return [];

  // Closed engagements (or all if includeOpen)
  const engagements = db.prepare(`
    SELECT e.*, b.bank_name FROM engagements e
    LEFT JOIN banks b ON b.key = e.bank_key
    WHERE e.bank_key != ? ${includeOpen ? '' : "AND e.state = 'closed'"}
    ORDER BY e.updated_at DESC
  `).all(targetBankKey);

  if (engagements.length === 0) {
    return {
      target: target,
      similar_engagements: [],
      note: 'No prior engagements in the system to compare against. Similarity surfaces value as the engagement archive grows.',
    };
  }

  const matches = engagements.map(e => {
    const profile = buildBankProfile(db, e.bank_key);
    if (!profile) return null;
    const sim = similarity(target, profile);
    return {
      engagement_id: e.id,
      bank_key: e.bank_key,
      bank_name: e.bank_name,
      country: profile.country,
      engagement_type: e.engagement_type,
      state: e.state,
      outcome: e.outcome,
      title: e.title,
      similarity_score: sim.score,
      similarity_reasons: sim.reasons,
    };
  }).filter(Boolean);

  matches.sort((a, b) => b.similarity_score - a.similarity_score);
  return {
    target: { bank_key: target.bank_key, bank_name: target.bank_name, country: target.country },
    similar_engagements: matches.slice(0, maxResults),
  };
}
