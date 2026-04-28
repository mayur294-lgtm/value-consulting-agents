/**
 * Regulatory Impact Agent — map new regulations to portfolio impact
 * ─────────────────────────────────────────────────────────────────
 * When a regulatory signal lands, identifies which banks in the portfolio
 * are most likely affected based on:
 *   - Country match (banks in jurisdiction)
 *   - Topic match (banks with related capability gaps or pain points)
 *   - Existing regulatory exposure (banks with prior regulatory signals)
 *
 * Output: ranked list of impacted banks with rationale.
 *
 * Pure structural composition — same input → same output. The LLM is
 * NOT used for impact mapping (we have the capability data; we just
 * compute overlap).
 */

const REGULATORY_KEYWORDS = {
  AML: ['aml', 'anti-money', 'money laundering'],
  KYC: ['kyc', 'know your customer', 'customer due diligence', 'cdd'],
  PSD2: ['psd2', 'open banking'],
  DORA: ['dora', 'operational resilience'],
  GDPR: ['gdpr', 'data protection'],
  SANCTIONS: ['sanctions', 'embargo'],
  CRYPTO: ['crypto', 'mica', 'digital asset'],
  CLIMATE: ['climate', 'esg', 'sustainability'],
};

function classifyRegulation(title, description) {
  const blob = `${title} ${description || ''}`.toLowerCase();
  const tags = [];
  for (const [tag, keywords] of Object.entries(REGULATORY_KEYWORDS)) {
    if (keywords.some(k => blob.includes(k))) tags.push(tag);
  }
  return tags.length > 0 ? tags : ['GENERAL'];
}

/**
 * Given a regulatory signal, compute portfolio impact.
 * @param {object} regulationSignal — { title, description, country, jurisdiction }
 */
export function mapRegulationToImpact(db, regulationSignal, options = {}) {
  const { maxBanks = 12 } = options;
  const tags = classifyRegulation(regulationSignal.title, regulationSignal.description);
  const country = regulationSignal.country || regulationSignal.jurisdiction || null;

  // Candidate banks: same country OR same region OR have prior signals on same tags
  const banks = db.prepare(`
    SELECT key, bank_name, country FROM banks WHERE country != '_competitor' OR country IS NULL
  `).all();

  const impacts = [];
  for (const bank of banks) {
    let impactScore = 0;
    const reasons = [];

    // Country/jurisdiction match
    if (country && bank.country) {
      if (bank.country.toLowerCase().includes(country.toLowerCase()) ||
          country.toLowerCase().includes(bank.country.toLowerCase().split(' ')[0])) {
        impactScore += 5;
        reasons.push(`country match: ${bank.country}`);
      }
    }

    // Prior regulatory signal density (same tags)
    const priorRegSignals = db.prepare(`
      SELECT title, description FROM deal_signals
      WHERE deal_id = ? AND signal_category = 'regulatory'
        AND COALESCE(is_demo, 0) = 0 AND detected_at >= datetime('now', '-180 days')
    `).all(bank.key);
    let tagOverlap = 0;
    for (const s of priorRegSignals) {
      const sTags = classifyRegulation(s.title, s.description);
      if (sTags.some(t => tags.includes(t))) tagOverlap += 1;
    }
    if (tagOverlap > 0) {
      impactScore += Math.min(4, tagOverlap);
      reasons.push(`${tagOverlap} prior regulatory signal${tagOverlap === 1 ? '' : 's'} on same topic`);
    }

    // Customer pain point or unmet need on same tag (if customer_needs is sourced)
    try {
      const country = db.prepare(`SELECT data FROM countries WHERE name = ?`).get(bank.country);
      if (country) {
        const cd = JSON.parse(country.data || '{}');
        const cn = cd.customer_needs || {};
        const painBlob = JSON.stringify(cn.customer_pain_points || []) + JSON.stringify(cn.unmet_needs || []);
        for (const tag of tags) {
          if (REGULATORY_KEYWORDS[tag]?.some(k => painBlob.toLowerCase().includes(k))) {
            impactScore += 2;
            reasons.push(`country has pain point on ${tag}`);
            break;
          }
        }
      }
    } catch { /* swallow */ }

    if (impactScore > 0) {
      impacts.push({
        bank_key: bank.key,
        bank_name: bank.bank_name,
        country: bank.country,
        impact_score: impactScore,
        reasons,
        regulation_tags: tags,
      });
    }
  }

  return {
    regulation: { title: regulationSignal.title, tags, country },
    impacted_banks: impacts.sort((a, b) => b.impact_score - a.impact_score).slice(0, maxBanks),
  };
}
