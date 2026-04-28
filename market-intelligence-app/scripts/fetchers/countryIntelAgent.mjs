/**
 * Country Intelligence Agent — AI-powered refresh of country market intelligence.
 *
 * Generates structured JSON for 4 sections:
 *   - fintech_landscape: vendor categories with presence/threat mapping
 *   - regulatory_environment: regulations, licensing, open banking status
 *   - market_news: trends, M&A deals, digital transformation scoring
 *   - customer_needs: adoption metrics, unmet needs, pain points, behavioral shifts
 *
 * Uses callClaude() from the shared client with the Denmark data as a few-shot example.
 */

import { callClaude } from './claudeClient.mjs';

const STALENESS_HOURS = 24;

/**
 * Fetch recent Google News articles for a topic+country combo. Returns up to
 * `maxResults` items, each with { title, url, source, date }. The url field is
 * what the UI needs to render clickable citations.
 */
async function searchGoogleNews(query, maxResults = 5) {
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
    const itemMatches = Array.from(xml.matchAll(/<item>([\s\S]*?)<\/item>/g));
    for (const im of itemMatches) {
      if (items.length >= maxResults) break;
      const it = im[1];
      const title = (it.match(/<title>(.*?)<\/title>/) || [])[1] || '';
      const link = (it.match(/<link>(.*?)<\/link>/) || [])[1] || '';
      const pubDate = (it.match(/<pubDate>(.*?)<\/pubDate>/) || [])[1] || '';
      const source = (it.match(/<source.*?>(.*?)<\/source>/) || [])[1] || '';
      const cleanTitle = title
        .replace(/<!\[CDATA\[|\]\]>/g, '')
        .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
        .replace(/&quot;/g, '"').replace(/&#39;/g, "'");
      if (cleanTitle && link) {
        items.push({
          title: cleanTitle,
          url: link.replace(/<!\[CDATA\[|\]\]>/g, '').trim(),
          source: source.replace(/<!\[CDATA\[|\]\]>/g, ''),
          date: pubDate,
        });
      }
    }
    return items;
  } catch {
    return [];
  }
}

/**
 * Build a per-section news feed by running 1-2 targeted searches per section.
 * Returns { fintech_landscape: [...], regulatory_environment: [...], ... }
 */
async function fetchSectionNews(countryName, sections) {
  const queries = {
    fintech_landscape: [`${countryName} fintech vendors banking`, `${countryName} digital banking platform`],
    regulatory_environment: [`${countryName} banking regulation 2025`, `${countryName} central bank PSD2 open banking`],
    market_news: [`${countryName} bank acquisition merger 2025`, `${countryName} digital transformation banking`],
    customer_needs: [`${countryName} customer banking survey`, `${countryName} digital banking adoption customers`],
  };
  const out = {};
  for (const section of sections) {
    if (!queries[section]) continue;
    const articleLists = await Promise.all(queries[section].map(q => searchGoogleNews(q, 4)));
    // Flatten + de-dupe by URL
    const seen = new Set();
    const merged = [];
    for (const list of articleLists) {
      for (const a of list) {
        if (a.url && !seen.has(a.url)) {
          seen.add(a.url);
          merged.push(a);
        }
      }
    }
    out[section] = merged.slice(0, 6); // cap per section
  }
  return out;
}

export function isCountryIntelAvailable() {
  return !!process.env.ANTHROPIC_API_KEY;
}

/**
 * Check if a section is stale (> STALENESS_HOURS since last refresh)
 */
function isStale(sectionData) {
  if (!sectionData?.last_refreshed) return true;
  const age = Date.now() - new Date(sectionData.last_refreshed).getTime();
  return age > STALENESS_HOURS * 3600 * 1000;
}

const SYSTEM_PROMPT = `You are a senior financial technology market analyst specializing in banking technology landscapes across global markets. You generate structured market intelligence for Backbase, the AI-native Banking OS vendor (Control Plane that sits above systems of record and coordinates execution across customers, employees, and AI agents).

Your output must be VALID JSON matching the exact schema provided. No markdown, no commentary outside JSON.

Key principles:
- Be specific: name real vendors, real regulations, real market events
- Be accurate: use publicly available information only
- Be balanced: acknowledge market strengths AND gaps
- Focus on technology vendors relevant to banking: CBS, digital experience, payments, cards, AML/compliance, CRM, wealth management, lending, AI/ML, open banking, channels, identity/KYC, trading, data analytics
- For each vendor, assess their presence (strong/moderate/emerging/exiting) and threat level to Backbase (high/medium/low)
- Highlight Backbase's positioning: where it competes, where there's whitespace, where it complements

IMPORTANT: The "threat_level" field refers to the competitive threat TO Backbase in the digital banking / Banking OS / engagement orchestration space. CBS vendors are typically "low" threat (complementary — Backbase coexists with cores). CRM vendors like Salesforce are "medium" (overlapping customer 360, but coexist). Digital banking platforms (Temenos Infinity, Q2, Alkami) and emerging "Banking OS" challengers are the primary competition. Specialist treasury/lending platforms (Kyriba, nCino) compete in narrower lanes.

CITATION RULES (STRICTLY ENFORCED — unsourced items will be DROPPED post-parse):
- Every news article in the user message is numbered "[N]" with a URL. When a fact in your output is sourced from one of those articles, append the matching [N] marker to that field.
- For trends, recent_deals, customer pain points, and behavioral_shifts: every item MUST set "source_url" to the article's URL. Items without source_url will be discarded — DO NOT submit unsourced trend/deal/pain/shift items.
- For vendors: include "source_url" only when it's the vendor's own website or a recent funding/launch news article — NOT for pure inferences. Vendor source_url is optional.
- For regulations: items MUST set "source_url" pointing to the regulator's announcement OR be marked relevance="high" (regulators are well-known and verifiable). Anything else is dropped.
- For pain_points and behavioral_shifts: include either "source_url" OR a substantial "evidence" / "implication" string explaining the inference. Items with neither will be dropped.
- Top-level "sources" array on each section: include EVERY numbered article from the user message that you actually used, with { id, url, source, title, date }.
- DO NOT fabricate URLs. If you don't have a verifiable source for an item, simply OMIT that item rather than producing a hollow citation. Fewer well-sourced items beat more invented ones.`;

/**
 * Build a per-section user prompt
 */
function buildUserPrompt(countryName, existingData, sections, sectionNews = {}) {
  const sectionDescriptions = {
    fintech_landscape: `Generate the "fintech_landscape" section with:
- summary: 2-3 sentence overview of the fintech ecosystem
- maturity_level: "emerging" | "growing" | "mature" | "advanced"
- categories: array of 10-14 categories, each with:
  - id: slug (cbs, engagement_banking, payments, cards, aml_compliance, crm, wealth_management, lending_platforms, ai_ml, open_banking, channels, identity_verification, trading, data_analytics)
  - name: human-readable category name
  - vendors: array of 3-5 vendors per category, each with: name, type (global/regional/local/neobank), presence (strong/moderate/emerging/exiting), notable_clients (array), threat_level (high/medium/low), notes (1 sentence), source_url (optional — vendor website or recent news URL when available)
- sources: array of every news article you cited, each with { id, url, source, title, date }
- last_refreshed: current ISO timestamp`,

    regulatory_environment: `Generate the "regulatory_environment" section with:
- summary: 2-3 sentence overview
- central_bank: name and key facts
- central_bank_url: official central bank website URL (e.g., "https://www.nationalbanken.dk")
- key_regulations: array of 5-8 major regulations, each with: name, status (implemented/in_progress/planned), effective_date, impact (1 sentence), relevance (high/medium/low), source_url (regulator's announcement page when available)
- licensing: { digital_banking_license: bool, neobank_framework: bool, sandbox_available: bool, notes: string }
- open_banking: { status (advanced/implemented/in_progress/early/none), standard, api_adoption_rate, notes }
- aml_kyc: { digital_onboarding_allowed: bool, ekyc_framework: bool, notes }
- sources: array of every news article you cited, each with { id, url, source, title, date }
- last_refreshed: current ISO timestamp`,

    market_news: `Generate the "market_news" section with:
- trends: array of 4-6 recent market trends, each with: title, category (digital_transformation/m_and_a/regulation/fintech/consumer/sustainability), summary (2-3 sentences), impact (high/medium/low), date (YYYY-QN format), source_url (when from a numbered article), source (publisher name)
- recent_deals: array of 3-5 recent M&A/partnership/funding events, each with: type (acquisition/partnership/funding/divestment), parties (array), value, date, significance, source_url (when from a numbered article), source
- digital_transformation_score: 0-10 integer
- sources: array of every news article you cited, each with { id, url, source, title, date }
- last_refreshed: current ISO timestamp`,

    customer_needs: `Generate the "customer_needs" section with:
- summary: 2-3 sentence overview
- digital_adoption: { mobile_banking_penetration, online_banking_penetration, contactless_payments, open_banking_usage } — all as percentage strings
- unmet_needs: array of 4-6 items, each with: segment (retail/sme/corporate/wealth), need, gap_severity (high/medium/low), opportunity, evidence, source_url (optional — survey or report URL)
- customer_pain_points: array of 4-5 items, each with: pain, affected_segments (array), prevalence (widespread/common/niche), source_url (optional)
- behavioral_shifts: array of 3-4 items, each with: shift, trend_direction (accelerating/steady/slowing), implication, source_url (optional)
- sources: array of every news article you cited, each with { id, url, source, title, date }
- last_refreshed: current ISO timestamp`,
  };

  // Build the per-section numbered news context Claude can cite as [N]
  let newsBlock = '';
  let counter = 0;
  for (const section of sections) {
    const articles = sectionNews[section] || [];
    if (articles.length === 0) continue;
    const numbered = articles.map((a) => {
      counter += 1;
      return `  [${counter}] "${a.title}" — ${a.source || 'unknown'} (${a.date || 'undated'})\n      URL: ${a.url}`;
    }).join('\n');
    newsBlock += `\n\n### Recent news for "${section}" (cite as [N] AND copy the URL into source_url on the relevant item):\n${numbered}`;
  }

  const requestedSections = sections
    .map(s => sectionDescriptions[s])
    .filter(Boolean)
    .join('\n\n');

  // Include existing context for enrichment
  const existingContext = existingData ? `
Existing country context:
- Tagline: ${existingData.tagline || 'N/A'}
- Banking sector: ${(existingData.banking_sector || '').substring(0, 500)}
- Top banks: ${(existingData.top_banks || []).map(b => b.name).join(', ')}
` : '';

  return `Generate market intelligence for: ${countryName}

${existingContext}
${newsBlock}

Generate ONLY the following sections as a single JSON object with section names as keys:

${requestedSections}

CRITICAL: Whenever your output cites a fact from a numbered news article above, you MUST:
  1. Append the matching [N] marker to the relevant text field (e.g., trend.summary, deal.significance)
  2. Set source_url on that item to the article's URL
  3. Set source to the article's publisher name
  4. Include the article in the section-level "sources" array

Output ONLY valid JSON. No markdown fences, no explanation text.`;
}

/**
 * Refresh country intelligence via Claude AI.
 *
 * @param {string} countryName - e.g., "Denmark"
 * @param {object} existingData - current country data blob
 * @param {string[]} sections - sections to refresh
 * @param {boolean} force - ignore staleness check
 * @returns {Promise<object>} - refreshed section data
 */
export async function refreshCountryIntelligence(countryName, existingData, sections, force = false) {
  // Filter to sections that are stale (or forced)
  const sectionsToRefresh = force
    ? sections
    : sections.filter(s => isStale(existingData?.[s]));

  if (sectionsToRefresh.length === 0) {
    return { refreshed: {}, skipped: sections };
  }

  // Step 1 — fetch real news per section so the agent can cite actual URLs.
  // Best-effort: if a fetch fails, the agent falls back to model knowledge
  // and the UI shows search-fallback links instead.
  let sectionNews = {};
  try {
    sectionNews = await fetchSectionNews(countryName, sectionsToRefresh);
    const totalArticles = Object.values(sectionNews).reduce((s, a) => s + a.length, 0);
    console.log(`   [countryIntel] Fetched ${totalArticles} news articles across ${sectionsToRefresh.length} sections for ${countryName}`);
  } catch (err) {
    console.warn(`   [countryIntel] News fetch failed for ${countryName}: ${err.message}`);
  }

  const userPrompt = buildUserPrompt(countryName, existingData, sectionsToRefresh, sectionNews);

  const response = await callClaude(SYSTEM_PROMPT, userPrompt, {
    maxTokens: 8192,
    timeout: 120000,
  });

  // Parse and validate JSON
  let parsed;
  try {
    // Strip markdown fences if present
    const cleaned = response.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
    parsed = JSON.parse(cleaned);
  } catch (e) {
    throw new Error(`Failed to parse AI response as JSON: ${e.message}`);
  }

  // Validate required fields per section + ENFORCE source provenance on
  // fact-claim items. Anti-hallucination guardrail (mirrors Sprint 2.2):
  // when news articles were provided in the prompt, every fact-claim item
  // (trend, deal, regulation, pain point, behavioral shift) MUST carry a
  // source_url. Unsourced items get dropped, not invented around.
  const refreshed = {};
  const droppedPerSection = {};

  for (const section of sectionsToRefresh) {
    if (!parsed[section]) continue;
    const sec = parsed[section];

    // News was actually provided for this section?
    const hadNews = (sectionNews[section] || []).length > 0;
    let dropped = 0;

    // Per-section guard: items that should carry source_url when news exists.
    if (hadNews) {
      if (Array.isArray(sec.trends)) {
        const before = sec.trends.length;
        sec.trends = sec.trends.filter(t => t.source_url || /\[\d+\]/.test(`${t.summary || ''} ${t.title || ''}`));
        dropped += before - sec.trends.length;
      }
      if (Array.isArray(sec.recent_deals)) {
        const before = sec.recent_deals.length;
        sec.recent_deals = sec.recent_deals.filter(d => d.source_url || /\[\d+\]/.test(`${d.significance || ''}`));
        dropped += before - sec.recent_deals.length;
      }
      if (Array.isArray(sec.key_regulations)) {
        // Regulations: keep if has source_url OR if it's a high-relevance regulation
        // (regulators are well-known; we trust the agent more here than for news)
        const before = sec.key_regulations.length;
        sec.key_regulations = sec.key_regulations.filter(r => r.source_url || r.relevance === 'high');
        dropped += before - sec.key_regulations.length;
      }
      if (Array.isArray(sec.customer_pain_points)) {
        const before = sec.customer_pain_points.length;
        sec.customer_pain_points = sec.customer_pain_points.filter(p => p.source_url || p.evidence);
        dropped += before - sec.customer_pain_points.length;
      }
      if (Array.isArray(sec.behavioral_shifts)) {
        const before = sec.behavioral_shifts.length;
        sec.behavioral_shifts = sec.behavioral_shifts.filter(b => b.source_url || b.implication);
        dropped += before - sec.behavioral_shifts.length;
      }
    }

    // Compute source coverage stat — surfaced in UI for transparency
    sec._source_coverage = computeSourceCoverage(sec);
    sec.last_refreshed = new Date().toISOString();
    refreshed[section] = sec;
    if (dropped > 0) droppedPerSection[section] = dropped;
  }

  if (Object.keys(droppedPerSection).length > 0) {
    console.log(`   [countryIntel] Dropped unsourced items:`, droppedPerSection);
  }

  return {
    refreshed,
    skipped: sections.filter(s => !refreshed[s]),
    dropped: droppedPerSection,
  };
}

/**
 * Compute the % of fact-claim items in a section that carry a source_url.
 * Surfaced in UI as a "source coverage" chip per cluster.
 */
function computeSourceCoverage(sec) {
  const claimArrays = ['trends', 'recent_deals', 'key_regulations', 'unmet_needs', 'customer_pain_points', 'behavioral_shifts'];
  let total = 0, sourced = 0;
  for (const k of claimArrays) {
    if (Array.isArray(sec[k])) {
      total += sec[k].length;
      sourced += sec[k].filter(item => item.source_url).length;
    }
  }
  if (total === 0) return null;
  return { total, sourced, pct: Math.round(sourced / total * 100) };
}
