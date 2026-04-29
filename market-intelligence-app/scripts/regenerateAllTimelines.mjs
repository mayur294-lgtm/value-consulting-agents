#!/usr/bin/env node
/**
 * regenerateAllTimelines.mjs — bulk Engagement & Execution Timeline gen
 * ────────────────────────────────────────────────────────────────────
 * Iterates every real bank in the portfolio and runs regenerateTimeline().
 * Pure deterministic — no LLM calls — so this is fast and safe to run
 * repeatedly. Per-bank user customizations are preserved (only auto-
 * generated `planned` actions get refreshed).
 *
 * Usage:
 *   node scripts/regenerateAllTimelines.mjs                          # all banks
 *   node scripts/regenerateAllTimelines.mjs --country=Sweden          # filter by country prefix
 *   node scripts/regenerateAllTimelines.mjs --region=nordics          # filter via market.countries[]
 *   node scripts/regenerateAllTimelines.mjs --bank=Nordea             # single bank
 *   node scripts/regenerateAllTimelines.mjs --dry-run                 # preview counts, no DB writes
 *   node scripts/regenerateAllTimelines.mjs --skip-existing           # skip banks that already have any actions
 *   node scripts/regenerateAllTimelines.mjs --min-actions=3           # report banks with < N actions
 */

import dotenv from 'dotenv';
dotenv.config({ override: true, quiet: true });

import { getDb } from './db.mjs';
import { regenerateTimeline, getBankTimeline, generateTimelineActions } from './lib/engagementTimeline.mjs';
import { getBanksForRegion } from './lib/regionAggregator.mjs';

const args = process.argv.slice(2);
const get = (key) => args.find(a => a.startsWith(`--${key}=`))?.split('=')[1];
const has = (key) => args.includes(`--${key}`);

const DRY_RUN = has('dry-run');
const SKIP_EXISTING = has('skip-existing');
const VERBOSE = has('verbose');
const country = get('country');
const region = get('region');
const bankFilter = get('bank');
const minActions = parseInt(get('min-actions') || '0', 10);

const db = getDb();

function loadBanks() {
  // Always exclude synthetic _competitor_* rows (created by competitorTracker)
  let sql = `SELECT key, bank_name, country FROM banks WHERE (country IS NULL OR country != '_competitor')`;
  const params = [];
  if (bankFilter) {
    sql += ` AND (key LIKE ? OR bank_name LIKE ?)`;
    params.push(`%${bankFilter}%`, `%${bankFilter}%`);
  }
  if (country) {
    sql += ` AND (country = ? OR country LIKE ?)`;
    params.push(country, `${country}%`);
  }
  sql += ` ORDER BY country, bank_name`;
  let banks = db.prepare(sql).all(...params);
  if (region) {
    const regionBanks = new Set(getBanksForRegion(db, region).map(b => b.key));
    banks = banks.filter(b => regionBanks.has(b.key));
  }
  return banks;
}

const banks = loadBanks();

console.log('═'.repeat(70));
console.log('  Bulk Timeline Regeneration');
console.log('═'.repeat(70));
console.log(`  Mode:      ${DRY_RUN ? 'DRY-RUN (no DB writes)' : 'WRITE'}`);
console.log(`  Banks:     ${banks.length}${bankFilter ? ` (filter=${bankFilter})` : ''}${country ? ` (country=${country})` : ''}${region ? ` (region=${region})` : ''}`);
console.log(`  Skip existing: ${SKIP_EXISTING}`);
console.log();

if (banks.length === 0) {
  console.log('  No banks matched filters. Done.');
  process.exit(0);
}

const start = Date.now();
const stats = [];
let succeeded = 0;
let skipped = 0;
let failed = 0;
let totalActions = 0;

for (const bank of banks) {
  try {
    if (SKIP_EXISTING && !DRY_RUN) {
      const existing = getBankTimeline(db, bank.key);
      if (existing.length > 0) {
        console.log(`  ⊙ ${bank.bank_name.padEnd(35)} skipped (${existing.length} existing actions)`);
        skipped += 1;
        continue;
      }
    }

    let summary;
    if (DRY_RUN) {
      const preview = generateTimelineActions(db, bank.key);
      summary = preview.summary;
    } else {
      const result = regenerateTimeline(db, bank.key);
      summary = result.summary;
    }

    const total = summary.total_actions;
    const flag = (minActions > 0 && total < minActions) ? ' ⚠ low' : '';
    const cats = summary.by_category;
    const horizons = summary.by_horizon;
    console.log(
      `  ${DRY_RUN ? '⊙' : '✓'} ${bank.bank_name.padEnd(35)} ` +
      `${String(total).padStart(2)} actions  ` +
      `[w:${cats.workshop || 0} s:${cats.stakeholder_outreach || 0} m:${cats.marketing_event || 0} p:${cats.partner_led || 0}]  ` +
      `[60d:${horizons['60d'] || 0} 90d:${horizons['90d'] || 0}]${flag}`
    );

    stats.push({ bank: bank.bank_name, country: bank.country, total, by_category: cats, by_horizon: horizons });
    totalActions += total;
    succeeded += 1;
  } catch (err) {
    console.log(`  ✗ ${bank.bank_name.padEnd(35)} ERROR: ${err.message?.slice(0, 60)}`);
    failed += 1;
  }
}

const elapsed = ((Date.now() - start) / 1000).toFixed(1);
console.log();
console.log('═'.repeat(70));
console.log(`  Generated: ${succeeded}   Skipped: ${skipped}   Failed: ${failed}   Elapsed: ${elapsed}s`);
console.log(`  Total actions: ${totalActions}   Avg per bank: ${succeeded > 0 ? (totalActions / succeeded).toFixed(1) : '—'}`);
console.log('═'.repeat(70));

// Aggregate report
if (succeeded > 0) {
  const byCat = { workshop: 0, stakeholder_outreach: 0, marketing_event: 0, partner_led: 0 };
  const byHorizon = { '60d': 0, '90d': 0 };
  for (const s of stats) {
    Object.entries(s.by_category).forEach(([k, v]) => { byCat[k] = (byCat[k] || 0) + v; });
    Object.entries(s.by_horizon).forEach(([k, v]) => { byHorizon[k] = (byHorizon[k] || 0) + v; });
  }
  console.log();
  console.log('  Portfolio totals:');
  console.log(`    Workshops:               ${byCat.workshop}`);
  console.log(`    Stakeholder reach-out:   ${byCat.stakeholder_outreach}`);
  console.log(`    Marketing & events:      ${byCat.marketing_event}`);
  console.log(`    Partner-led:             ${byCat.partner_led}`);
  console.log(`    Next 60 days:            ${byHorizon['60d'] || 0}`);
  console.log(`    Next 60-90 days:         ${byHorizon['90d'] || 0}`);

  if (minActions > 0) {
    const weak = stats.filter(s => s.total < minActions);
    if (weak.length > 0) {
      console.log();
      console.log(`  ⚠ Banks with < ${minActions} actions (likely thin intel):`);
      weak.forEach(s => console.log(`    · ${s.bank} (${s.country}): ${s.total}`));
    }
  }
}
