#!/usr/bin/env node
/**
 * /handoff CLI — formal AE→VC handoff with intel snapshot
 * ───────────────────────────────────────────────────────
 * Usage:
 *   node scripts/handoffBank.mjs --bank=Nordea_Sweden --type=value_assessment \
 *     --vc=Mariam --ae=Oumaima --out=handoff.md
 *
 * Creates a new engagement record, captures Nova snapshot at this moment,
 * persists to DB, and writes a Markdown brief to stdout (or file via --out).
 */

import dotenv from 'dotenv';
dotenv.config({ override: true, quiet: true });

import { writeFileSync } from 'node:fs';
import { getDb } from './db.mjs';
import { buildHandoffSnapshot, snapshotToMarkdown } from './lib/engagementBridge.mjs';
import { createEngagement } from './lib/engagementTracker.mjs';

const args = process.argv.slice(2);
const get = (key) => args.find(a => a.startsWith(`--${key}=`))?.split('=')[1];
const has = (key) => args.includes(`--${key}`);

const bankKey = get('bank');
const engagementType = get('type') || 'value_assessment';
const vcLead = get('vc');
const aeLead = get('ae');
const title = get('title');
const period = get('period') || '2026-Q2';
const outFile = get('out');
const dryRun = has('dry-run');

if (!bankKey) {
  console.error('Usage: handoffBank.mjs --bank=<bank_key> [--type=...] [--vc=...] [--ae=...] [--title=...] [--out=file.md] [--dry-run]');
  process.exit(1);
}

const db = getDb();

console.log('═'.repeat(60));
console.log(`  AE→VC Handoff · ${bankKey}`);
console.log('═'.repeat(60));
console.log(`  Type: ${engagementType}   VC: ${vcLead || '(unset)'}   AE: ${aeLead || '(unset)'}`);
console.log(`  Period for Pulse: ${period}`);
console.log(`  Mode: ${dryRun ? 'DRY-RUN (no DB write)' : 'WRITE'}`);
console.log();

const snapshot = buildHandoffSnapshot(db, bankKey, { period });
console.log(`  ✓ Snapshot built — ${snapshot.stakeholders.total} stakeholders · ${snapshot.meeting_intel.attributed_fact_count} attributed facts · ${snapshot.patterns.total} patterns · ${snapshot.recent_high_grade_signals.length} A/B signals`);

if (!dryRun) {
  const engagement = createEngagement(db, {
    bank_key: bankKey,
    engagement_type: engagementType,
    title: title || `${snapshot.bank.name} — ${engagementType}`,
    ae_lead: aeLead,
    vc_lead: vcLead,
    kickoff_date: new Date().toISOString().slice(0, 10),
    handoff_snapshot: snapshot,
  });
  console.log(`  ✓ Engagement created — id ${engagement.id} · state ${engagement.state}`);
}

const md = snapshotToMarkdown(snapshot);
if (outFile) {
  writeFileSync(outFile, md, 'utf8');
  console.log(`  ✓ Brief written to ${outFile} (${md.length} chars)`);
} else {
  console.log();
  console.log('─── HANDOFF BRIEF (Markdown) ───');
  console.log(md);
}
