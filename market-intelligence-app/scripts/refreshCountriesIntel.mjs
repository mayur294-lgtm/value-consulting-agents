#!/usr/bin/env node
/**
 * refreshCountriesIntel.mjs — bulk country intelligence refresh
 * ─────────────────────────────────────────────────────────────
 * Iterates serially over (country, section) pairs and re-runs the country
 * intel agent on each. Serial execution avoids the 120s Claude timeout
 * that hits when refreshing 3+ sections at once.
 *
 * Reports per-section source coverage so we can see at a glance whether
 * the agent's anti-hallucination guardrails are sticking.
 *
 * Usage:
 *   node scripts/refreshCountriesIntel.mjs                     # default: Nordics + 4 sections
 *   node scripts/refreshCountriesIntel.mjs --countries=Sweden,Denmark
 *   node scripts/refreshCountriesIntel.mjs --sections=market_news,fintech_landscape
 *   node scripts/refreshCountriesIntel.mjs --include-prose     # also refresh banking_sector etc.
 *   node scripts/refreshCountriesIntel.mjs --force             # skip staleness check
 */

import dotenv from 'dotenv';
dotenv.config({ override: true, quiet: true });

import { getDb } from './db.mjs';
import { refreshCountryIntelligence, isCountryIntelAvailable } from './fetchers/countryIntelAgent.mjs';

const args = process.argv.slice(2);
const FORCE = args.includes('--force');
const INCLUDE_PROSE = args.includes('--include-prose');
const countriesArg = args.find(a => a.startsWith('--countries='));
const sectionsArg = args.find(a => a.startsWith('--sections='));

const DEFAULT_COUNTRIES = ['Sweden', 'Denmark', 'Norway', 'Finland'];
const STRUCTURED_SECTIONS = ['market_news', 'fintech_landscape', 'regulatory_environment', 'customer_needs'];
const PROSE_SECTIONS = ['banking_sector', 'demographics', 'digital_banking', 'consumer_segments', 'spending_trends', 'backbase_opportunities'];

const countries = countriesArg ? countriesArg.split('=')[1].split(',') : DEFAULT_COUNTRIES;
let sections;
if (sectionsArg) {
  sections = sectionsArg.split('=')[1].split(',');
} else {
  sections = INCLUDE_PROSE ? [...STRUCTURED_SECTIONS, ...PROSE_SECTIONS] : STRUCTURED_SECTIONS;
}

const db = getDb();

function loadCountry(name) {
  const row = db.prepare('SELECT name, data FROM countries WHERE name = ?').get(name);
  if (!row) return null;
  let parsed;
  try { parsed = JSON.parse(row.data); } catch { parsed = {}; }
  return { name: row.name, data: parsed };
}

function persistCountry(name, mergedData) {
  // SQLite treats "now" (double-quoted) as a column name; use single quotes
  // for the string literal.
  db.prepare("UPDATE countries SET data = ?, updated_at = datetime('now') WHERE name = ?")
    .run(JSON.stringify(mergedData), name);
}

function fmtCoverage(cov) {
  if (!cov) return '— ';
  const tone = cov.pct >= 80 ? '✓' : cov.pct >= 40 ? '~' : '✗';
  return `${tone} ${cov.sourced}/${cov.total} (${cov.pct}%)`;
}

async function main() {
  console.log('═'.repeat(70));
  console.log('  Country Intelligence Bulk Refresh');
  console.log('═'.repeat(70));
  console.log(`  Countries: ${countries.join(', ')}`);
  console.log(`  Sections:  ${sections.join(', ')} (${INCLUDE_PROSE ? 'with prose' : 'structured only'})`);
  console.log(`  Force:     ${FORCE}`);

  if (!isCountryIntelAvailable()) {
    console.error('\n✗ ANTHROPIC_API_KEY not configured. Cannot refresh.');
    process.exit(1);
  }

  console.log();
  let totalRefreshed = 0;
  let totalSkipped = 0;
  let totalDropped = 0;
  const start = Date.now();

  for (const countryName of countries) {
    const country = loadCountry(countryName);
    if (!country) {
      console.log(`  ✗ ${countryName}: not found in DB`);
      continue;
    }

    console.log(`  ── ${countryName} ──`);

    for (const section of sections) {
      const sectionStart = Date.now();
      try {
        const { refreshed, skipped, dropped } = await refreshCountryIntelligence(
          countryName, country.data, [section], FORCE
        );
        const elapsed = ((Date.now() - sectionStart) / 1000).toFixed(1);
        if (skipped.includes(section)) {
          console.log(`     ⊙ ${section.padEnd(25)} skipped (fresh)`);
          totalSkipped += 1;
        } else if (refreshed[section]) {
          // Merge into country data + persist
          const merged = { ...country.data, [section]: refreshed[section] };
          persistCountry(countryName, merged);
          country.data = merged; // for next section in same country
          const cov = refreshed[section]._source_coverage;
          const dropCount = dropped?.[section] || 0;
          console.log(`     ✓ ${section.padEnd(25)} ${fmtCoverage(cov)}${dropCount > 0 ? ` · ${dropCount} dropped` : ''} · ${elapsed}s`);
          totalRefreshed += 1;
          totalDropped += dropCount;
        } else {
          console.log(`     ✗ ${section.padEnd(25)} no data returned`);
        }
      } catch (err) {
        console.log(`     ✗ ${section.padEnd(25)} ${err.message?.slice(0, 60)}`);
      }
    }
  }

  const elapsed = ((Date.now() - start) / 1000).toFixed(1);
  console.log();
  console.log('═'.repeat(70));
  console.log(`  Refreshed: ${totalRefreshed}   Skipped (fresh): ${totalSkipped}   Dropped (unsourced): ${totalDropped}`);
  console.log(`  Elapsed:   ${elapsed}s`);
  console.log('═'.repeat(70));
}

main().catch(err => {
  console.error('Bulk refresh error:', err);
  process.exit(1);
});
