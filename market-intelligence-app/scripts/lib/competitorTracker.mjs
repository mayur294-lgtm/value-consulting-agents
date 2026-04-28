/**
 * Competitor Tracker — track Backbase competitor activity across the portfolio
 * ──────────────────────────────────────────────────────────────────────────
 * Watches a fixed list of Backbase competitors (Temenos, Q2, Alkami,
 * Mambu, Thought Machine, nCino, Finastra, Salesforce FSC, Microsoft) and
 * surfaces their wins, partnerships, hires, product launches as
 * competitor_signal events. Feeds into the existing change feed alongside
 * normal bank signals.
 *
 * Why dedicated agent: existing newsSignals.mjs is bank-keyed (each
 * signal belongs to a deal). Competitor signals are TYPE-keyed (each
 * belongs to a competitor) and need their own ingestion path so they
 * don't pollute per-bank signal feeds but DO surface portfolio-wide.
 */

import { randomUUID } from 'node:crypto';
import { gradeSignal } from './sourceGrader.mjs';

const COMPETITORS = [
  { name: 'Temenos',         queries: ['Temenos banking platform', 'Temenos Infinity'] },
  { name: 'Q2',              queries: ['Q2 digital banking', 'Q2 Holdings bank'] },
  { name: 'Alkami',          queries: ['Alkami banking', 'Alkami digital'] },
  { name: 'Mambu',           queries: ['Mambu cloud banking', 'Mambu core'] },
  { name: 'Thought Machine', queries: ['Thought Machine Vault', 'Thought Machine bank'] },
  { name: 'nCino',           queries: ['nCino banking', 'nCino lending'] },
  { name: 'Finastra',        queries: ['Finastra banking', 'Finastra Fusion'] },
  { name: 'Salesforce FSC',  queries: ['Salesforce Financial Services Cloud', 'Salesforce FSC banking'] },
];

async function searchGoogleNews(query, maxResults = 4) {
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
      const pubDate = (it.match(/<pubDate>(.*?)<\/pubDate>/) || [])[1] || '';
      const source = (it.match(/<source.*?>(.*?)<\/source>/) || [])[1] || '';
      const cleanTitle = title.replace(/<!\[CDATA\[|\]\]>/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'");
      if (cleanTitle && link) {
        items.push({
          title: cleanTitle, url: link.replace(/<!\[CDATA\[|\]\]>/g, '').trim(),
          source: source.replace(/<!\[CDATA\[|\]\]>/g, ''), date: pubDate,
        });
      }
    }
    return items;
  } catch { return []; }
}

/**
 * Refresh competitor signals — fetches news for each competitor, classifies
 * signal type, persists into deal_signals with deal_id='_competitor_<name>'
 * (synthetic deal id) so they show up in portfolio change feed under a
 * dedicated bucket.
 */
export async function refreshCompetitorSignals(db, options = {}) {
  const { competitors = COMPETITORS, maxPerCompetitor = 4 } = options;
  const results = { added: 0, skipped_duplicates: 0, by_competitor: {} };

  for (const comp of competitors) {
    const compKey = `_competitor_${comp.name.replace(/[^a-z0-9]+/gi, '_')}`;
    let added = 0;

    // Ensure synthetic "deal" row for the competitor (so deal_signals FK holds)
    try {
      db.prepare(`
        INSERT OR IGNORE INTO banks (key, bank_name, country, tagline, data)
        VALUES (?, ?, '_competitor', ?, '{}')
      `).run(compKey, `(Competitor) ${comp.name}`, `Backbase competitor — auto-tracked`);
    } catch { /* swallow */ }

    for (const q of comp.queries) {
      const articles = await searchGoogleNews(q, maxPerCompetitor);
      for (const a of articles) {
        // Dedup by URL
        const exists = db.prepare(`SELECT id FROM deal_signals WHERE deal_id = ? AND source_url = ?`).get(compKey, a.url);
        if (exists) { results.skipped_duplicates += 1; continue; }

        // Classify event type from title keywords
        const blob = `${a.title} ${a.source || ''}`.toLowerCase();
        let event = 'CompetitorActivity';
        if (/\b(wins?|won|signed|announced)\b/i.test(blob)) event = 'CompetitorWin';
        else if (/\b(partner|partnership|alliance)\b/i.test(blob)) event = 'CompetitorPartnership';
        else if (/\b(launch|launches|launched|releases?)\b/i.test(blob)) event = 'CompetitorProductLaunch';
        else if (/\b(hire|hires|hired|appointed|joins)\b/i.test(blob)) event = 'CompetitorHire';
        else if (/\b(funding|raises?|valuation|ipo)\b/i.test(blob)) event = 'CompetitorFunding';

        const grade = gradeSignal({
          source_type: 'news', source_url: a.url, title: a.title, description: '',
        });

        const id = randomUUID();
        try {
          db.prepare(`
            INSERT INTO deal_signals (
              id, deal_id, signal_category, signal_event, title, description,
              source_url, source_type, severity, detected_at, source_grade,
              publisher_name, is_demo, relevance_score, is_strategic_initiative
            ) VALUES (?, ?, 'competitive', ?, ?, ?, ?, 'news', 'attention',
              datetime('now'), ?, ?, 0, 6, 0)
          `).run(
            id, compKey, event, a.title.slice(0, 240), a.title.slice(0, 480),
            a.url, grade.grade || 'C', grade.publisher || a.source || null
          );
          added += 1;
        } catch (err) {
          console.warn(`[competitorTracker] Insert failed: ${err.message}`);
        }
      }
    }
    results.added += added;
    results.by_competitor[comp.name] = added;
    console.log(`  ${comp.name.padEnd(20)} +${added} signals`);
  }

  return results;
}

export { COMPETITORS };
