/**
 * Data CRUD route handlers — banks, markets, countries, search, stats.
 */

import crypto from 'node:crypto';
import { jsonResponse, parseBody } from './helpers.mjs';
import { getSignalRouting } from '../../src/data/intelligenceLayer.js';
import { getChangesForBank } from '../lib/changeWriter.mjs';
import { harvestSignalsForBank } from '../harvestNordicSignals.mjs';
import { reclassifyStaleForBank } from '../reclassifySignals.mjs';
import { routeLiveSignals } from '../lib/signalRouter.mjs';
import { buildStakeholderMatcher, enrichStakeholders } from '../lib/stakeholderMatcher.mjs';
import { fetchOpenGraph } from '../lib/ogFetcher.mjs';
import { runningRefreshes } from '../lib/signalScheduler.mjs';
import { generatePulseForBank } from '../lib/pulseGenerator.mjs';
import { getStakeholderDrift, getDriftByStakeholder, getBankDriftRollup } from '../lib/stakeholderDrift.mjs';
import { getPatternsForBank, runCrossReferenceForBank } from '../lib/crossReferenceEngine.mjs';
import { getChangeFeed, getChangeFeedCounts } from '../lib/changeFeed.mjs';
import { runPortfolioQuery, EXAMPLE_QUERIES } from '../lib/portfolioQuery.mjs';
import { translateQuery as translateNLQuery } from '../lib/portfolioQueryNL.mjs';
import {
  getBanksForRegion, getBanksForCountry,
  getRegionPatterns, getRegionGradeDistribution, getRegionDriftHeatmap,
  getComputedOpportunities, getRegionEngagementSummary,
} from '../lib/regionAggregator.mjs';
import { generateRegionPulse } from '../lib/regionPulse.mjs';
import {
  listEngagements, getEngagement, createEngagement, transitionEngagement,
  registerArtifact, listArtifacts, getBankEngagementSummary,
} from '../lib/engagementTracker.mjs';
import { buildHandoffSnapshot, snapshotToMarkdown } from '../lib/engagementBridge.mjs';
import { ingestDeliverable } from '../lib/deliverableIngest.mjs';
import { ingestTranscript } from '../lib/transcriptIngestor.mjs';
import { ingestEmailThread } from '../lib/emailThreadParser.mjs';

// ── Qualification Score Calculator (mirrors client-side calcScoreFromData) ──
const QUAL_WEIGHTS = {
  firmographics: 0.10, technographics: 0.15, decision_process: 0.10,
  landing_zones: 0.20, pain_push: 0.20, power_map: 0.15, partner_access: 0.10,
};

function calcBankScore(qualData) {
  if (!qualData) return 0;
  let w = 0;
  for (const [dim, weight] of Object.entries(QUAL_WEIGHTS)) {
    const d = qualData[dim];
    if (d && typeof d.score === 'number') w += d.score * weight;
  }
  if (qualData.power_map?.activated) w += 1.0;
  if (qualData.partner_access?.backbase_access) w += 0.5;
  return Math.round(Math.min(w, 10) * 10) / 10;
}

/**
 * Try to handle a data route. Returns true if handled, false if not matched.
 */
export async function handleDataRoute(req, res, { path, url, db, parseRow, parseRows }) {
  let match;

  // ── GET /api/banks ── List all banks (summary)
  if (path === '/api/banks' && req.method === 'GET') {
    const rows = db.prepare(`
      SELECT b.key, b.bank_name, b.country, b.tagline,
             q.data as qual_data,
             c.core_banking, c.digital_platform
      FROM banks b
      LEFT JOIN qualification q ON q.bank_key = b.key
      LEFT JOIN competition c ON c.bank_key = b.key
      ORDER BY b.bank_name
    `).all();
    const banks = rows.map(row => {
      const qd = row.qual_data ? JSON.parse(row.qual_data) : null;
      return {
        key: row.key, bank_name: row.bank_name, country: row.country,
        tagline: row.tagline, core_banking: row.core_banking,
        digital_platform: row.digital_platform, qualification: qd,
      };
    });
    jsonResponse(res, 200, banks);
    return true;
  }

  // ── GET /api/stats ──
  if (path === '/api/stats' && req.method === 'GET') {
    const totalBanks = db.prepare('SELECT COUNT(*) as c FROM banks').get().c;
    const totalCountries = db.prepare('SELECT COUNT(*) as c FROM countries').get().c;
    const totalMarkets = db.prepare('SELECT COUNT(*) as c FROM markets WHERE has_data = 1').get().c;
    jsonResponse(res, 200, { totalBanks, totalCountries, totalMarkets });
    return true;
  }

  // ── GET /api/signals ── Blended live + static signals for homepage
  if (path === '/api/signals' && req.method === 'GET') {
    const limit = parseInt(url.searchParams.get('limit') || '8', 10);
    const minScore = parseFloat(url.searchParams.get('min_score') || '5');
    const sourceFilter = url.searchParams.get('source'); // 'live', 'static', or null (both)
    const bankFilter = url.searchParams.get('bank_key'); // filter to one bank
    const typeFilter = url.searchParams.get('type'); // 'strategic,hiring' etc.

    const signals = [];
    const priorityOrder = { high: 3, medium: 2, low: 1 };

    // ── 1. Live signals from live_signals table (AI-classified) ──
    if (sourceFilter !== 'static') {
      try {
        let liveQuery = `
          SELECT ls.*, b.bank_name, b.country, q.data as qual_data
          FROM live_signals ls
          JOIN banks b ON b.key = ls.bank_key
          LEFT JOIN qualification q ON q.bank_key = ls.bank_key
          WHERE ls.relevance_score >= ?
            AND ls.classified_at IS NOT NULL
        `;
        const params = [minScore];

        if (bankFilter) {
          liveQuery += ' AND ls.bank_key = ?';
          params.push(bankFilter);
        }
        if (typeFilter) {
          const types = typeFilter.split(',').map(t => t.trim());
          liveQuery += ` AND ls.signal_type IN (${types.map(() => '?').join(',')})`;
          params.push(...types);
        }

        liveQuery += ' ORDER BY ls.relevance_score DESC, ls.published_at DESC LIMIT 50';

        const liveRows = db.prepare(liveQuery).all(...params);
        for (const row of liveRows) {
          const qd = row.qual_data ? JSON.parse(row.qual_data) : null;
          const bankScore = calcBankScore(qd);
          signals.push({
            type: row.signal_type || 'signal',
            bank: row.bank_name,
            bankKey: row.bank_key,
            country: row.country,
            score: bankScore,
            text: row.title,
            detail: row.implication || row.snippet || '',
            source: `${row.source} (Live)`,
            sourceUrl: row.source_url,
            priority: row.priority || (row.relevance_score >= 8 ? 'high' : row.relevance_score >= 6 ? 'medium' : 'low'),
            relevanceScore: row.relevance_score,
            publishedAt: row.published_at,
            isLive: true,
          });
        }

        // ── Adaptive threshold: fill in underrepresented banks ──
        // If a bank has zero signals at the normal threshold, surface their
        // best signal at a lower threshold (score >= 3) so every tracked bank
        // gets at least some coverage. This prevents large-cap bias.
        if (!bankFilter) {
          const banksWithSignals = new Set(liveRows.map(r => r.bank_key));
          const allBankKeys = db.prepare('SELECT key FROM banks').all().map(r => r.key);
          const underrepresented = allBankKeys.filter(k => !banksWithSignals.has(k));

          if (underrepresented.length > 0) {
            const placeholders = underrepresented.map(() => '?').join(',');
            const fallbackRows = db.prepare(`
              SELECT ls.*, b.bank_name, b.country, q.data as qual_data
              FROM live_signals ls
              JOIN banks b ON b.key = ls.bank_key
              LEFT JOIN qualification q ON q.bank_key = ls.bank_key
              WHERE ls.bank_key IN (${placeholders})
                AND ls.relevance_score >= 3
                AND ls.classified_at IS NOT NULL
              ORDER BY ls.relevance_score DESC, ls.published_at DESC
            `).all(...underrepresented);

            // Take the single best signal per underrepresented bank
            const seenBanks = new Set();
            for (const row of fallbackRows) {
              if (seenBanks.has(row.bank_key)) continue;
              seenBanks.add(row.bank_key);

              const qd = row.qual_data ? JSON.parse(row.qual_data) : null;
              const bankScore = calcBankScore(qd);
              signals.push({
                type: row.signal_type || 'signal',
                bank: row.bank_name,
                bankKey: row.bank_key,
                country: row.country,
                score: bankScore,
                text: row.title,
                detail: row.implication || row.snippet || '',
                source: `${row.source} (Live)`,
                sourceUrl: row.source_url,
                priority: 'low',
                relevanceScore: row.relevance_score,
                publishedAt: row.published_at,
                isLive: true,
                isFallback: true, // Flag so UI can optionally style differently
              });
            }
          }
        }
      } catch {
        // live_signals table may not exist yet — graceful fallback
      }
    }

    // ── 2. Static signals from bank profile data ──
    if (sourceFilter !== 'live') {
      const bankQuery = bankFilter
        ? db.prepare(`SELECT b.key, b.bank_name, b.country, b.data as bank_data, q.data as qual_data
            FROM banks b LEFT JOIN qualification q ON q.bank_key = b.key
            WHERE b.key = ? AND b.data IS NOT NULL AND b.data != '{}'`).all(bankFilter)
        : db.prepare(`SELECT b.key, b.bank_name, b.country, b.data as bank_data, q.data as qual_data
            FROM banks b LEFT JOIN qualification q ON q.bank_key = b.key
            WHERE b.data IS NOT NULL AND b.data != '{}'
            ORDER BY b.updated_at DESC`).all();

      for (const row of bankQuery) {
        const bd = row.bank_data ? JSON.parse(row.bank_data) : {};
        const qd = row.qual_data ? JSON.parse(row.qual_data) : null;
        const score = calcBankScore(qd);

        // Strategic signals
        if (bd.signals && Array.isArray(bd.signals)) {
          for (const sig of bd.signals.slice(0, 2)) {
            signals.push({
              type: 'signal',
              bank: row.bank_name,
              bankKey: row.key,
              country: row.country,
              score,
              text: sig.signal || sig.text || '',
              detail: sig.implication || '',
              source: 'Strategic Signal',
              priority: score >= 8 ? 'high' : score >= 6 ? 'medium' : 'low',
              isLive: false,
            });
          }
        }

        // Pain points
        if (bd.pain_points && Array.isArray(bd.pain_points)) {
          for (const pp of bd.pain_points.slice(0, 1)) {
            signals.push({
              type: 'pain_point',
              bank: row.bank_name,
              bankKey: row.key,
              country: row.country,
              score,
              text: pp.title || '',
              detail: pp.detail || '',
              source: 'Pain Point',
              priority: score >= 8 ? 'high' : 'medium',
              isLive: false,
            });
          }
        }

        // Stock movements
        if (bd.live_stock?.price && bd.live_stock?.dayChangePercent) {
          const pct = bd.live_stock.dayChangePercent;
          if (Math.abs(pct) > 3) {
            signals.push({
              type: 'stock',
              bank: row.bank_name,
              bankKey: row.key,
              country: row.country,
              score,
              text: `Stock ${pct > 0 ? '↑' : '↓'} ${Math.abs(pct).toFixed(1)}% — ${bd.live_stock.ticker} at ${bd.live_stock.currency} ${bd.live_stock.price}`,
              detail: '',
              source: 'Stock Movement',
              priority: Math.abs(pct) > 5 ? 'high' : 'medium',
              isLive: false,
            });
          }
        }
      }
    }

    // Deduplicate: live signals take precedence over static with similar text
    const seen = new Set();
    const deduped = signals.filter(s => {
      const key = `${s.bankKey}|${s.text.substring(0, 50).toLowerCase()}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });

    // Sort: live first, then by score, then by priority
    deduped.sort((a, b) =>
      (b.isLive ? 1 : 0) - (a.isLive ? 1 : 0)
      || (b.score - a.score)
      || (priorityOrder[b.priority] || 0) - (priorityOrder[a.priority] || 0)
    );

    jsonResponse(res, 200, deduped.slice(0, limit));
    return true;
  }

  // ── POST /api/signals/refresh ── Trigger on-demand signal refresh
  if (path === '/api/signals/refresh' && req.method === 'POST') {
    // Check cooldown (10 min between refreshes)
    const lastRun = db.prepare(
      `SELECT completed_at FROM signal_refresh_log WHERE status = 'complete' ORDER BY id DESC LIMIT 1`
    ).get();

    if (lastRun?.completed_at) {
      const elapsed = Date.now() - new Date(lastRun.completed_at + 'Z').getTime();
      if (elapsed < 10 * 60 * 1000) {
        jsonResponse(res, 429, {
          error: 'Signal refresh on cooldown',
          retryAfterMs: 10 * 60 * 1000 - elapsed,
          lastRefresh: lastRun.completed_at,
        });
        return true;
      }
    }

    // Run refresh in background (non-blocking)
    const { runSignalRefresh } = await import('../fetchers/signalIngestion.mjs');
    runSignalRefresh(db, { skipNews: false }).catch(err =>
      console.error('[signals/refresh] Error:', err.message)
    );

    jsonResponse(res, 202, { status: 'started', message: 'Signal refresh started in background' });
    return true;
  }

  // ── GET /api/signals/status ── Refresh status
  if (path === '/api/signals/status' && req.method === 'GET') {
    const lastRun = db.prepare(
      `SELECT * FROM signal_refresh_log ORDER BY id DESC LIMIT 1`
    ).get();

    let totalLiveSignals = 0;
    let topSources = [];
    try {
      totalLiveSignals = db.prepare('SELECT COUNT(*) as cnt FROM live_signals WHERE relevance_score >= 5').get()?.cnt || 0;
      topSources = db.prepare(`
        SELECT source, COUNT(*) as cnt FROM live_signals
        WHERE relevance_score >= 5 GROUP BY source ORDER BY cnt DESC LIMIT 5
      `).all();
    } catch {
      // Table may not exist yet
    }

    jsonResponse(res, 200, {
      lastRefresh: lastRun || null,
      totalLiveSignals,
      topSources,
    });
    return true;
  }

  // ── GET /api/search?q= ──
  if (path === '/api/search' && req.method === 'GET') {
    const q = url.searchParams.get('q');
    if (!q || q.length < 2) { jsonResponse(res, 200, { results: [], counts: {} }); return true; }
    const term = `%${q.toLowerCase()}%`;
    const results = [];
    const counts = {};

    // Search banks
    const bankRows = db.prepare(`
      SELECT b.key, b.bank_name, b.country, b.tagline, b.data as bank_data, q.data as qual_data
      FROM banks b LEFT JOIN qualification q ON q.bank_key = b.key
      WHERE LOWER(b.bank_name) LIKE ? OR LOWER(b.country) LIKE ? OR LOWER(b.tagline) LIKE ? OR LOWER(b.data) LIKE ?
      LIMIT 20
    `).all(term, term, term, term);
    for (const r of bankRows) {
      const bd = r.bank_data ? JSON.parse(r.bank_data) : {};
      const qd = r.qual_data ? JSON.parse(r.qual_data) : null;
      const dealSize = bd.backbase_qualification?.deal_size;
      results.push({
        type: 'bank', name: r.bank_name,
        meta: r.country + (dealSize ? ' \u2022 ' + dealSize : ''),
        key: r.key, score: calcBankScore(qd),
      });

      const kdms = bd.key_decision_makers || [];
      for (const dm of kdms) {
        if (dm.name && !dm.name.startsWith('(')) {
          const hay = (dm.name + ' ' + dm.role + ' ' + (dm.note || '')).toLowerCase();
          if (q.toLowerCase().split(/\s+/).every(w => hay.includes(w) || r.bank_name.toLowerCase().includes(w))) {
            results.push({
              type: 'person', name: dm.name,
              meta: r.bank_name + ' \u2014 ' + dm.role,
              bankKey: r.key,
            });
          }
        }
      }
    }

    // Search KDMs in non-matched banks
    const personRows = db.prepare(`
      SELECT key, bank_name, data FROM banks
      WHERE LOWER(data) LIKE ? AND key NOT IN (${bankRows.map(() => '?').join(',') || "''"})
      LIMIT 20
    `).all(term, ...bankRows.map(r => r.key));
    for (const r of personRows) {
      const bd = JSON.parse(r.data);
      const kdms = bd.key_decision_makers || [];
      for (const dm of kdms) {
        if (dm.name && !dm.name.startsWith('(')) {
          const hay = (dm.name + ' ' + dm.role + ' ' + (dm.note || '')).toLowerCase();
          if (q.toLowerCase().split(/\s+/).every(w => hay.includes(w))) {
            results.push({
              type: 'person', name: dm.name,
              meta: r.bank_name + ' \u2014 ' + dm.role,
              bankKey: r.key,
            });
          }
        }
      }
    }

    // Search countries
    const countryRows = db.prepare(`
      SELECT name, data FROM countries WHERE LOWER(name) LIKE ? OR LOWER(data) LIKE ? LIMIT 10
    `).all(term, term);
    for (const r of countryRows) {
      const d = JSON.parse(r.data);
      results.push({ type: 'country', name: r.name, meta: d.tagline || '' });
    }

    // Search markets
    const marketRows = db.prepare(`
      SELECT key, name FROM markets WHERE LOWER(name) LIKE ? LIMIT 5
    `).all(term);
    for (const r of marketRows) {
      results.push({ type: 'market', name: r.name, key: r.key });
    }

    results.forEach(r => { counts[r.type] = (counts[r.type] || 0) + 1; });
    jsonResponse(res, 200, { results, counts });
    return true;
  }

  // ── GET /api/markets ──
  if (path === '/api/markets' && req.method === 'GET') {
    const rows = db.prepare('SELECT * FROM markets ORDER BY name').all();
    jsonResponse(res, 200, parseRows('markets', rows));
    return true;
  }

  // ── GET /api/markets/:key ──
  match = path.match(/^\/api\/markets\/([^/]+)$/);
  if (match && req.method === 'GET') {
    const key = decodeURIComponent(match[1]);
    const row = db.prepare('SELECT * FROM markets WHERE key = ?').get(key);
    if (!row) { jsonResponse(res, 404, { error: 'Market not found' }); return true; }
    jsonResponse(res, 200, parseRow('markets', row));
    return true;
  }

  // ── GET /api/markets/:key/banks ──
  match = path.match(/^\/api\/markets\/([^/]+)\/banks$/);
  if (match && req.method === 'GET') {
    const key = decodeURIComponent(match[1]);
    const market = db.prepare('SELECT countries FROM markets WHERE key = ?').get(key);
    if (!market) { jsonResponse(res, 404, { error: 'Market not found' }); return true; }
    const countries = JSON.parse(market.countries);
    if (!countries.length) { jsonResponse(res, 200, []); return true; }
    const placeholders = countries.map(() => '?').join(',');
    const rows = db.prepare(`
      SELECT b.key, b.bank_name, b.country, b.tagline, b.data as bank_data, q.data as qual_data
      FROM banks b LEFT JOIN qualification q ON q.bank_key = b.key
      WHERE b.country IN (${placeholders}) OR b.country LIKE '%' || ? || '%'
      ORDER BY b.bank_name
    `).all(...countries, countries[0]);
    const MIN_SCORE = 3;
    const banks = rows.map(r => {
      const qd = r.qual_data ? JSON.parse(r.qual_data) : null;
      let score = 0;
      if (qd) {
        const fw = { firmographics: 0.10, technographics: 0.15, decision_process: 0.10, landing_zones: 0.20, pain_push: 0.20, power_map: 0.15, partner_access: 0.10 };
        for (const [dim, weight] of Object.entries(fw)) {
          if (qd[dim]?.score) score += qd[dim].score * weight;
        }
      }
      return {
        key: r.key, bank_name: r.bank_name, country: r.country, tagline: r.tagline,
        data: r.bank_data ? JSON.parse(r.bank_data) : null,
        qualification: qd,
        score: Math.round(score * 10) / 10,
      };
    }).filter(b => b.score > MIN_SCORE);
    jsonResponse(res, 200, banks);
    return true;
  }

  // ── GET /api/countries ──
  if (path === '/api/countries' && req.method === 'GET') {
    const rows = db.prepare('SELECT name, market_key FROM countries ORDER BY name').all();
    jsonResponse(res, 200, rows);
    return true;
  }

  // ── GET /api/countries/:name ──
  match = path.match(/^\/api\/countries\/([^/]+)$/);
  if (match && req.method === 'GET') {
    const name = decodeURIComponent(match[1]);
    const row = db.prepare('SELECT * FROM countries WHERE name = ?').get(name);
    if (!row) { jsonResponse(res, 404, { error: 'Country not found' }); return true; }
    jsonResponse(res, 200, parseRow('countries', row));
    return true;
  }

  // ── GET /api/countries/:name/banks ──
  match = path.match(/^\/api\/countries\/([^/]+)\/banks$/);
  if (match && req.method === 'GET') {
    const name = decodeURIComponent(match[1]);
    const rows = db.prepare(`
      SELECT b.key, b.bank_name, b.country, b.tagline, b.data as bank_data, q.data as qual_data,
             vs.data as vs_data
      FROM banks b
      LEFT JOIN qualification q ON q.bank_key = b.key
      LEFT JOIN value_selling vs ON vs.bank_key = b.key
      WHERE b.country = ? OR b.country LIKE '%' || ? || '%'
      ORDER BY b.bank_name
    `).all(name, name);
    const MIN_SCORE = 3;
    const banks = rows.map(r => {
      const qd = r.qual_data ? JSON.parse(r.qual_data) : null;
      // Calculate score server-side for filtering
      let score = 0;
      if (qd) {
        const fw = { firmographics: 0.10, technographics: 0.15, decision_process: 0.10, landing_zones: 0.20, pain_push: 0.20, power_map: 0.15, partner_access: 0.10 };
        for (const [dim, weight] of Object.entries(fw)) {
          if (qd[dim]?.score) score += qd[dim].score * weight;
        }
      }
      return {
        key: r.key, bank_name: r.bank_name, country: r.country, tagline: r.tagline,
        data: r.bank_data ? JSON.parse(r.bank_data) : null,
        qualification: qd,
        value_selling: r.vs_data ? JSON.parse(r.vs_data) : null,
        score: Math.round(score * 10) / 10,
      };
    }).filter(b => b.score > MIN_SCORE);
    jsonResponse(res, 200, banks);
    return true;
  }

  // ── Bank sub-resources ──

  // GET /api/banks/:key/changes — Layer 3 change history
  match = path.match(/^\/api\/banks\/([^/]+)\/changes$/);
  if (match && req.method === 'GET') {
    const key = decodeURIComponent(match[1]);
    const since = url.searchParams.get('since') || null;
    const limit = parseInt(url.searchParams.get('limit') || '20', 10);
    const changes = getChangesForBank(key, { since, limit });
    jsonResponse(res, 200, { bank_key: key, changes, total: changes.length, since });
    return true;
  }

  // ── Meeting History CRUD (Layer 4) ──

  // POST /api/banks/:key/meetings — create meeting record
  match = path.match(/^\/api\/banks\/([^/]+)\/meetings$/);
  if (match && req.method === 'POST') {
    const key = decodeURIComponent(match[1]);
    const body = await parseBody(req);
    if (!body.meeting_date) {
      jsonResponse(res, 400, { error: 'Missing required field: meeting_date' });
      return true;
    }
    const id = crypto.randomUUID();
    db.prepare(`
      INSERT INTO meeting_history (id, bank_key, meeting_date, attendees, key_topics, objections_raised, commitments_made, outcome, notes, source, meeting_type)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      id, key, body.meeting_date,
      body.attendees ? JSON.stringify(body.attendees) : null,
      body.key_topics ? JSON.stringify(body.key_topics) : null,
      body.objections_raised ? JSON.stringify(body.objections_raised) : null,
      body.commitments_made ? JSON.stringify(body.commitments_made) : null,
      body.outcome || null,
      body.notes || null,
      body.source || 'manual',
      body.meeting_type || 'client',
    );
    // Auto-advance deal stage based on meeting activity
    if (body.meeting_type !== 'internal') {
      const currentStatus = db.prepare('SELECT status FROM pipeline_settings WHERE bank_key = ?').get(key);
      const status = currentStatus?.status || 'prospect';
      const meetingTotal = db.prepare("SELECT COUNT(*) as c FROM meeting_history WHERE bank_key = ? AND meeting_type = 'client'").get(key).c;

      let newStatus = null;
      // Auto-advance: prospect → discovery on first meeting
      if (status === 'prospect' && meetingTotal >= 1) newStatus = 'discovery';
      // Auto-advance: discovery → qualification after 3+ meetings
      else if (status === 'discovery' && meetingTotal >= 3) newStatus = 'qualification';

      if (newStatus) {
        db.prepare(`INSERT INTO pipeline_settings (bank_key, status, updated_at) VALUES (?, ?, datetime('now'))
          ON CONFLICT(bank_key) DO UPDATE SET status = ?, updated_at = datetime('now')`)
          .run(key, newStatus, newStatus);
      }
    }

    const created = db.prepare('SELECT * FROM meeting_history WHERE id = ?').get(id);
    jsonResponse(res, 201, parseRow('meeting_history', created));
    return true;
  }

  // GET /api/banks/:key/meetings — list meetings for bank
  if (match && req.method === 'GET') {
    const key = decodeURIComponent(match[1]);
    const limit = parseInt(url.searchParams.get('limit') || '10', 10);
    const rows = db.prepare('SELECT * FROM meeting_history WHERE bank_key = ? ORDER BY meeting_date DESC LIMIT ?').all(key, limit);
    jsonResponse(res, 200, { bank_key: key, meetings: parseRows('meeting_history', rows), total: rows.length });
    return true;
  }

  // PUT /api/banks/:key/meetings/:id — partial update
  match = path.match(/^\/api\/banks\/([^/]+)\/meetings\/([^/]+)$/);
  if (match && req.method === 'PUT') {
    const key = decodeURIComponent(match[1]);
    const id = decodeURIComponent(match[2]);
    const body = await parseBody(req);

    const allowedFields = ['meeting_date', 'attendees', 'key_topics', 'objections_raised', 'commitments_made', 'outcome', 'notes', 'source', 'meeting_type'];
    const jsonFieldSet = new Set(['attendees', 'key_topics', 'objections_raised', 'commitments_made']);
    const updates = [];
    const values = [];

    for (const field of allowedFields) {
      if (body[field] !== undefined) {
        updates.push(field + ' = ?');
        values.push(jsonFieldSet.has(field) && typeof body[field] === 'object' ? JSON.stringify(body[field]) : body[field]);
      }
    }

    if (updates.length === 0) {
      jsonResponse(res, 400, { error: 'No valid fields to update' });
      return true;
    }

    values.push(id, key);
    const result = db.prepare('UPDATE meeting_history SET ' + updates.join(', ') + ' WHERE id = ? AND bank_key = ?').run(...values);
    if (result.changes === 0) {
      jsonResponse(res, 404, { error: 'Meeting not found' });
      return true;
    }
    jsonResponse(res, 200, { ok: true });
    return true;
  }

  // GET /api/banks/:key/qualification
  match = path.match(/^\/api\/banks\/([^/]+)\/qualification$/);
  if (match && req.method === 'GET') {
    const key = decodeURIComponent(match[1]);
    const row = db.prepare('SELECT * FROM qualification WHERE bank_key = ?').get(key);
    if (!row) { jsonResponse(res, 404, { error: 'Not found' }); return true; }
    jsonResponse(res, 200, parseRow('qualification', row));
    return true;
  }
  // PUT /api/banks/:key/qualification
  if (match && req.method === 'PUT') {
    const key = decodeURIComponent(match[1]);
    const body = await parseBody(req);
    db.prepare(`
      INSERT INTO qualification (bank_key, data, updated_at) VALUES (?, ?, datetime('now'))
      ON CONFLICT(bank_key) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at
    `).run(key, JSON.stringify(body));
    jsonResponse(res, 200, { ok: true });
    return true;
  }

  // GET /api/banks/:key/cx
  match = path.match(/^\/api\/banks\/([^/]+)\/cx$/);
  if (match && req.method === 'GET') {
    const key = decodeURIComponent(match[1]);
    const row = db.prepare('SELECT * FROM cx WHERE bank_key = ?').get(key);
    if (!row) { jsonResponse(res, 404, { error: 'Not found' }); return true; }
    jsonResponse(res, 200, parseRow('cx', row));
    return true;
  }

  // GET /api/banks/:key/competition
  match = path.match(/^\/api\/banks\/([^/]+)\/competition$/);
  if (match && req.method === 'GET') {
    const key = decodeURIComponent(match[1]);
    const row = db.prepare('SELECT * FROM competition WHERE bank_key = ?').get(key);
    if (!row) { jsonResponse(res, 404, { error: 'Not found' }); return true; }
    jsonResponse(res, 200, parseRow('competition', row));
    return true;
  }

  // GET /api/banks/:key/value-selling
  match = path.match(/^\/api\/banks\/([^/]+)\/value-selling$/);
  if (match && req.method === 'GET') {
    const key = decodeURIComponent(match[1]);
    const row = db.prepare('SELECT * FROM value_selling WHERE bank_key = ?').get(key);
    if (!row) { jsonResponse(res, 404, { error: 'Not found' }); return true; }
    jsonResponse(res, 200, parseRow('value_selling', row));
    return true;
  }

  // GET /api/banks/:key/sources
  match = path.match(/^\/api\/banks\/([^/]+)\/sources$/);
  if (match && req.method === 'GET') {
    const key = decodeURIComponent(match[1]);
    const rows = db.prepare('SELECT * FROM sources WHERE ref_key = ?').all(key);
    jsonResponse(res, 200, rows);
    return true;
  }

  // GET /api/banks/:key/relationships
  match = path.match(/^\/api\/banks\/([^/]+)\/relationships$/);
  if (match && req.method === 'GET') {
    const key = decodeURIComponent(match[1]);
    const row = db.prepare('SELECT * FROM relationships WHERE bank_key = ?').get(key);
    if (!row) { jsonResponse(res, 200, null); return true; }
    jsonResponse(res, 200, parseRow('relationships', row));
    return true;
  }

  // ── GET /api/banks/:key ── Full bank profile (joined)
  match = path.match(/^\/api\/banks\/([^/]+)$/);
  if (match && req.method === 'GET') {
    const key = decodeURIComponent(match[1]);
    const bank = db.prepare('SELECT * FROM banks WHERE key = ?').get(key);
    if (!bank) { jsonResponse(res, 404, { error: 'Bank not found' }); return true; }

    const qual = db.prepare('SELECT * FROM qualification WHERE bank_key = ?').get(key);
    const cx = db.prepare('SELECT * FROM cx WHERE bank_key = ?').get(key);
    const comp = db.prepare('SELECT * FROM competition WHERE bank_key = ?').get(key);
    const vs = db.prepare('SELECT * FROM value_selling WHERE bank_key = ?').get(key);
    const rel = db.prepare('SELECT * FROM relationships WHERE bank_key = ?').get(key);
    const sources = db.prepare('SELECT * FROM sources WHERE ref_key = ?').all(key);

    // Layer 2: normalized entities
    const personsRows = db.prepare('SELECT * FROM persons WHERE bank_key = ? ORDER BY role_category, canonical_name').all(key);
    const painPointsRows = db.prepare('SELECT * FROM pain_points WHERE bank_key = ?').all(key);
    const landingZonesRows = db.prepare('SELECT * FROM landing_zones WHERE bank_key = ? ORDER BY source, fit_score DESC').all(key);

    // Layer 1: person provenance for source attribution on People tab
    const personProvenanceRows = db.prepare(
      "SELECT field_path, source_type, source_date, confidence_tier, is_stale FROM field_provenance WHERE entity_type = 'person' AND entity_key = ?"
    ).all(key);

    const result = {
      ...parseRow('banks', bank),
      qualification: qual ? parseRow('qualification', qual).data : null,
      cx: cx ? parseRow('cx', cx).data : null,
      competition: comp ? parseRow('competition', comp).data : null,
      value_selling: vs ? parseRow('value_selling', vs).data : null,
      relationship: rel ? parseRow('relationships', rel).data : null,
      sources,
      // Layer 2: normalized entity arrays (backward-compatible — new top-level keys)
      persons: parseRows('persons', personsRows),
      pain_points_normalized: parseRows('pain_points', painPointsRows),
      landing_zones_normalized: parseRows('landing_zones', landingZonesRows),
      // Layer 1: person provenance for source badges
      person_provenance: personProvenanceRows,
    };
    jsonResponse(res, 200, result);
    return true;
  }

  // ── POST /api/banks ── Create a bank
  if (path === '/api/banks' && req.method === 'POST') {
    const body = await parseBody(req);
    if (!body.key || !body.bank_name || !body.country) {
      jsonResponse(res, 400, { error: 'key, bank_name, country required' });
      return true;
    }

    const insertBank = db.transaction((b) => {
      db.prepare(`
        INSERT INTO banks (key, bank_name, country, tagline, data) VALUES (?, ?, ?, ?, ?)
      `).run(b.key, b.bank_name, b.country, b.tagline || null, JSON.stringify(b.data || b));
      if (b.qualification) {
        db.prepare('INSERT INTO qualification (bank_key, data) VALUES (?, ?)').run(b.key, JSON.stringify(b.qualification));
      }
      if (b.cx) {
        db.prepare('INSERT INTO cx (bank_key, app_rating_ios, app_rating_android, digital_maturity, data) VALUES (?, ?, ?, ?, ?)').run(
          b.key, b.cx.app_rating_ios ?? null, b.cx.app_rating_android ?? null, b.cx.digital_maturity || null, JSON.stringify(b.cx)
        );
      }
      if (b.competition) {
        db.prepare('INSERT INTO competition (bank_key, core_banking, digital_platform, data) VALUES (?, ?, ?, ?)').run(
          b.key, b.competition.core_banking || null, b.competition.digital_platform || null, JSON.stringify(b.competition)
        );
      }
      if (b.value_selling) {
        db.prepare('INSERT INTO value_selling (bank_key, data) VALUES (?, ?)').run(b.key, JSON.stringify(b.value_selling));
      }
    });

    try {
      insertBank(body);
      jsonResponse(res, 201, { key: body.key });
    } catch (err) {
      if (err.message.includes('UNIQUE constraint')) {
        jsonResponse(res, 409, { error: `Bank ${body.key} already exists` });
      } else {
        throw err;
      }
    }
    return true;
  }

  // ── PUT /api/banks/:key ──
  match = path.match(/^\/api\/banks\/([^/]+)$/);
  if (match && req.method === 'PUT') {
    const key = decodeURIComponent(match[1]);
    const body = await parseBody(req);
    const existing = db.prepare('SELECT key FROM banks WHERE key = ?').get(key);
    if (!existing) { jsonResponse(res, 404, { error: 'Bank not found' }); return true; }
    db.prepare(`
      UPDATE banks SET bank_name = ?, country = ?, tagline = ?, data = ?, updated_at = datetime('now')
      WHERE key = ?
    `).run(body.bank_name || key, body.country || '', body.tagline || null, JSON.stringify(body.data || body), key);
    jsonResponse(res, 200, { ok: true });
    return true;
  }

  // ── DELETE /api/banks/:key ──
  match = path.match(/^\/api\/banks\/([^/]+)$/);
  if (match && req.method === 'DELETE') {
    const key = decodeURIComponent(match[1]);
    const result = db.prepare('DELETE FROM banks WHERE key = ?').run(key);
    if (result.changes === 0) { jsonResponse(res, 404, { error: 'Bank not found' }); return true; }
    jsonResponse(res, 200, { ok: true, deleted: key });
    return true;
  }

  // ── POST /api/feedback/brief — Submit brief feedback ──
  if (path === '/api/feedback/brief' && req.method === 'POST') {
    const { bankKey, bankName, persona, sectionsUsed, accuracyRating, comment } = await parseBody(req);
    if (!bankName || !sectionsUsed || !accuracyRating) {
      jsonResponse(res, 400, { error: 'Missing required fields: bankName, sectionsUsed, accuracyRating' });
      return true;
    }
    const stmt = db.prepare(`
      INSERT INTO brief_feedback (bank_key, bank_name, persona, sections_used, accuracy_rating, comment)
      VALUES (?, ?, ?, ?, ?, ?)
    `);
    const result = stmt.run(
      bankKey || null,
      bankName,
      persona || null,
      JSON.stringify(sectionsUsed),
      accuracyRating,
      comment || null
    );
    jsonResponse(res, 200, { ok: true, id: result.lastInsertRowid });
    return true;
  }

  // ── GET /api/feedback/brief — Read all brief feedback (admin) ──
  if (path === '/api/feedback/brief' && req.method === 'GET') {
    const rows = db.prepare(`
      SELECT * FROM brief_feedback ORDER BY created_at DESC LIMIT 200
    `).all();
    const parsed = rows.map(r => parseRow('brief_feedback', r));
    jsonResponse(res, 200, { feedback: parsed });
    return true;
  }

  // ── GET /api/feedback/brief/stats — Aggregate feedback stats (admin) ──
  if (path === '/api/feedback/brief/stats' && req.method === 'GET') {
    const totalCount = db.prepare('SELECT COUNT(*) as count FROM brief_feedback').get().count;
    const avgRating = db.prepare('SELECT AVG(accuracy_rating) as avg FROM brief_feedback').get().avg;
    const ratingDist = db.prepare('SELECT accuracy_rating, COUNT(*) as count FROM brief_feedback GROUP BY accuracy_rating ORDER BY accuracy_rating').all();
    const allSections = db.prepare('SELECT sections_used FROM brief_feedback').all();

    // Aggregate section usage counts
    const sectionCounts = {};
    for (const row of allSections) {
      let sections;
      try { sections = JSON.parse(row.sections_used); } catch { sections = []; }
      for (const s of sections) {
        sectionCounts[s] = (sectionCounts[s] || 0) + 1;
      }
    }

    jsonResponse(res, 200, {
      totalCount,
      avgRating: avgRating ? Math.round(avgRating * 10) / 10 : null,
      ratingDistribution: ratingDist,
      sectionUsage: Object.entries(sectionCounts)
        .sort((a, b) => b[1] - a[1])
        .map(([section, count]) => ({ section, count, pct: totalCount > 0 ? Math.round((count / totalCount) * 100) : 0 })),
    });
    return true;
  }

  // ── POST /api/deal-outcomes ── Record a deal outcome
  if (path === '/api/deal-outcomes' && req.method === 'POST') {
    const body = await parseBody(req);
    const { bankKey, outcome } = body;
    if (!bankKey || !outcome) { jsonResponse(res, 400, { error: 'bankKey and outcome required' }); return true; }
    const id = crypto.randomUUID();
    db.prepare(`INSERT INTO deal_outcomes (id, bank_key, outcome, arr_value, close_date, win_reasons, loss_reasons, competitor_won, lessons_learned) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`).run(
      id, bankKey, outcome, body.arrValue || null, body.closeDate || null,
      body.winReasons ? JSON.stringify(body.winReasons) : null,
      body.lossReasons ? JSON.stringify(body.lossReasons) : null,
      body.competitorWon || null, body.lessonsLearned || null
    );
    jsonResponse(res, 201, { id });
    return true;
  }

  // ── GET /api/deal-outcomes ── List all deal outcomes (optional ?bankKey= filter)
  if (path === '/api/deal-outcomes' && req.method === 'GET') {
    const bankKey = url.searchParams.get('bankKey');
    const rows = bankKey
      ? db.prepare('SELECT * FROM deal_outcomes WHERE bank_key = ? ORDER BY created_at DESC').all(bankKey)
      : db.prepare('SELECT * FROM deal_outcomes ORDER BY created_at DESC LIMIT 50').all();
    jsonResponse(res, 200, parseRows('deal_outcomes', rows));
    return true;
  }

  // ── GET /api/deal-outcomes/stats ── Win/loss aggregation
  if (path === '/api/deal-outcomes/stats' && req.method === 'GET') {
    const outcomes = db.prepare('SELECT outcome, COUNT(*) as count FROM deal_outcomes GROUP BY outcome').all();
    const total = outcomes.reduce((s, o) => s + o.count, 0);
    const recentLosses = db.prepare("SELECT bank_key, competitor_won, lessons_learned FROM deal_outcomes WHERE outcome = 'lost' ORDER BY created_at DESC LIMIT 5").all();
    jsonResponse(res, 200, {
      total,
      breakdown: Object.fromEntries(outcomes.map(o => [o.outcome, o.count])),
      winRate: total > 0 ? Math.round((outcomes.find(o => o.outcome === 'won')?.count || 0) / total * 100) : 0,
      recentLosses,
    });
    return true;
  }

  // ── GET /api/banks/:key/status ── Single bank status for bank page
  const bankStatusMatch = path.match(/^\/api\/banks\/([^/]+)\/status$/);
  if (bankStatusMatch && req.method === 'GET') {
    const bk = decodeURIComponent(bankStatusMatch[1]);
    const row = db.prepare('SELECT status, excluded, disqualify_reason FROM pipeline_settings WHERE bank_key = ?').get(bk);
    jsonResponse(res, 200, row || { status: 'prospect', excluded: false, disqualify_reason: null });
    return true;
  }

  // ── GET /api/pipeline-settings ── List all banks with status + exclusion
  if (path === '/api/pipeline-settings' && req.method === 'GET') {
    const banks = db.prepare('SELECT key, bank_name, country, data FROM banks ORDER BY bank_name').all();
    const settings = db.prepare('SELECT bank_key, excluded, status, disqualify_reason FROM pipeline_settings').all();
    const settingsMap = {};
    settings.forEach(s => { settingsMap[s.bank_key] = s; });

    // Get qualification scores
    const quals = db.prepare('SELECT bank_key, data FROM qualification').all();
    const qualMap = {};
    quals.forEach(q => { qualMap[q.bank_key] = JSON.parse(q.data || '{}'); });

    const result = banks.map(b => {
      const s = settingsMap[b.key] || {};
      const bd = JSON.parse(b.data || '{}');
      // Compute score inline
      const qd = qualMap[b.key];
      let score = 0;
      if (qd) {
        const fw = { firmographics: 0.10, technographics: 0.15, decision_process: 0.10, landing_zones: 0.20, pain_push: 0.20, power_map: 0.15, partner_access: 0.10 };
        for (const [dim, weight] of Object.entries(fw)) {
          if (qd[dim]?.score) score += qd[dim].score * weight;
        }
      }
      return {
        key: b.key,
        bank_name: b.bank_name,
        country: b.country,
        score: Math.round(score * 10) / 10,
        deal_size: bd.backbase_qualification?.deal_size || '',
        excluded: s.excluded === 1,
        status: s.status || 'prospect',
        disqualify_reason: s.disqualify_reason || null,
      };
    });
    jsonResponse(res, 200, result);
    return true;
  }

  // ── PUT /api/pipeline-settings/:bankKey ── Update bank status + exclusion
  const settingsMatch = path.match(/^\/api\/pipeline-settings\/([^/]+)$/);
  if (settingsMatch && req.method === 'PUT') {
    const bankKey = decodeURIComponent(settingsMatch[1]);
    const body = await parseBody(req);
    const excluded = body.excluded ? 1 : 0;
    const status = body.status || 'prospect';
    const disqualifyReason = body.disqualify_reason || null;

    // Auto-exclude disqualified and lost banks from pipeline
    const effectiveExcluded = (status === 'disqualified' || status === 'lost') ? 1 : excluded;

    db.prepare(`INSERT INTO pipeline_settings (bank_key, excluded, status, disqualify_reason, updated_at)
      VALUES (?, ?, ?, ?, datetime('now'))
      ON CONFLICT(bank_key) DO UPDATE SET excluded = ?, status = ?, disqualify_reason = ?, updated_at = datetime('now')`)
      .run(bankKey, effectiveExcluded, status, disqualifyReason, effectiveExcluded, status, disqualifyReason);

    jsonResponse(res, 200, { bank_key: bankKey, excluded: !!effectiveExcluded, status, disqualify_reason: disqualifyReason });
    return true;
  }

  // ══════════════════════════════════════════════════════════════
  // INTELLIGENCE LAYER — Plays, Signals, Outputs, Feedback
  // ══════════════════════════════════════════════════════════════

  // ── POST /api/deals/:dealId/plays — Create/activate a play ──
  match = path.match(/^\/api\/deals\/([^/]+)\/plays$/);
  if (match && req.method === 'POST') {
    const dealId = decodeURIComponent(match[1]);
    const body = await parseBody(req);
    if (!body.play_type) { jsonResponse(res, 400, { error: 'play_type required' }); return true; }
    const id = crypto.randomUUID();
    db.prepare('INSERT INTO deal_plays (id, deal_id, play_type) VALUES (?, ?, ?)').run(id, dealId, body.play_type);
    const created = db.prepare('SELECT * FROM deal_plays WHERE id = ?').get(id);
    jsonResponse(res, 201, created);
    return true;
  }

  // ── GET /api/deals/:dealId/plays — List plays for a deal ──
  match = path.match(/^\/api\/deals\/([^/]+)\/plays$/);
  if (match && req.method === 'GET') {
    const dealId = decodeURIComponent(match[1]);
    const rows = db.prepare('SELECT * FROM deal_plays WHERE deal_id = ? ORDER BY created_at DESC').all(dealId);
    // Attach output counts per play
    const plays = rows.map(p => {
      const outputCount = db.prepare('SELECT COUNT(*) as c FROM play_outputs WHERE play_id = ?').get(p.id).c;
      const feedbackCount = db.prepare("SELECT COUNT(*) as c FROM play_outputs WHERE play_id = ? AND feedback IS NOT NULL").get(p.id).c;
      return { ...p, output_count: outputCount, feedback_count: feedbackCount };
    });
    jsonResponse(res, 200, plays);
    return true;
  }

  // ── GET /api/deals/:dealId/plays/:playId — Play detail with outputs ──
  match = path.match(/^\/api\/deals\/([^/]+)\/plays\/([^/]+)$/);
  if (match && req.method === 'GET') {
    const playId = decodeURIComponent(match[2]);
    const play = db.prepare('SELECT * FROM deal_plays WHERE id = ?').get(playId);
    if (!play) { jsonResponse(res, 404, { error: 'Play not found' }); return true; }
    const outputs = db.prepare('SELECT * FROM play_outputs WHERE play_id = ? ORDER BY created_at DESC').all(playId);
    jsonResponse(res, 200, { ...play, outputs: parseRows('play_outputs', outputs) });
    return true;
  }

  // ── PUT /api/deals/:dealId/plays/:playId — Update play status ──
  match = path.match(/^\/api\/deals\/([^/]+)\/plays\/([^/]+)$/);
  if (match && req.method === 'PUT') {
    const playId = decodeURIComponent(match[2]);
    const body = await parseBody(req);
    const updates = [];
    const values = [];
    if (body.status) { updates.push('status = ?'); values.push(body.status); }
    if (body.status === 'completed') { updates.push("completed_at = datetime('now')"); }
    updates.push("updated_at = datetime('now')");
    values.push(playId);
    db.prepare(`UPDATE deal_plays SET ${updates.join(', ')} WHERE id = ?`).run(...values);
    const updated = db.prepare('SELECT * FROM deal_plays WHERE id = ?').get(playId);
    jsonResponse(res, 200, updated);
    return true;
  }

  // ── GET /api/plays/:playId/outputs — List outputs for a play ──
  match = path.match(/^\/api\/plays\/([^/]+)\/outputs$/);
  if (match && req.method === 'GET') {
    const playId = decodeURIComponent(match[1]);
    const rows = db.prepare('SELECT * FROM play_outputs WHERE play_id = ? ORDER BY created_at DESC').all(playId);
    jsonResponse(res, 200, parseRows('play_outputs', rows));
    return true;
  }

  // ── PUT /api/plays/:playId/outputs/:outputId — Update output ──
  match = path.match(/^\/api\/plays\/([^/]+)\/outputs\/([^/]+)$/);
  if (match && req.method === 'PUT') {
    const outputId = decodeURIComponent(match[2]);
    const body = await parseBody(req);
    const updates = [];
    const values = [];
    if (body.content) { updates.push('content = ?'); values.push(body.content); }
    if (body.feedback) { updates.push('feedback = ?'); values.push(body.feedback); }
    if (body.used_in_meeting_id) { updates.push('used_in_meeting_id = ?'); values.push(body.used_in_meeting_id); }
    if (body.confidence_tier) { updates.push('confidence_tier = ?'); values.push(body.confidence_tier); }
    updates.push("updated_at = datetime('now')");
    values.push(outputId);
    db.prepare(`UPDATE play_outputs SET ${updates.join(', ')} WHERE id = ?`).run(...values);
    const updated = db.prepare('SELECT * FROM play_outputs WHERE id = ?').get(outputId);
    jsonResponse(res, 200, parseRow('play_outputs', updated));
    return true;
  }

  // ── POST /api/plays/:playId/outputs/:outputId/feedback — Submit feedback ──
  match = path.match(/^\/api\/plays\/([^/]+)\/outputs\/([^/]+)\/feedback$/);
  if (match && req.method === 'POST') {
    const outputId = decodeURIComponent(match[2]);
    const body = await parseBody(req);
    if (!body.feedback_type) { jsonResponse(res, 400, { error: 'feedback_type required' }); return true; }
    const id = crypto.randomUUID();
    db.prepare('INSERT INTO output_feedback (id, play_output_id, meeting_id, feedback_type, notes, stakeholder_reaction) VALUES (?, ?, ?, ?, ?, ?)').run(
      id, outputId, body.meeting_id || null, body.feedback_type, body.notes || null, body.stakeholder_reaction || null
    );
    // Also update the play_output's feedback field
    db.prepare('UPDATE play_outputs SET feedback = ? WHERE id = ?').run(body.feedback_type, outputId);
    jsonResponse(res, 201, { id, feedback_type: body.feedback_type });
    return true;
  }

  // ── POST /api/deals/:dealId/signals — Create a signal ──
  match = path.match(/^\/api\/deals\/([^/]+)\/signals$/);
  if (match && req.method === 'POST') {
    const dealId = decodeURIComponent(match[1]);
    const body = await parseBody(req);
    if (!body.signal_category || !body.signal_event || !body.title) {
      jsonResponse(res, 400, { error: 'signal_category, signal_event, and title required' });
      return true;
    }
    const id = crypto.randomUUID();
    db.prepare(`INSERT INTO deal_signals (id, deal_id, signal_category, signal_event, title, description, source_url, source_type, severity)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`).run(
      id, dealId, body.signal_category, body.signal_event, body.title,
      body.description || null, body.source_url || null, body.source_type || 'manual', body.severity || 'info'
    );

    // Route signal to active plays based on the shared SIGNAL_CATALOGUE routing config.
    // (Single source of truth: src/data/intelligenceLayer.js — used by both frontend & backend.)
    const targetTypes = getSignalRouting(body.signal_category);
    const activePlays = db.prepare("SELECT id, play_type FROM deal_plays WHERE deal_id = ? AND status = 'active'").all(dealId);
    const routedPlays = activePlays.filter(p => targetTypes.includes(p.play_type));

    let outputsStaled = 0;
    if (routedPlays.length > 0) {
      const playIds = routedPlays.map(p => p.id);
      db.prepare('UPDATE deal_signals SET routed_to_plays = ? WHERE id = ?').run(JSON.stringify(playIds), id);

      // Flag outputs as stale if signal is attention or urgent
      if (body.severity === 'attention' || body.severity === 'urgent') {
        const staleIds = [];
        for (const play of routedPlays) {
          const outputs = db.prepare("SELECT id FROM play_outputs WHERE play_id = ? AND confidence_tier != 'stale'").all(play.id);
          for (const o of outputs) {
            db.prepare("UPDATE play_outputs SET confidence_tier = 'stale', updated_at = datetime('now') WHERE id = ?").run(o.id);
            staleIds.push(o.id);
          }
        }
        outputsStaled = staleIds.length;
        if (staleIds.length > 0) {
          db.prepare('UPDATE deal_signals SET triggered_output_ids = ? WHERE id = ?').run(JSON.stringify(staleIds), id);
        }
      }
    }

    jsonResponse(res, 201, { id, routed_to: routedPlays.length, outputs_staled: outputsStaled });
    return true;
  }

  // ── GET /api/deals/:dealId/signals — List signals ──
  // Query parameters:
  //   ?category=stakeholder|strategic|...  filter by signal category
  //   ?severity=urgent|attention|info       filter by severity
  //   ?sort=relevance|recent|oldest         sort order (default: relevance)
  //   ?include_demos=true                   include is_demo=1 rows
  //   ?include_old=true                     include articles older than 2 years
  //                                         (lasting-strategic articles always shown)
  //
  // Recency policy: by default, articles older than 2 years are filtered out
  // because banking news loses relevance fast. EXCEPTION: signals tagged
  // is_strategic_initiative=1 are always shown (these represent multi-year
  // transformations or lasting plans whose relevance extends beyond 2 years).
  match = path.match(/^\/api\/deals\/([^/]+)\/signals$/);
  if (match && req.method === 'GET') {
    const dealId = decodeURIComponent(match[1]);
    const category = url.searchParams.get('category');
    const severity = url.searchParams.get('severity');
    const sortMode = url.searchParams.get('sort') || 'relevance';
    const includeDemos = url.searchParams.get('include_demos') === 'true';
    const includeOld = url.searchParams.get('include_old') === 'true';

    // Hide-demo decision: if the deal has any non-demo signals, hide demos by default.
    const hasReal = db.prepare(
      "SELECT COUNT(*) AS c FROM deal_signals WHERE deal_id = ? AND COALESCE(is_demo, 0) = 0"
    ).get(dealId)?.c > 0;
    const hideDemos = !includeDemos && hasReal;

    let sql = 'SELECT * FROM deal_signals WHERE deal_id = ?';
    const params = [dealId];
    if (category) { sql += ' AND signal_category = ?'; params.push(category); }
    if (severity) { sql += ' AND severity = ?'; params.push(severity); }
    if (hideDemos) { sql += ' AND COALESCE(is_demo, 0) = 0'; }
    // 2-year recency cap with lasting-strategic-initiative escape hatch.
    // Demos and internal/manual notes are exempt (no public article date to compare).
    if (!includeOld) {
      sql += ` AND (
        COALESCE(is_demo, 0) = 1
        OR source_type IN ('internal', 'manual', 'meeting')
        OR detected_at IS NULL
        OR detected_at >= date('now', '-2 years')
        OR COALESCE(is_strategic_initiative, 0) = 1
      )`;
    }
    // Sort modes
    if (sortMode === 'recent') {
      sql += ' ORDER BY detected_at DESC, COALESCE(relevance_score, 0) DESC';
    } else if (sortMode === 'oldest') {
      sql += ' ORDER BY detected_at ASC, COALESCE(relevance_score, 0) DESC';
    } else {
      // 'relevance' (default) — score DESC, then severity, then most recent
      sql += ` ORDER BY
        COALESCE(relevance_score, 0) DESC,
        CASE severity WHEN 'urgent' THEN 3 WHEN 'attention' THEN 2 ELSE 1 END DESC,
        detected_at DESC`;
    }
    sql += ' LIMIT 50';
    const rows = db.prepare(sql).all(...params);
    // Enrich mentioned_stakeholders with personId so the UI can link chips
    // to the person profile. One matcher per request (cached across rows).
    const matcher = buildStakeholderMatcher(db, dealId);
    const parsed = parseRows('deal_signals', rows).map(r => ({
      ...r,
      mentioned_stakeholders: enrichStakeholders(matcher, r.mentioned_stakeholders),
    }));
    jsonResponse(res, 200, parsed);
    return true;
  }

  // ── POST /api/deals/:dealId/signals/refresh — Pull latest news for ONE bank ──
  // Chains: harvest (5 strands × English + native locales) → classify (Claude
  // scores Backbase relevance + categorizes + emits action_point) → route
  // (promotes score >= 5 into deal_signals). Idempotent: re-running only
  // adds genuinely-new articles. Synchronous — takes 3-5 minutes.
  // Tip: client should set a long timeout (≥ 10 min) when calling.
  match = path.match(/^\/api\/deals\/([^/]+)\/signals\/refresh$/);
  if (match && req.method === 'POST') {
    const dealId = decodeURIComponent(match[1]);
    const bank = db.prepare('SELECT key, bank_name FROM banks WHERE key = ?').get(dealId);
    if (!bank) { jsonResponse(res, 404, { error: `Bank not found: ${dealId}` }); return true; }
    // 409 Conflict if another refresh (manual or scheduled) is already running for this bank
    if (runningRefreshes.has(dealId)) {
      jsonResponse(res, 409, { error: `Refresh already in progress for ${bank.bank_name}. Try again in a few minutes.` });
      return true;
    }
    runningRefreshes.add(dealId);
    const startTime = Date.now();
    // Stage 4B: log the refresh attempt to signal_refresh_log so the UI can
    // show "Last refreshed X minutes ago".
    const logId = db.prepare(
      `INSERT INTO signal_refresh_log (source, bank_key, status, started_at) VALUES (?, ?, 'running', datetime('now'))`
    ).run('manual_refresh', dealId).lastInsertRowid;
    try {
      // Step 1: harvest fresh articles for this bank (English + native locales)
      const { inserted, articlesFound, queriesRun } = await harvestSignalsForBank(db, dealId);
      // Step 2: classify any stale (score=0/unclassified) rows for this bank
      const { classified } = await reclassifyStaleForBank(db, dealId);
      // Step 3: promote actionable signals into deal_signals
      const { promoted } = routeLiveSignals(db, { minScore: 5, bankKey: dealId });
      const durationMs = Date.now() - startTime;
      // Mark the log row complete with stats
      db.prepare(
        `UPDATE signal_refresh_log
         SET status='complete', articles_fetched=?, articles_classified=?, promoted=?, duration_ms=?, completed_at=datetime('now')
         WHERE id=?`
      ).run(inserted, classified, promoted, durationMs, logId);
      jsonResponse(res, 200, {
        bank: bank.bank_name,
        bankKey: dealId,
        queries_run: queriesRun,
        articles_found: articlesFound,
        harvested: inserted,
        classified,
        promoted,
        elapsed_seconds: parseFloat((durationMs / 1000).toFixed(1)),
      });
    } catch (err) {
      console.error(`[refresh] ${dealId} failed:`, err);
      db.prepare(
        `UPDATE signal_refresh_log SET status='error', errors=1, completed_at=datetime('now') WHERE id=?`
      ).run(logId);
      jsonResponse(res, 500, { error: err.message || String(err) });
    } finally {
      runningRefreshes.delete(dealId);
    }
    return true;
  }

  // ── POST /api/deals/:dealId/signals/manual — Manual / LinkedIn signal submission ──
  // Stage 4C. Accepts { url, title, description, category, severity, source_type }.
  // Inserts directly into deal_signals (skipping the live_signals harvest path)
  // because the consultant has already curated it. source_type defaults to 'manual'
  // unless the URL is from linkedin.com (then 'linkedin'). The signal goes
  // into the bank's feed immediately and is eligible for acknowledgment + AI
  // output injection like any other signal.
  match = path.match(/^\/api\/deals\/([^/]+)\/signals\/manual$/);
  if (match && req.method === 'POST') {
    const dealId = decodeURIComponent(match[1]);
    const body = await parseBody(req);
    if (!body.title || body.title.length < 5) {
      jsonResponse(res, 400, { error: 'title is required (≥5 chars)' });
      return true;
    }
    const validCategories = ['stakeholder', 'strategic', 'competitive', 'momentum', 'market', 'regulatory', 'internal'];
    const category = validCategories.includes(body.category) ? body.category : 'strategic';
    const severity = ['urgent', 'attention', 'info'].includes(body.severity) ? body.severity : 'info';
    // LinkedIn URL detection
    const url = body.url ? String(body.url).trim() : null;
    const isLinkedIn = url && /linkedin\.com/i.test(url);
    const sourceType = body.source_type
      || (isLinkedIn ? 'linkedin' : url ? 'manual' : 'internal');
    const signalEvent = isLinkedIn ? 'StakeholderPublishedContent' : `Manual${category[0].toUpperCase()}${category.slice(1)}Note`;

    const id = crypto.randomUUID();
    const detectedAt = body.detected_at || new Date().toISOString().replace('T', ' ').replace(/\.\d+Z$/, '');
    db.prepare(`
      INSERT INTO deal_signals (
        id, deal_id, signal_category, signal_event, title, description,
        source_url, source_type, severity, detected_at, action_point,
        evidence_quote, mentioned_stakeholders, relevance_score, is_demo,
        is_strategic_initiative, domain_tags
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
    `).run(
      id, dealId, category, signalEvent, body.title, body.description || null,
      url, sourceType, severity, detectedAt,
      body.action_point || null,
      body.evidence_quote || null,
      JSON.stringify(body.mentioned_stakeholders || []),
      body.relevance_score != null ? body.relevance_score : 6, // manual signals default to 6 (mid-actionable)
      body.is_strategic_initiative ? 1 : 0,
      JSON.stringify(body.domain_tags || []),
    );
    const created = db.prepare('SELECT * FROM deal_signals WHERE id = ?').get(id);
    jsonResponse(res, 201, parseRow('deal_signals', created));
    return true;
  }

  // ════════════════════════════════════════════════════════════════════
  //  PULSE ENDPOINTS (Strategic Repositioning Sprint 1)
  // ════════════════════════════════════════════════════════════════════

  // GET /api/review-periods — list all periods (for UI dropdowns)
  if (path === '/api/review-periods' && req.method === 'GET') {
    const rows = db.prepare('SELECT * FROM review_periods ORDER BY id DESC').all();
    jsonResponse(res, 200, rows);
    return true;
  }

  // GET /api/banks/:key/pulses — list all pulses for an account
  match = path.match(/^\/api\/banks\/([^/]+)\/pulses$/);
  if (match && req.method === 'GET') {
    const bankKey = decodeURIComponent(match[1]);
    const rows = db.prepare(`
      SELECT id, account_id, period_id, generated_at, generated_by,
             confirmed_by_ae_at, confirmed_by_ae, exported_at
      FROM pulses
      WHERE account_id = ?
      ORDER BY period_id DESC
    `).all(bankKey);
    jsonResponse(res, 200, rows);
    return true;
  }

  // POST /api/banks/:key/pulses?period=2026-Q2 — generate (or regenerate) a pulse.
  // Synchronous; takes ~50ms because it's structured composition, not LLM calls.
  match = path.match(/^\/api\/banks\/([^/]+)\/pulses$/);
  if (match && req.method === 'POST') {
    const bankKey = decodeURIComponent(match[1]);
    const periodId = url.searchParams.get('period') || '2026-Q2';
    try {
      const pulse = generatePulseForBank(db, bankKey, periodId, { generated_by: 'manual' });
      jsonResponse(res, 200, pulse);
    } catch (err) {
      jsonResponse(res, 500, { error: err.message });
    }
    return true;
  }

  // GET /api/pulses/:id — fetch a stored pulse + its overrides
  match = path.match(/^\/api\/pulses\/([^/]+)$/);
  if (match && req.method === 'GET') {
    const pulseId = decodeURIComponent(match[1]);
    const row = db.prepare('SELECT * FROM pulses WHERE id = ?').get(pulseId);
    if (!row) { jsonResponse(res, 404, { error: 'Pulse not found' }); return true; }
    const overrides = db.prepare('SELECT * FROM pulse_overrides WHERE pulse_id = ? ORDER BY created_at DESC').all(pulseId);
    const payload = JSON.parse(row.payload_json);
    payload.id = row.id;
    payload.confirmed_by_ae_at = row.confirmed_by_ae_at;
    payload.confirmed_by_ae = row.confirmed_by_ae;
    payload.exported_at = row.exported_at;
    payload.ae_overrides = overrides;
    jsonResponse(res, 200, payload);
    return true;
  }

  // PUT /api/pulses/:id/cells — apply an AE cell override (telemetry on
  // synthesizer weakness). Body: { cell_path, original_value, override_value, reason, ae_id }
  match = path.match(/^\/api\/pulses\/([^/]+)\/cells$/);
  if (match && req.method === 'PUT') {
    const pulseId = decodeURIComponent(match[1]);
    const body = await parseBody(req);
    if (!body.cell_path || body.override_value === undefined) {
      jsonResponse(res, 400, { error: 'cell_path and override_value required' });
      return true;
    }
    const overrideId = crypto.randomUUID();
    db.prepare(`
      INSERT INTO pulse_overrides (id, pulse_id, cell_path, original_value, override_value, ae_id, reason)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `).run(
      overrideId, pulseId, body.cell_path,
      JSON.stringify(body.original_value ?? null),
      JSON.stringify(body.override_value),
      body.ae_id || null,
      body.reason || null,
    );
    // Apply override to the stored pulse payload by mutating cell_path
    const row = db.prepare('SELECT payload_json FROM pulses WHERE id = ?').get(pulseId);
    if (row) {
      const payload = JSON.parse(row.payload_json);
      // cell_path is a dot-path like "sections.engagement_trend.synthesis"
      const parts = body.cell_path.split('.');
      let target = payload;
      for (let i = 0; i < parts.length - 1; i++) {
        if (target[parts[i]] === undefined) target[parts[i]] = {};
        target = target[parts[i]];
      }
      target[parts[parts.length - 1]] = body.override_value;
      db.prepare('UPDATE pulses SET payload_json = ? WHERE id = ?').run(JSON.stringify(payload), pulseId);
    }
    jsonResponse(res, 201, { id: overrideId, cell_path: body.cell_path });
    return true;
  }

  // POST /api/pulses/:id/confirm — mark the pulse as AE-confirmed (locks for export)
  match = path.match(/^\/api\/pulses\/([^/]+)\/confirm$/);
  if (match && req.method === 'POST') {
    const pulseId = decodeURIComponent(match[1]);
    const body = await parseBody(req);
    db.prepare(`UPDATE pulses SET confirmed_by_ae_at = datetime('now'), confirmed_by_ae = ? WHERE id = ?`)
      .run(body.ae_id || 'unknown', pulseId);
    const updated = db.prepare('SELECT confirmed_by_ae_at, confirmed_by_ae FROM pulses WHERE id = ?').get(pulseId);
    jsonResponse(res, 200, updated);
    return true;
  }

  // ── GET /api/banks/:key/stakeholder-drift — Sprint 2.3 ──
  // Returns per-(stakeholder, topic) sentiment drift cells for the bank.
  // Query params:
  //   ?view=cells     (default) — flat list of drift cells, sorted by influence
  //   ?view=by-person — grouped by stakeholder, each carrying their topic series
  //   ?view=rollup    — bank-level diff buckets (improving/deteriorating/new)
  //   &include_unattributed=1 — include facts whose speaker isn't matched to persons
  //   &min_facts=1    — minimum series length to include a cell
  match = path.match(/^\/api\/banks\/([^/]+)\/stakeholder-drift$/);
  if (match && req.method === 'GET') {
    const bankKey = decodeURIComponent(match[1]);
    const view = url.searchParams.get('view') || 'cells';
    const includeUnattributed = url.searchParams.get('include_unattributed') === '1';
    const minFacts = parseInt(url.searchParams.get('min_facts') || '1', 10);
    const opts = { includeUnattributed, minFacts };
    let payload;
    if (view === 'by-person') payload = getDriftByStakeholder(db, bankKey, opts);
    else if (view === 'rollup') payload = getBankDriftRollup(db, bankKey, opts);
    else payload = getStakeholderDrift(db, bankKey, opts);
    jsonResponse(res, 200, { bank_key: bankKey, view, data: payload });
    return true;
  }

  // ── GET /api/banks/:key/patterns — Sprint 2.4 ──
  // Returns cross-reference patterns (internal fact ↔ external signal pairs).
  // Query: ?min_confidence=high|medium|low   ?unack=1
  match = path.match(/^\/api\/banks\/([^/]+)\/patterns$/);
  if (match && req.method === 'GET') {
    const bankKey = decodeURIComponent(match[1]);
    const minConfidence = url.searchParams.get('min_confidence') || null;
    const onlyUnacknowledged = url.searchParams.get('unack') === '1';
    const patterns = getPatternsForBank(db, bankKey, { minConfidence, onlyUnacknowledged });
    jsonResponse(res, 200, { bank_key: bankKey, count: patterns.length, patterns });
    return true;
  }

  // ── POST /api/banks/:key/patterns/run — trigger cross-reference engine on demand
  match = path.match(/^\/api\/banks\/([^/]+)\/patterns\/run$/);
  if (match && req.method === 'POST') {
    const bankKey = decodeURIComponent(match[1]);
    const body = await parseBody(req).catch(() => ({}));
    const result = await runCrossReferenceForBank(db, bankKey, {
      windowDays: body.window_days || 60,
      maxCandidates: body.max_candidates || 4,
      force: body.force === true,
    });
    jsonResponse(res, 200, { bank_key: bankKey, ...result });
    return true;
  }

  // ── GET /api/banks/:key/change-feed — Sprint 4.2 ──
  // Returns the unified change feed for one bank. Query:
  //   ?lookback=30          — days back from now (default 30)
  //   ?sort=significance|time  (default time)
  //   ?min_significance=N   — filter (default 0)
  //   ?limit=N              — cap (default 100)
  //   ?include=NEW_SIGNAL,NEW_PATTERN,…  (default all 6)
  match = path.match(/^\/api\/banks\/([^/]+)\/change-feed$/);
  if (match && req.method === 'GET') {
    const bankKey = decodeURIComponent(match[1]);
    const lookback = parseInt(url.searchParams.get('lookback') || '30', 10);
    const sort = url.searchParams.get('sort') || 'time';
    const minSig = parseInt(url.searchParams.get('min_significance') || '0', 10);
    const limit = parseInt(url.searchParams.get('limit') || '100', 10);
    const include = url.searchParams.get('include')?.split(',').filter(Boolean);
    const opts = { bankKey, lookbackDays: lookback, sort, minSignificance: minSig, limit };
    if (include?.length) opts.include = include;
    const events = getChangeFeed(db, opts);
    const counts = getChangeFeedCounts(db, { bankKey, lookbackDays: lookback });
    jsonResponse(res, 200, { bank_key: bankKey, lookback_days: lookback, counts, events });
    return true;
  }

  // ── GET /api/change-feed — Sprint 4.3 ──
  // Portfolio-wide change feed (no bank filter). Same query params.
  if (path === '/api/change-feed' && req.method === 'GET') {
    const lookback = parseInt(url.searchParams.get('lookback') || '7', 10);
    const sort = url.searchParams.get('sort') || 'significance';
    const minSig = parseInt(url.searchParams.get('min_significance') || '5', 10);
    const limit = parseInt(url.searchParams.get('limit') || '50', 10);
    const include = url.searchParams.get('include')?.split(',').filter(Boolean);
    const opts = { bankKey: null, lookbackDays: lookback, sort, minSignificance: minSig, limit };
    if (include?.length) opts.include = include;
    const events = getChangeFeed(db, opts);
    const counts = getChangeFeedCounts(db, { lookbackDays: lookback });
    jsonResponse(res, 200, { lookback_days: lookback, counts, events });
    return true;
  }

  // ── POST /api/portfolio/query — Sprint 5.2 ──
  // Body: { filter: { op, predicates, children } } — see portfolioQuery.mjs
  // Returns: { matched: [...], total: N, leaf_predicates: N }
  if (path === '/api/portfolio/query' && req.method === 'POST') {
    const body = await parseBody(req);
    if (!body || typeof body !== 'object' || !body.filter) {
      jsonResponse(res, 400, { error: 'filter is required' });
      return true;
    }
    let results;
    try { results = runPortfolioQuery(db, body.filter); }
    catch (err) {
      jsonResponse(res, 400, { error: 'Query failed', detail: err.message });
      return true;
    }
    jsonResponse(res, 200, { total: results.length, matched: results });
    return true;
  }

  // ── GET /api/portfolio/query/examples — pre-built sample queries
  if (path === '/api/portfolio/query/examples' && req.method === 'GET') {
    jsonResponse(res, 200, { examples: EXAMPLE_QUERIES });
    return true;
  }

  // ──────────────────────────────────────────────────────────────────
  // Region + country aggregations (post-B-series). Both surfaces share the
  // same library — region resolves bank list via market.data.countries[],
  // country resolves via direct LIKE-tolerant match. The helper below picks
  // the right resolver based on URL pattern.
  // ──────────────────────────────────────────────────────────────────

  function resolveBankSet(kind, identifier) {
    if (kind === 'regions') return { banks: getBanksForRegion(db, identifier), label: identifier };
    if (kind === 'countries') return { banks: getBanksForCountry(db, identifier), label: identifier };
    return { banks: [], label: identifier };
  }

  // GET /api/regions/:key/intel  OR  /api/countries/:name/intel
  // Returns a single composite payload for the page (one round-trip).
  // Intentionally combines aggregations to minimize UI fetches.
  match = path.match(/^\/api\/(regions|countries)\/([^/]+)\/intel$/);
  if (match && req.method === 'GET') {
    const kind = match[1];
    const identifier = decodeURIComponent(match[2]);
    const { banks } = resolveBankSet(kind, identifier);
    const bankKeys = banks.map(b => b.key);
    const period = url.searchParams.get('period') || '2026-Q2';
    const priorPeriod = url.searchParams.get('prior_period') || (period === '2026-Q2' ? '2026-Q1' : '2026-Q1');
    const opps = getComputedOpportunities(db, bankKeys, { withinDays: 60 });
    const grade_distribution = getRegionGradeDistribution(db, bankKeys);
    const top_patterns = getRegionPatterns(db, bankKeys, { limit: 8, minConfidence: 'medium' });
    const drift_heatmap = getRegionDriftHeatmap(db, bankKeys).slice(0, 10);
    const engagement = getRegionEngagementSummary(db, bankKeys, { from: priorPeriod, to: period });
    jsonResponse(res, 200, {
      kind,
      identifier,
      banks: banks.map(b => ({ key: b.key, bank_name: b.bank_name, country: b.country })),
      bank_count: banks.length,
      computed_opportunities: opps,
      grade_distribution,
      top_patterns,
      drift_heatmap,
      engagement_summary: engagement,
    });
    return true;
  }

  // GET /api/regions/:key/change-feed  OR  /api/countries/:name/change-feed
  // Forwards to getChangeFeed with bankKeys filter pre-resolved server-side.
  match = path.match(/^\/api\/(regions|countries)\/([^/]+)\/change-feed$/);
  if (match && req.method === 'GET') {
    const kind = match[1];
    const identifier = decodeURIComponent(match[2]);
    const { banks } = resolveBankSet(kind, identifier);
    const bankKeys = banks.map(b => b.key);
    const lookback = parseInt(url.searchParams.get('lookback') || '30', 10);
    const sort = url.searchParams.get('sort') || 'significance';
    const minSig = parseInt(url.searchParams.get('min_significance') || '0', 10);
    const limit = parseInt(url.searchParams.get('limit') || '100', 10);
    const include = url.searchParams.get('include')?.split(',').filter(Boolean);
    const opts = { bankKeys, lookbackDays: lookback, sort, minSignificance: minSig, limit };
    if (include?.length) opts.include = include;
    const events = getChangeFeed(db, opts);
    const counts = getChangeFeedCounts(db, { bankKeys, lookbackDays: lookback });
    jsonResponse(res, 200, { kind, identifier, bank_count: bankKeys.length, lookback_days: lookback, counts, events });
    return true;
  }

  // GET /api/regions/:key/pulse  OR  /api/countries/:name/pulse?period=2026-Q2
  // Returns the aggregated region/country pulse (Tier 2).
  match = path.match(/^\/api\/(regions|countries)\/([^/]+)\/pulse$/);
  if (match && req.method === 'GET') {
    const kind = match[1];
    const identifier = decodeURIComponent(match[2]);
    const { banks } = resolveBankSet(kind, identifier);
    const bankKeys = banks.map(b => b.key);
    const period = url.searchParams.get('period') || '2026-Q2';
    const priorPeriod = url.searchParams.get('prior_period');
    const pulse = generateRegionPulse(db, {
      bankKeys, periodId: period,
      regionLabel: identifier,
      ...(priorPeriod ? { priorPeriodId: priorPeriod } : {}),
    });
    jsonResponse(res, 200, pulse || { error: 'No banks in scope' });
    return true;
  }

  // ──────────────────────────────────────────────────────────────────
  // AE↔VC bridge endpoints (Wave 2)
  // ──────────────────────────────────────────────────────────────────

  // GET /api/engagements?bank_key=...&open_only=1
  if (path === '/api/engagements' && req.method === 'GET') {
    const bankKey = url.searchParams.get('bank_key');
    const openOnly = url.searchParams.get('open_only') === '1';
    const state = url.searchParams.get('state');
    jsonResponse(res, 200, { engagements: listEngagements(db, { bankKey, state, openOnly }) });
    return true;
  }

  // GET /api/banks/:key/engagement-summary — at-a-glance state per bank
  match = path.match(/^\/api\/banks\/([^/]+)\/engagement-summary$/);
  if (match && req.method === 'GET') {
    const bankKey = decodeURIComponent(match[1]);
    jsonResponse(res, 200, getBankEngagementSummary(db, bankKey));
    return true;
  }

  // POST /api/engagements — create
  if (path === '/api/engagements' && req.method === 'POST') {
    const body = await parseBody(req);
    try {
      const eng = createEngagement(db, body);
      jsonResponse(res, 201, eng);
    } catch (err) {
      jsonResponse(res, 400, { error: err.message });
    }
    return true;
  }

  // POST /api/engagements/:id/transition — change state
  match = path.match(/^\/api\/engagements\/([^/]+)\/transition$/);
  if (match && req.method === 'POST') {
    const id = decodeURIComponent(match[1]);
    const body = await parseBody(req);
    try {
      const eng = transitionEngagement(db, id, body.state, { outcome: body.outcome });
      jsonResponse(res, 200, eng);
    } catch (err) {
      jsonResponse(res, 400, { error: err.message });
    }
    return true;
  }

  // GET /api/engagements/:id — detail + artifacts
  match = path.match(/^\/api\/engagements\/([^/]+)$/);
  if (match && req.method === 'GET') {
    const id = decodeURIComponent(match[1]);
    const eng = getEngagement(db, id);
    if (!eng) { jsonResponse(res, 404, { error: 'Not found' }); return true; }
    const artifacts = listArtifacts(db, { engagementId: id });
    jsonResponse(res, 200, { ...eng, artifacts });
    return true;
  }

  // POST /api/engagements/:id/artifacts — register a deliverable
  match = path.match(/^\/api\/engagements\/([^/]+)\/artifacts$/);
  if (match && req.method === 'POST') {
    const id = decodeURIComponent(match[1]);
    const body = await parseBody(req);
    try {
      const artifact = registerArtifact(db, { engagement_id: id, ...body });
      jsonResponse(res, 201, artifact);
    } catch (err) {
      jsonResponse(res, 400, { error: err.message });
    }
    return true;
  }

  // POST /api/engagements/:id/ingest — ingest a deliverable file
  match = path.match(/^\/api\/engagements\/([^/]+)\/ingest$/);
  if (match && req.method === 'POST') {
    const id = decodeURIComponent(match[1]);
    const body = await parseBody(req);
    try {
      const artifact = ingestDeliverable(db, { engagement_id: id, ...body });
      jsonResponse(res, 201, artifact);
    } catch (err) {
      jsonResponse(res, 400, { error: err.message });
    }
    return true;
  }

  // GET /api/banks/:key/handoff-snapshot — generate snapshot (read-only, doesn't persist)
  match = path.match(/^\/api\/banks\/([^/]+)\/handoff-snapshot$/);
  if (match && req.method === 'GET') {
    const bankKey = decodeURIComponent(match[1]);
    const period = url.searchParams.get('period') || '2026-Q2';
    const format = url.searchParams.get('format') || 'json';
    try {
      const snap = buildHandoffSnapshot(db, bankKey, { period });
      if (format === 'markdown') {
        res.setHeader('Content-Type', 'text/markdown');
        res.end(snapshotToMarkdown(snap));
      } else {
        jsonResponse(res, 200, snap);
      }
    } catch (err) {
      jsonResponse(res, 400, { error: err.message });
    }
    return true;
  }

  // POST /api/banks/:key/handoff — formal AE→VC handoff: creates engagement + persists snapshot
  match = path.match(/^\/api\/banks\/([^/]+)\/handoff$/);
  if (match && req.method === 'POST') {
    const bankKey = decodeURIComponent(match[1]);
    const body = await parseBody(req);
    try {
      const snapshot = buildHandoffSnapshot(db, bankKey, { period: body.period || '2026-Q2' });
      const engagement = createEngagement(db, {
        bank_key: bankKey,
        engagement_type: body.engagement_type || 'value_assessment',
        title: body.title || `${snapshot.bank.name} — ${body.engagement_type || 'value_assessment'}`,
        ae_lead: body.ae_lead || null,
        vc_lead: body.vc_lead || null,
        kickoff_date: body.kickoff_date || new Date().toISOString().slice(0, 10),
        target_close_date: body.target_close_date || null,
        handoff_snapshot: snapshot,
      });
      jsonResponse(res, 201, { engagement, snapshot_size: JSON.stringify(snapshot).length });
    } catch (err) {
      jsonResponse(res, 400, { error: err.message });
    }
    return true;
  }

  // ── Meeting intel input (Wave 3) ──
  // POST /api/banks/:key/ingest-transcript
  match = path.match(/^\/api\/banks\/([^/]+)\/ingest-transcript$/);
  if (match && req.method === 'POST') {
    const bankKey = decodeURIComponent(match[1]);
    const body = await parseBody(req);
    try {
      const result = await ingestTranscript(db, { bank_key: bankKey, ...body });
      jsonResponse(res, 201, result);
    } catch (err) {
      jsonResponse(res, 400, { error: err.message });
    }
    return true;
  }
  // POST /api/banks/:key/ingest-email
  match = path.match(/^\/api\/banks\/([^/]+)\/ingest-email$/);
  if (match && req.method === 'POST') {
    const bankKey = decodeURIComponent(match[1]);
    const body = await parseBody(req);
    try {
      const result = await ingestEmailThread(db, { bank_key: bankKey, ...body });
      jsonResponse(res, 201, result);
    } catch (err) {
      jsonResponse(res, 400, { error: err.message });
    }
    return true;
  }

  // ── Bank notes (shared AE+VC comment thread) ──
  match = path.match(/^\/api\/banks\/([^/]+)\/notes$/);
  if (match && req.method === 'GET') {
    const bankKey = decodeURIComponent(match[1]);
    const notes = db.prepare(`SELECT * FROM bank_notes WHERE bank_key = ? ORDER BY pinned DESC, created_at DESC`).all(bankKey);
    jsonResponse(res, 200, { notes });
    return true;
  }
  if (match && req.method === 'POST') {
    const bankKey = decodeURIComponent(match[1]);
    const body = await parseBody(req);
    if (!body.body || !body.author) { jsonResponse(res, 400, { error: 'body and author required' }); return true; }
    const id = crypto.randomUUID();
    db.prepare(`INSERT INTO bank_notes (id, bank_key, author, author_role, body, pinned) VALUES (?, ?, ?, ?, ?, ?)`)
      .run(id, bankKey, body.author, body.author_role || 'other', body.body, body.pinned ? 1 : 0);
    jsonResponse(res, 201, { id, bank_key: bankKey });
    return true;
  }
  match = path.match(/^\/api\/notes\/([^/]+)$/);
  if (match && req.method === 'DELETE') {
    db.prepare('DELETE FROM bank_notes WHERE id = ?').run(decodeURIComponent(match[1]));
    jsonResponse(res, 200, { deleted: true });
    return true;
  }

  // ── POST /api/portfolio/query/translate — B3: NL → predicate JSON
  // Body: { query: "Swedish banks with a deteriorating CFO" }
  // Returns: { ok, filter, explanation, warnings } — filter is then run through
  // the existing /api/portfolio/query endpoint by the UI (deterministic engine).
  if (path === '/api/portfolio/query/translate' && req.method === 'POST') {
    const body = await parseBody(req);
    if (!body?.query) {
      jsonResponse(res, 400, { ok: false, error: 'query is required' });
      return true;
    }
    const result = await translateNLQuery(body.query);
    jsonResponse(res, result.ok ? 200 : 400, result);
    return true;
  }

  // ── GET /api/portfolio/saved-views — Sprint 5.4 (list)
  if (path === '/api/portfolio/saved-views' && req.method === 'GET') {
    let rows = [];
    try {
      rows = db.prepare(`SELECT id, name, description, filter_json, created_at, updated_at FROM portfolio_saved_views ORDER BY updated_at DESC`).all();
    } catch { rows = []; }
    jsonResponse(res, 200, { views: rows.map(r => ({ ...r, filter: JSON.parse(r.filter_json || '{}') })) });
    return true;
  }

  // ── POST /api/portfolio/saved-views — create
  if (path === '/api/portfolio/saved-views' && req.method === 'POST') {
    const body = await parseBody(req);
    if (!body?.name || !body?.filter) {
      jsonResponse(res, 400, { error: 'name and filter required' });
      return true;
    }
    const id = crypto.randomUUID();
    db.prepare(`
      INSERT INTO portfolio_saved_views (id, name, description, filter_json)
      VALUES (?, ?, ?, ?)
    `).run(id, body.name, body.description || null, JSON.stringify(body.filter));
    jsonResponse(res, 201, { id, name: body.name });
    return true;
  }

  // ── DELETE /api/portfolio/saved-views/:id
  match = path.match(/^\/api\/portfolio\/saved-views\/([^/]+)$/);
  if (match && req.method === 'DELETE') {
    const id = decodeURIComponent(match[1]);
    db.prepare(`DELETE FROM portfolio_saved_views WHERE id = ?`).run(id);
    jsonResponse(res, 200, { id, deleted: true });
    return true;
  }

  // ── POST /api/patterns/:id/acknowledge — AE marks a pattern as seen/handled
  match = path.match(/^\/api\/patterns\/([^/]+)\/acknowledge$/);
  if (match && req.method === 'POST') {
    const patternId = decodeURIComponent(match[1]);
    const body = await parseBody(req).catch(() => ({}));
    db.prepare(`UPDATE pattern_matches SET acknowledged_at = datetime('now'), acknowledged_by = ? WHERE id = ?`)
      .run(body.ae_id || 'unknown', patternId);
    jsonResponse(res, 200, { id: patternId, acknowledged: true });
    return true;
  }

  // ── POST /api/og-fetch — Fetch Open Graph metadata for a URL ──
  // Used by the manual-submission UI to auto-populate title/description from
  // a pasted URL before the consultant clicks Submit.
  if (path === '/api/og-fetch' && req.method === 'POST') {
    const body = await parseBody(req);
    if (!body.url || typeof body.url !== 'string') {
      jsonResponse(res, 400, { error: 'url is required' });
      return true;
    }
    const og = await fetchOpenGraph(body.url);
    jsonResponse(res, 200, og || { error: 'Could not fetch metadata' });
    return true;
  }

  // ── GET /api/deals/:dealId/signals/freshness — when was last refresh + summary ──
  match = path.match(/^\/api\/deals\/([^/]+)\/signals\/freshness$/);
  if (match && req.method === 'GET') {
    const dealId = decodeURIComponent(match[1]);
    const lastRefresh = db.prepare(`
      SELECT completed_at, articles_fetched, promoted, status
      FROM signal_refresh_log
      WHERE bank_key = ? AND status = 'complete'
      ORDER BY completed_at DESC LIMIT 1
    `).get(dealId);
    // Fall back to MAX(detected_at) on existing deal_signals if no refresh log
    const fallbackLatest = db.prepare(`
      SELECT MAX(detected_at) AS latest FROM deal_signals
      WHERE deal_id = ? AND COALESCE(is_demo, 0) = 0
    `).get(dealId)?.latest;
    jsonResponse(res, 200, {
      bankKey: dealId,
      last_refreshed_at: lastRefresh?.completed_at || null,
      last_article_at: fallbackLatest || null,
      last_refresh_added: lastRefresh?.articles_fetched || 0,
      last_refresh_promoted: lastRefresh?.promoted || 0,
    });
    return true;
  }

  // ── PUT /api/deals/:dealId/signals/:signalId — Acknowledge/action ──
  match = path.match(/^\/api\/deals\/([^/]+)\/signals\/([^/]+)$/);
  if (match && req.method === 'PUT') {
    const signalId = decodeURIComponent(match[2]);
    const body = await parseBody(req);
    // acknowledged: true → set timestamp; acknowledged: false → clear it (undo)
    // We must check `body.acknowledged !== undefined` so an explicit `false`
    // is accepted; the older truthy check was rejecting un-ack requests.
    if (body.acknowledged === true) {
      db.prepare("UPDATE deal_signals SET acknowledged_at = datetime('now') WHERE id = ?").run(signalId);
    } else if (body.acknowledged === false) {
      db.prepare('UPDATE deal_signals SET acknowledged_at = NULL WHERE id = ?').run(signalId);
    }
    // Same toggle pattern for actioned
    if (body.actioned === true) {
      db.prepare("UPDATE deal_signals SET actioned_at = datetime('now') WHERE id = ?").run(signalId);
    } else if (body.actioned === false) {
      db.prepare('UPDATE deal_signals SET actioned_at = NULL WHERE id = ?').run(signalId);
    }
    const updated = db.prepare('SELECT * FROM deal_signals WHERE id = ?').get(signalId);
    jsonResponse(res, 200, parseRow('deal_signals', updated));
    return true;
  }

  // ── GET /api/deals/:dealId/signals/summary — Signal summary for WhatsChanged ──
  match = path.match(/^\/api\/deals\/([^/]+)\/signals\/summary$/);
  if (match && req.method === 'GET') {
    const dealId = decodeURIComponent(match[1]);
    const total = db.prepare('SELECT COUNT(*) as c FROM deal_signals WHERE deal_id = ?').get(dealId).c;
    const unacknowledged = db.prepare('SELECT COUNT(*) as c FROM deal_signals WHERE deal_id = ? AND acknowledged_at IS NULL').get(dealId).c;
    const bySeverity = db.prepare('SELECT severity, COUNT(*) as c FROM deal_signals WHERE deal_id = ? GROUP BY severity').all(dealId);
    const byCategory = db.prepare('SELECT signal_category, COUNT(*) as c FROM deal_signals WHERE deal_id = ? AND acknowledged_at IS NULL GROUP BY signal_category').all(dealId);
    const recent = db.prepare('SELECT * FROM deal_signals WHERE deal_id = ? ORDER BY detected_at DESC LIMIT 5').all(dealId);
    // Count plays with stale outputs
    const playsWithStale = db.prepare(`
      SELECT COUNT(DISTINCT dp.id) as c FROM deal_plays dp
      JOIN play_outputs po ON po.play_id = dp.id
      WHERE dp.deal_id = ? AND dp.status = 'active' AND po.confidence_tier = 'stale'
    `).get(dealId).c;

    jsonResponse(res, 200, {
      total, unacknowledged,
      by_severity: Object.fromEntries(bySeverity.map(r => [r.severity, r.c])),
      by_category: Object.fromEntries(byCategory.map(r => [r.signal_category, r.c])),
      recent: parseRows('deal_signals', recent),
      plays_with_stale_outputs: playsWithStale,
    });
    return true;
  }

  // ── GET /api/deals/:dealId/twin — Get current twin state ──
  match = path.match(/^\/api\/deals\/([^/]+)\/twin$/);
  if (match && req.method === 'GET') {
    const dealId = decodeURIComponent(match[1]);
    const state = db.prepare('SELECT * FROM deal_twin_state WHERE deal_id = ?').get(dealId);
    if (!state) {
      jsonResponse(res, 200, { deal_id: dealId, deal_health_score: null, message: 'No twin state calculated yet' });
    } else {
      jsonResponse(res, 200, parseRow('deal_twin_state', state));
    }
    return true;
  }

  // ── GET /api/deals/:dealId/twin/history — Historical snapshots ──
  match = path.match(/^\/api\/deals\/([^/]+)\/twin\/history$/);
  if (match && req.method === 'GET') {
    const dealId = decodeURIComponent(match[1]);
    const rows = db.prepare('SELECT * FROM deal_twin_history WHERE deal_id = ? ORDER BY snapshot_date DESC LIMIT 30').all(dealId);
    jsonResponse(res, 200, rows);
    return true;
  }

  // ══════════════════════════════════════════════════════════════
  // STRATEGIC ACCOUNT PLAN — Person CRUD (stakeholder map editing)
  // ══════════════════════════════════════════════════════════════

  // Helper: serialize JSON fields before writing
  const serializePersonJsonFields = (body) => {
    const out = { ...body };
    for (const key of ['meddicc_roles', 'priorities', 'kpis_of_interest', 'aliases']) {
      if (out[key] !== undefined && out[key] !== null && typeof out[key] !== 'string') {
        out[key] = JSON.stringify(out[key]);
      }
    }
    return out;
  };

  // ── GET /api/banks/:key/persons/:personId/signals — Signals mentioning this person ──
  // Powers the "Recent signals mentioning this person" panel on stakeholder profiles.
  // Searches deal_signals.mentioned_stakeholders for the person's canonical name + aliases.
  match = path.match(/^\/api\/banks\/([^/]+)\/persons\/([^/]+)\/signals$/);
  if (match && req.method === 'GET') {
    const bankKey = decodeURIComponent(match[1]);
    const personId = decodeURIComponent(match[2]);
    const person = db.prepare('SELECT id, canonical_name, aliases FROM persons WHERE id = ? AND bank_key = ?').get(personId, bankKey);
    if (!person) { jsonResponse(res, 404, { error: 'Person not found' }); return true; }

    // Build the set of names to search for
    const names = [person.canonical_name];
    if (person.aliases) {
      try {
        const a = typeof person.aliases === 'string' ? JSON.parse(person.aliases) : person.aliases;
        if (Array.isArray(a)) names.push(...a);
      } catch { /* not json — treat as comma-separated */
        names.push(...String(person.aliases).split(',').map(s => s.trim()));
      }
    }
    // Match in JSON via LIKE — fast enough at our scale (≤500 deal_signals per bank)
    const likeClauses = names.map(() => 'mentioned_stakeholders LIKE ?').join(' OR ');
    const likeParams = names.map(n => `%"${n}"%`);
    const sql = `
      SELECT id, signal_category, signal_event, title, description,
             source_url, source_type, severity, detected_at,
             acknowledged_at, action_point, evidence_quote,
             relevance_score, is_strategic_initiative, domain_tags,
             mentioned_stakeholders
      FROM deal_signals
      WHERE deal_id = ?
        AND COALESCE(is_demo, 0) = 0
        AND (${likeClauses})
      ORDER BY COALESCE(relevance_score, 0) DESC, detected_at DESC
      LIMIT 30
    `;
    const rows = db.prepare(sql).all(bankKey, ...likeParams);
    jsonResponse(res, 200, parseRows('deal_signals', rows));
    return true;
  }

  // ── POST /api/banks/:key/persons — Create a new person ──
  match = path.match(/^\/api\/banks\/([^/]+)\/persons$/);
  if (match && req.method === 'POST') {
    const bankKey = decodeURIComponent(match[1]);
    const body = await parseBody(req);
    if (!body.canonical_name) { jsonResponse(res, 400, { error: 'canonical_name required' }); return true; }
    const id = crypto.randomUUID();
    const data = serializePersonJsonFields(body);
    try {
      db.prepare(`INSERT INTO persons (
        id, bank_key, canonical_name, role, role_category, lob, reports_to, seniority_order,
        linkedin_url, note, confidence_tier, aliases,
        meddicc_roles, influence_score, engagement_status, support_status,
        relationship_type, linkedin_intel, priorities, kpis_of_interest,
        discovery_source, created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))`).run(
        id, bankKey,
        data.canonical_name, data.role || null, data.role_category || null,
        data.lob || null, data.reports_to || null, data.seniority_order || null,
        data.linkedin_url || null, data.note || null, data.confidence_tier || 2, data.aliases || null,
        data.meddicc_roles || null, data.influence_score || null, data.engagement_status || 'neutral',
        data.support_status || 'neutral', data.relationship_type || null, data.linkedin_intel || null,
        data.priorities || null, data.kpis_of_interest || null,
        data.discovery_source || 'manual'
      );
      const created = db.prepare('SELECT * FROM persons WHERE id = ?').get(id);
      jsonResponse(res, 201, parseRow('persons', created));
    } catch (err) {
      if (err.code === 'SQLITE_CONSTRAINT_UNIQUE') {
        jsonResponse(res, 409, { error: `Person '${body.canonical_name}' already exists for ${bankKey}` });
      } else {
        jsonResponse(res, 500, { error: err.message });
      }
    }
    return true;
  }

  // ── PUT /api/banks/:key/persons/:id — Update any person fields ──
  match = path.match(/^\/api\/banks\/([^/]+)\/persons\/([^/]+)$/);
  if (match && req.method === 'PUT') {
    const personId = decodeURIComponent(match[2]);
    const body = await parseBody(req);
    const existing = db.prepare('SELECT id FROM persons WHERE id = ?').get(personId);
    if (!existing) { jsonResponse(res, 404, { error: 'Person not found' }); return true; }

    // Whitelist updatable fields
    const updatable = [
      'canonical_name', 'role', 'role_category', 'lob', 'reports_to', 'seniority_order',
      'linkedin_url', 'note', 'confidence_tier', 'aliases',
      'meddicc_roles', 'influence_score', 'engagement_status', 'support_status',
      'relationship_type', 'linkedin_intel', 'priorities', 'kpis_of_interest',
    ];
    const data = serializePersonJsonFields(body);
    const updates = [];
    const values = [];
    for (const field of updatable) {
      if (data[field] !== undefined) {
        updates.push(`${field} = ?`);
        values.push(data[field]);
      }
    }
    if (updates.length === 0) { jsonResponse(res, 400, { error: 'No updatable fields provided' }); return true; }
    updates.push("updated_at = datetime('now')");
    values.push(personId);
    db.prepare(`UPDATE persons SET ${updates.join(', ')} WHERE id = ?`).run(...values);
    const updated = db.prepare('SELECT * FROM persons WHERE id = ?').get(personId);
    jsonResponse(res, 200, parseRow('persons', updated));
    return true;
  }

  // ── DELETE /api/banks/:key/persons/:id — Remove a person ──
  match = path.match(/^\/api\/banks\/([^/]+)\/persons\/([^/]+)$/);
  if (match && req.method === 'DELETE') {
    const personId = decodeURIComponent(match[2]);
    const result = db.prepare('DELETE FROM persons WHERE id = ?').run(personId);
    if (result.changes === 0) { jsonResponse(res, 404, { error: 'Person not found' }); return true; }
    jsonResponse(res, 200, { deleted: true, id: personId });
    return true;
  }

  // ── PATCH /api/banks/:key/persons/:id/position — Drag-and-drop position update ──
  // Lightweight endpoint for the stakeholder matrix — only influence_score + engagement_status
  match = path.match(/^\/api\/banks\/([^/]+)\/persons\/([^/]+)\/position$/);
  if (match && req.method === 'PATCH') {
    const personId = decodeURIComponent(match[2]);
    const body = await parseBody(req);
    const existing = db.prepare('SELECT id FROM persons WHERE id = ?').get(personId);
    if (!existing) { jsonResponse(res, 404, { error: 'Person not found' }); return true; }
    const score = Math.max(1, Math.min(10, parseInt(body.influence_score) || 5));
    const status = ['champion', 'engaged', 'neutral', 'unaware', 'blocker'].includes(body.engagement_status)
      ? body.engagement_status : 'neutral';
    db.prepare(`UPDATE persons SET influence_score = ?, engagement_status = ?, updated_at = datetime('now') WHERE id = ?`)
      .run(score, status, personId);
    const updated = db.prepare('SELECT * FROM persons WHERE id = ?').get(personId);
    jsonResponse(res, 200, parseRow('persons', updated));
    return true;
  }

  return false;
}
