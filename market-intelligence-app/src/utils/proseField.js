/**
 * proseField — schema migration helper for country reference content
 * ─────────────────────────────────────────────────────────────────
 * Country data has historically stored 6 reference fields as raw strings:
 *   banking_sector, demographics, digital_banking, consumer_segments,
 *   spending_trends, backbase_opportunities
 *
 * As part of the source-traceability upgrade, these fields are migrating
 * to a structured shape:
 *   {
 *     summary: string (the paragraph text),
 *     sources: [{ url, source, title, date }],
 *     last_refreshed: ISO string,
 *     _source_coverage: { total, sourced, pct } | null
 *   }
 *
 * normalizeProseField() reads either shape transparently — old string
 * data continues to render; new structured data exposes its sources.
 *
 * This helper is the single source of truth for "how do I read this prose
 * field?" Used by CountryProfileTab and any future UI consumer.
 */

/**
 * Normalize a prose field to { summary, sources, last_refreshed, coverage, isSourced }.
 *
 * @param {string|object|null|undefined} value — raw field value
 * @returns {{ summary: string, sources: Array, last_refreshed: string|null, coverage: object|null, isSourced: boolean }}
 */
export function normalizeProseField(value) {
  // Empty / nullish → empty record
  if (value == null) {
    return { summary: '', sources: [], last_refreshed: null, coverage: null, isSourced: false };
  }
  // Legacy string shape — wrap and mark as unsourced
  if (typeof value === 'string') {
    return {
      summary: value,
      sources: [],
      last_refreshed: null,
      coverage: null,
      isSourced: false,
      legacy: true,
    };
  }
  // New structured shape
  if (typeof value === 'object') {
    const summary = value.summary || value.text || '';
    const sources = Array.isArray(value.sources) ? value.sources : [];
    const lastRefreshed = value.last_refreshed || null;
    const coverage = value._source_coverage || null;
    return {
      summary,
      sources,
      last_refreshed: lastRefreshed,
      coverage,
      isSourced: sources.length > 0,
      legacy: false,
    };
  }
  return { summary: String(value), sources: [], last_refreshed: null, coverage: null, isSourced: false };
}

/**
 * Extract a list of unique source URLs from a normalized prose field.
 * Used to render a citations list at the foot of each subsection.
 */
export function uniqueSourceUrls(sources) {
  const seen = new Set();
  const out = [];
  for (const s of sources || []) {
    const url = s.url || s.source_url;
    if (!url || seen.has(url)) continue;
    seen.add(url);
    out.push({ url, source: s.source || s.publisher || null, title: s.title || null, date: s.date || null });
  }
  return out;
}
