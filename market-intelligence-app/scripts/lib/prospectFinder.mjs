/**
 * Prospect Finder — surfaces new banks Nova doesn't yet track
 * ───────────────────────────────────────────────────────────
 * Uses Google News to find banking entities mentioned in a region/country
 * that are NOT already in Nova's banks table. For each candidate, gathers
 * minimal evidence (recent news, country) and surfaces as a "new prospect"
 * for AE review.
 *
 * Conservative design — does NOT auto-create banks. AE/admin reviews the
 * candidate list and decides which to onboard via existing bank-create
 * flow. Anti-spam: filters out generic mentions (large multinationals,
 * non-banks, news-publisher names).
 */

const NEWS_QUERIES = {
  Sweden: ['Swedish bank fintech', 'Sweden challenger bank', 'Sweden neobank'],
  Denmark: ['Danish bank fintech', 'Denmark challenger bank'],
  Norway: ['Norwegian bank fintech', 'Norway challenger bank'],
  Finland: ['Finnish bank fintech', 'Finland challenger bank'],
};

// Banks the world already knows about — never surface as "new"
const WELL_KNOWN_NON_PROSPECTS = new Set([
  'JPMorgan', 'Citi', 'Bank of America', 'HSBC', 'BNP Paribas', 'Deutsche Bank',
  'Goldman Sachs', 'Morgan Stanley', 'UBS', 'Credit Suisse',
]);

async function searchGoogleNews(query, maxResults = 8) {
  const encoded = encodeURIComponent(query);
  const feed = `https://news.google.com/rss/search?q=${encoded}&hl=en&gl=US&ceid=US:en`;
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 8000);
    const res = await fetch(feed, { signal: controller.signal });
    clearTimeout(timer);
    if (!res.ok) return [];
    const xml = await res.text();
    const items = [];
    const matches = Array.from(xml.matchAll(/<item>([\s\S]*?)<\/item>/g));
    for (const m of matches) {
      if (items.length >= maxResults) break;
      const it = m[1];
      const title = (it.match(/<title>(.*?)<\/title>/) || [])[1] || '';
      const link = (it.match(/<link>(.*?)<\/link>/) || [])[1] || '';
      const cleanTitle = title.replace(/<!\[CDATA\[|\]\]>/g, '').replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#39;/g, "'");
      if (cleanTitle && link) items.push({ title: cleanTitle, url: link.trim() });
    }
    return items;
  } catch { return []; }
}

/**
 * Extract candidate bank names from headlines using regex heuristics.
 * Looks for patterns like "<Name> Bank", "<Name> Financial", "<Name> Banking"
 * and filters against existing banks + non-prospect blacklist.
 */
function extractCandidateNames(articles, existingBankNames) {
  const candidates = new Map(); // name → { mentions, articles }
  // Capture leading capitalized phrase before "Bank" / "Financial" / "Banking"
  const namePattern = /\b([A-Z][\w&]+(?:\s+[A-Z][\w&]+){0,3})\s+(?:Bank|Banking|Financial Services|Sparbank|Sparkasse|Bank Group)\b/g;

  for (const article of articles) {
    const matches = Array.from(article.title.matchAll(namePattern));
    for (const m of matches) {
      const candidate = m[0].trim();
      // Skip if already known
      if (existingBankNames.some(name => candidate.toLowerCase().includes(name.toLowerCase()) ||
                                         name.toLowerCase().includes(candidate.toLowerCase()))) continue;
      // Skip blacklisted multinationals
      if (Array.from(WELL_KNOWN_NON_PROSPECTS).some(b => candidate.includes(b))) continue;
      // Skip too-short candidates
      if (candidate.length < 6) continue;
      if (!candidates.has(candidate)) candidates.set(candidate, { mentions: 0, articles: [] });
      const c = candidates.get(candidate);
      c.mentions += 1;
      c.articles.push(article);
    }
  }
  return Array.from(candidates.entries())
    .filter(([, v]) => v.mentions >= 1) // at least 1 mention
    .map(([name, v]) => ({ candidate_name: name, mentions: v.mentions, sample_articles: v.articles.slice(0, 3) }))
    .sort((a, b) => b.mentions - a.mentions);
}

/**
 * Find new bank prospects in a country that Nova doesn't currently track.
 *
 * @param {Database} db
 * @param {string} country — country name (e.g., "Sweden")
 * @returns Array of candidates with name + sample articles
 */
export async function findProspectsInCountry(db, country) {
  const queries = NEWS_QUERIES[country] || [`${country} bank fintech`];

  const articleLists = await Promise.all(queries.map(q => searchGoogleNews(q, 8)));
  const articles = [];
  const seen = new Set();
  for (const list of articleLists) {
    for (const a of list) {
      if (!seen.has(a.url)) { seen.add(a.url); articles.push(a); }
    }
  }

  const existing = db.prepare(`SELECT bank_name FROM banks WHERE country LIKE ?`).all(`${country}%`).map(r => r.bank_name);

  return {
    country,
    articles_searched: articles.length,
    existing_banks: existing.length,
    candidates: extractCandidateNames(articles, existing),
  };
}
