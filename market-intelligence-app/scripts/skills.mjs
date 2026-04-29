#!/usr/bin/env node
/**
 * Nova Skills CLI — workflow automation skills (Wave 6)
 * ─────────────────────────────────────────────────────
 * Single CLI dispatcher for many small skills. Each subcommand wraps a lib
 * call + prints structured output. Reduces npm-script noise from N entries
 * to one.
 *
 * Usage:
 *   node scripts/skills.mjs <command> [args]
 *
 * Commands:
 *   refresh-bank --bank=<key>           Full-stack refresh: signals + Pulse + facts + cross-ref
 *   draft-pulse --bank=<key> [period]   Generate Pulse without committing it
 *   audit-pulse --bank=<key> [period]   Lint a Pulse — gaps, stale, low-grade sources
 *   benchmark-bank --bank=<key>         Benchmarks scoped to bank
 *   capability-snapshot --bank=<key>    Quick capability assessment
 *   engagement-status --bank=<key>      Show VC engagement state
 *   intent-score --bank=<key>           Buying intent score
 *   intent-portfolio                    Rank entire portfolio by intent
 *   opportunity-windows --bank=<key>    Multi-stream opportunity windows
 *   opportunity-portfolio               Portfolio-wide windows
 *   compare-banks --banks=A,B,C         Side-by-side comparison
 *   find-similar --bank=<key>           Find similar prior engagements
 *   weekly-digest [--for=ae|vc]         Portfolio digest
 *   vc-watch                            VC-relevant change feed
 *   refresh-competitors                 Refresh competitor signals
 *   find-prospects --country=<name>     New prospects in country
 *   harvest-engagement --id=<id> [--out=folder]  Post-engagement harvest
 *   reg-impact --signal-id=<id>         Map regulation to portfolio impact
 *   smart-schedule                      Smart-prioritized refresh scheduler
 */

import dotenv from 'dotenv';
dotenv.config({ override: true, quiet: true });

import { getDb } from './db.mjs';
import { generatePulseForBank } from './lib/pulseGenerator.mjs';
import { computeBuyingIntent, rankPortfolioByIntent } from './lib/buyingIntentScorer.mjs';
import { detectOpportunityWindows, detectAllPortfolioWindows } from './lib/opportunityWindowDetector.mjs';
import { findSimilarEngagements } from './lib/engagementSimilarityFinder.mjs';
import { generateCapabilitySnapshot } from './lib/capabilitySnapshot.mjs';
import { getBenchmarksForBank } from './lib/benchmarkBridge.mjs';
import { getBankEngagementSummary, listEngagements } from './lib/engagementTracker.mjs';
import { harvestEngagement } from './lib/postEngagementHarvester.mjs';
import { refreshCompetitorSignals } from './lib/competitorTracker.mjs';
import { findProspectsInCountry } from './lib/prospectFinder.mjs';
import { mapRegulationToImpact } from './lib/regulatoryImpactAgent.mjs';
import { getChangeFeed } from './lib/changeFeed.mjs';

const args = process.argv.slice(2);
const cmd = args[0];
const get = (key) => args.find(a => a.startsWith(`--${key}=`))?.split('=')[1];

const db = getDb();

function header(title) {
  console.log('═'.repeat(70));
  console.log(`  ${title}`);
  console.log('═'.repeat(70));
}

async function main() {
  switch (cmd) {

    case 'refresh-bank': {
      const bank = get('bank');
      if (!bank) return console.error('--bank=<key> required');
      header(`refresh-bank · ${bank}`);
      const period = get('period') || '2026-Q2';
      // Run pulse generation + facts + cross-ref serially
      const pulse = generatePulseForBank(db, bank, period, { generated_by: 'skills' });
      console.log(`  ✓ Pulse generated for ${period} — ${pulse.metrics?.total_source_records || 0} sources`);
      console.log(`  ↪ For meeting facts run: npm run extract-facts`);
      console.log(`  ↪ For patterns run: npm run cross-reference -- --bank=${bank}`);
      break;
    }

    case 'draft-pulse': {
      const bank = get('bank');
      if (!bank) return console.error('--bank=<key> required');
      const period = get('period') || '2026-Q2';
      header(`draft-pulse · ${bank} · ${period}`);
      const pulse = generatePulseForBank(db, bank, period, { generated_by: 'draft', dryRun: true });
      console.log(`  Synthesis preview:`);
      Object.entries(pulse.sections || {}).forEach(([k, s]) => {
        console.log(`    [${k}] ${s.synthesis.slice(0, 100)}…`);
      });
      console.log(`\n  Lint warnings: ${pulse.metrics?.lint_warning_count || 0}`);
      console.log(`  Sources: ${pulse.metrics?.total_source_records}`);
      break;
    }

    case 'audit-pulse': {
      const bank = get('bank');
      if (!bank) return console.error('--bank=<key> required');
      const period = get('period') || '2026-Q2';
      header(`audit-pulse · ${bank} · ${period}`);
      const row = db.prepare(`SELECT payload_json FROM pulses WHERE account_id = ? AND period_id = ?`).get(bank, period);
      if (!row) { console.log('  No pulse found. Run refresh-bank first.'); break; }
      const payload = JSON.parse(row.payload_json);
      let totalLint = 0, sectionsWithLint = 0;
      Object.entries(payload.sections || {}).forEach(([k, s]) => {
        const lint = s._lint || [];
        if (lint.length > 0) {
          sectionsWithLint += 1;
          console.log(`  ${k}: ${lint.length} warning(s)`);
          lint.forEach(w => console.log(`    - ${w.code}: ${w.message}`));
          totalLint += lint.length;
        }
      });
      console.log(`\n  Total: ${totalLint} warnings across ${sectionsWithLint} sections`);
      const grades = {};
      Object.values(payload.sections).forEach(s => {
        (s.source_records || []).forEach(r => { grades[r.source_grade || '_'] = (grades[r.source_grade || '_'] || 0) + 1; });
      });
      console.log(`  Source grade mix: ${JSON.stringify(grades)}`);
      break;
    }

    case 'benchmark-bank': {
      const bank = get('bank');
      if (!bank) return console.error('--bank=<key> required');
      header(`benchmark-bank · ${bank}`);
      const r = getBenchmarksForBank(db, bank);
      console.log(`  Bank: ${r.bank?.name} (${r.bank?.country})`);
      if (r.note) console.log(`  ${r.note}`);
      console.log(`  Benchmarks found: ${r.benchmarks?.length || 0}`);
      (r.benchmarks || []).forEach(b => {
        console.log(`    · ${b.benchmark_name} — ${b.relevant_rows}/${b.total_rows_in_file} relevant rows`);
      });
      break;
    }

    case 'capability-snapshot': {
      const bank = get('bank');
      if (!bank) return console.error('--bank=<key> required');
      header(`capability-snapshot · ${bank}`);
      const snap = generateCapabilitySnapshot(db, bank);
      console.log(`  Bank: ${snap.bank.name}`);
      if (snap.note) console.log(`  ⚠ ${snap.note}`);
      console.log(`\n  Maturity scores (1-5):`);
      snap.dimensions.forEach(d => {
        const bar = d.score != null ? '█'.repeat(Math.round(d.score)) + '░'.repeat(5 - Math.round(d.score)) : '—————';
        console.log(`    ${d.label.padEnd(28)} ${bar} ${d.score ?? '?'} (n=${d.n_facts})`);
      });
      if (snap.biggest_gaps?.length > 0) {
        console.log(`\n  Biggest gaps:`);
        snap.biggest_gaps.forEach(g => console.log(`    ✗ ${g.label} (score ${g.maturity_score})`));
      }
      break;
    }

    case 'engagement-status': {
      const bank = get('bank');
      if (!bank) return console.error('--bank=<key> required');
      header(`engagement-status · ${bank}`);
      const sum = getBankEngagementSummary(db, bank);
      console.log(`  Active engagements: ${sum.active_count}`);
      console.log(`  Closed engagements: ${sum.closed_count}`);
      console.log(`  Artifacts: ${sum.artifact_count}`);
      sum.active_engagements.forEach(e => {
        console.log(`    · [${e.state}] ${e.engagement_type} — ${e.title || ''}`);
      });
      break;
    }

    case 'intent-score': {
      const bank = get('bank');
      if (!bank) return console.error('--bank=<key> required');
      header(`intent-score · ${bank}`);
      const r = computeBuyingIntent(db, bank);
      console.log(`  Total: ${r.score}/100  ·  Tier: ${r.tier.toUpperCase()}`);
      console.log(`  Components:`);
      Object.entries(r.components).forEach(([k, v]) => console.log(`    ${k.padEnd(22)} +${v}`));
      break;
    }

    case 'intent-portfolio': {
      header(`intent-portfolio (top 15)`);
      const ranked = rankPortfolioByIntent(db);
      ranked.slice(0, 15).forEach(b => {
        console.log(`  [${b.score.toString().padStart(3)}/100 ${b.tier.padEnd(8)}] ${b.bank_key}`);
      });
      break;
    }

    case 'opportunity-windows': {
      const bank = get('bank');
      if (!bank) return console.error('--bank=<key> required');
      header(`opportunity-windows · ${bank}`);
      const windows = detectOpportunityWindows(db, bank);
      if (windows.length === 0) { console.log('  No windows detected.'); break; }
      windows.forEach(w => {
        console.log(`  [${w.significance}/10] ${w.type} — ${w.title}`);
        console.log(`    ${w.detail}`);
      });
      break;
    }

    case 'opportunity-portfolio': {
      header(`opportunity-portfolio`);
      const all = detectAllPortfolioWindows(db);
      if (all.length === 0) { console.log('  No windows portfolio-wide.'); break; }
      all.forEach(b => {
        console.log(`  ${b.bank_name}:`);
        b.windows.forEach(w => console.log(`    [${w.significance}/10] ${w.type}`));
      });
      break;
    }

    case 'compare-banks': {
      const banksArg = get('banks');
      if (!banksArg) return console.error('--banks=A,B,C required');
      const banks = banksArg.split(',');
      header(`compare-banks · ${banks.join(' vs ')}`);
      const rows = banks.map(b => {
        const intent = computeBuyingIntent(db, b);
        const eng = getBankEngagementSummary(db, b);
        return {
          bank: b,
          score: intent.score,
          tier: intent.tier,
          active_eng: eng.active_count,
          artifacts: eng.artifact_count,
        };
      });
      console.log(`  Bank                          Intent  Tier      Active eng  Artifacts`);
      rows.forEach(r => {
        console.log(`  ${r.bank.padEnd(28)}  ${String(r.score).padStart(3)}/100 ${r.tier.padEnd(8)}  ${String(r.active_eng).padStart(8)}    ${String(r.artifacts).padStart(8)}`);
      });
      break;
    }

    case 'find-similar': {
      const bank = get('bank');
      if (!bank) return console.error('--bank=<key> required');
      header(`find-similar · ${bank}`);
      const includeOpen = args.includes('--include-open');
      const r = findSimilarEngagements(db, bank, { includeOpen });
      if (r.note) console.log(`  ${r.note}`);
      (r.similar_engagements || []).forEach(e => {
        console.log(`  [sim ${e.similarity_score}] ${e.bank_name} (${e.country}) · ${e.engagement_type} · ${e.outcome || e.state}`);
        console.log(`    Reasons: ${e.similarity_reasons.join(', ')}`);
      });
      break;
    }

    case 'weekly-digest': {
      const persona = get('for') || 'ae';
      header(`weekly-digest · for ${persona.toUpperCase()}`);
      const events = getChangeFeed(db, { lookbackDays: 7, sort: 'significance', minSignificance: 5, limit: 20 });
      console.log(`  Top ${events.length} events this week:`);
      const filter = persona === 'vc'
        ? (e) => ['NEW_PATTERN', 'NEW_MEETING_FACT', 'STAKEHOLDER_DRIFT'].includes(e.type) || /regulatory|capability|engagement/i.test(e.headline || '')
        : () => true;
      events.filter(filter).forEach(e => {
        console.log(`  [${e.significance}/10] ${e.bank_key.padEnd(30)} ${e.type.padEnd(20)} | ${(e.headline || '').slice(0, 60)}`);
      });
      break;
    }

    case 'vc-watch': {
      header('vc-watch — VC-relevant changes (last 7d)');
      const events = getChangeFeed(db, { lookbackDays: 7, sort: 'significance', minSignificance: 4, limit: 50 });
      const vcRelevant = events.filter(e =>
        ['NEW_PATTERN', 'NEW_MEETING_FACT', 'STAKEHOLDER_DRIFT'].includes(e.type) ||
        /regulatory|capability|engagement|artifact/i.test(e.headline || '')
      );
      vcRelevant.forEach(e => {
        console.log(`  [${e.significance}/10] ${e.bank_key.padEnd(28)} ${e.type.padEnd(20)} | ${(e.headline || '').slice(0, 60)}`);
      });
      console.log(`\n  ${vcRelevant.length}/${events.length} events relevant to VCs`);
      break;
    }

    case 'refresh-competitors': {
      header('refresh-competitors');
      const r = await refreshCompetitorSignals(db);
      console.log(`\n  Total added: ${r.added}  · Skipped duplicates: ${r.skipped_duplicates}`);
      break;
    }

    case 'find-prospects': {
      const country = get('country') || 'Sweden';
      header(`find-prospects · ${country}`);
      const r = await findProspectsInCountry(db, country);
      console.log(`  Searched ${r.articles_searched} articles · ${r.existing_banks} existing banks tracked`);
      console.log(`  Candidates (not yet in Nova):`);
      r.candidates.slice(0, 10).forEach(c => {
        console.log(`    · ${c.candidate_name}  (${c.mentions} mention${c.mentions === 1 ? '' : 's'})`);
        c.sample_articles.slice(0, 1).forEach(a => console.log(`      "${a.title.slice(0, 70)}"`));
      });
      break;
    }

    case 'harvest-engagement': {
      const id = get('id');
      const out = get('out');
      if (!id) return console.error('--id=<engagement_id> required');
      header(`harvest-engagement · ${id}`);
      const r = harvestEngagement(db, id, { writeToFolder: out });
      console.log(`  Duration: ${r.metrics.duration_days || '?'} days · Outcome: ${r.metrics.outcome}`);
      console.log(`  Facts at close: ${r.metrics.facts_at_close} · Patterns: ${r.metrics.patterns_at_close} · Artifacts: ${r.metrics.artifacts_count}`);
      if (r.written_path) console.log(`  ✓ Harvest written to ${r.written_path}`);
      else console.log(`\n${r.harvest_markdown}`);
      break;
    }

    case 'reg-impact': {
      const sigId = get('signal-id');
      if (!sigId) return console.error('--signal-id=<id> required');
      header(`reg-impact · ${sigId}`);
      const sig = db.prepare(`SELECT title, description, deal_id FROM deal_signals WHERE id = ?`).get(sigId);
      if (!sig) return console.error('Signal not found');
      const country = db.prepare(`SELECT country FROM banks WHERE key = ?`).get(sig.deal_id)?.country;
      const r = mapRegulationToImpact(db, { ...sig, country });
      console.log(`  Regulation: ${r.regulation.title}`);
      console.log(`  Tags: ${r.regulation.tags.join(', ')}`);
      console.log(`  Top impacted banks:`);
      r.impacted_banks.slice(0, 8).forEach(b => {
        console.log(`    [${b.impact_score}] ${b.bank_name} (${b.country})`);
        console.log(`      ${b.reasons.join('; ')}`);
      });
      break;
    }

    case 'smart-schedule': {
      header('smart-schedule — prioritized refresh queue');
      // Smart scheduler: priority = staleness × deal value × signal volatility
      const banks = db.prepare(`
        SELECT b.key, b.bank_name,
          (SELECT MAX(detected_at) FROM deal_signals WHERE deal_id = b.key) AS last_signal,
          (SELECT COUNT(*) FROM deal_signals WHERE deal_id = b.key AND detected_at >= datetime('now', '-30 days')) AS recent_30d,
          (SELECT MAX(generated_at) FROM pulses WHERE account_id = b.key) AS last_pulse
        FROM banks b
        WHERE b.country != '_competitor' OR b.country IS NULL
      `).all();
      const now = Date.now();
      const queue = banks.map(b => {
        const lastSig = b.last_signal ? (now - new Date(b.last_signal).getTime()) / 86400000 : 999;
        const lastPulse = b.last_pulse ? (now - new Date(b.last_pulse).getTime()) / 86400000 : 999;
        const intent = computeBuyingIntent(db, b.key);
        const priority = Math.round(
          Math.min(20, lastSig) * 1.0 +     // staleness
          intent.score * 0.3 +              // intent
          Math.min(20, b.recent_30d) * 0.5  // recent activity
        );
        return { ...b, last_sig_days: Math.round(lastSig), last_pulse_days: Math.round(lastPulse), intent_score: intent.score, priority };
      }).sort((a, b) => b.priority - a.priority);
      console.log(`  Top 12 banks to refresh next:`);
      queue.slice(0, 12).forEach(b => {
        console.log(`    [P${String(b.priority).padStart(3)}] ${b.bank_name.padEnd(30)} sig:${b.last_sig_days}d pulse:${b.last_pulse_days}d intent:${b.intent_score}`);
      });
      break;
    }

    default:
      console.log('Available commands:');
      console.log('  refresh-bank · draft-pulse · audit-pulse · benchmark-bank');
      console.log('  capability-snapshot · engagement-status · intent-score · intent-portfolio');
      console.log('  opportunity-windows · opportunity-portfolio · compare-banks · find-similar');
      console.log('  weekly-digest · vc-watch · refresh-competitors · find-prospects');
      console.log('  harvest-engagement · reg-impact · smart-schedule');
      console.log();
      console.log('Run any with: node scripts/skills.mjs <command> [--args]');
      break;
  }
}

main().catch(err => { console.error(err); process.exit(1); });
