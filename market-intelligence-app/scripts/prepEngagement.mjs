#!/usr/bin/env node
/**
 * /prep-engagement CLI — VC pre-engagement preparation
 * ────────────────────────────────────────────────────
 * Bundles everything a VC needs before kicking off an engagement:
 *   1. Builds the handoff snapshot (Nova intel)
 *   2. Generates the Markdown brief
 *   3. Optionally creates an engagement folder structure compatible with
 *      the parent value-consulting-agents system
 *
 * Usage:
 *   node scripts/prepEngagement.mjs --bank=Nordea_Sweden --folder=./prep
 */

import dotenv from 'dotenv';
dotenv.config({ override: true, quiet: true });

import { writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { getDb } from './db.mjs';
import { buildHandoffSnapshot, snapshotToMarkdown } from './lib/engagementBridge.mjs';

const args = process.argv.slice(2);
const get = (key) => args.find(a => a.startsWith(`--${key}=`))?.split('=')[1];

const bankKey = get('bank');
const folder = get('folder') || `./engagement-prep/${bankKey}`;
const period = get('period') || '2026-Q2';

if (!bankKey) {
  console.error('Usage: prepEngagement.mjs --bank=<bank_key> [--folder=...] [--period=2026-Q2]');
  process.exit(1);
}

const db = getDb();
const snapshot = buildHandoffSnapshot(db, bankKey, { period });

if (!existsSync(folder)) mkdirSync(folder, { recursive: true });

// Standard engagement folder structure (mirrors VC value-consulting-agents)
mkdirSync(join(folder, 'inputs'), { recursive: true });
mkdirSync(join(folder, 'outputs'), { recursive: true });

writeFileSync(join(folder, 'inputs', '01_handoff_brief.md'), snapshotToMarkdown(snapshot), 'utf8');
writeFileSync(join(folder, 'inputs', '02_nova_snapshot.json'), JSON.stringify(snapshot, null, 2), 'utf8');

const contextMd = `# ENGAGEMENT_CONTEXT

**Bank**: ${snapshot.bank.name}
**Country**: ${snapshot.bank.country}
**Snapshot taken**: ${snapshot.snapshot_at}

## Inputs available
- 01_handoff_brief.md — human-readable AE→VC handoff brief (Nova intel)
- 02_nova_snapshot.json — full structured snapshot (consume into VC agents)

## Suggested next steps
1. Review the handoff brief
2. Run \`/scan-engagement\` (parent VC system) on this folder
3. Run \`/run-pipeline --pipeline=value_assessment\` to start

## Source-traceability note
Every claim in the handoff brief traces to a Nova source record. The snapshot
includes meeting facts (verbatim quotes), patterns (fact_id + signal_id),
signals (with source_grade A/B/C/D), and the latest Pulse with provenance chips.
`;
writeFileSync(join(folder, 'ENGAGEMENT_CONTEXT.md'), contextMd, 'utf8');

console.log('═'.repeat(60));
console.log(`  /prep-engagement · ${bankKey}`);
console.log('═'.repeat(60));
console.log(`  Folder: ${folder}`);
console.log(`  Files:`);
console.log(`    ENGAGEMENT_CONTEXT.md`);
console.log(`    inputs/01_handoff_brief.md`);
console.log(`    inputs/02_nova_snapshot.json`);
console.log();
console.log(`  Snapshot stats:`);
console.log(`    ${snapshot.stakeholders.total} stakeholders`);
console.log(`    ${snapshot.meeting_intel.attributed_fact_count} attributed facts`);
console.log(`    ${snapshot.patterns.total} corroborated patterns`);
console.log(`    ${snapshot.recent_high_grade_signals.length} A/B-grade signals`);
console.log(`    ${snapshot.pulse ? '1 Pulse' : 'no Pulse for this period'}`);
