#!/usr/bin/env node
/**
 * addOP90d.mjs — extend OP timeline with Q3 (90d) lookahead actions
 * ─────────────────────────────────────────────────────────────────
 * The original 60-day plan implies Q3 follow-throughs ("EY joint approach
 * live for Q3", "August omnichannel session", "Aladdin co-pitch") but
 * doesn't enumerate them. This script adds 6 curated Q3 lookahead actions
 * AND re-runs auto-gen so OP's timeline has both 60d sprint + 90d Q3
 * direction.
 */

import dotenv from 'dotenv';
dotenv.config({ override: true, quiet: true });

import { randomUUID } from 'node:crypto';
import { getDb } from './db.mjs';
import { regenerateTimeline } from './lib/engagementTimeline.mjs';

const BANK_KEY = 'OP Financial Group_Finland';

// Q3 lookahead actions — explicit follow-throughs the 60-day plan implied
const Q3_ACTIONS = [
  {
    horizon: '90d', category: 'stakeholder_outreach', priority: 9,
    title: 'Execute August omnichannel session w/ Tuomas + Matti',
    rationale: 'Pre-scheduled Aug 2026 follow-up. Use AI-demo learnings, raise new questions on omnichannel orchestration. Bring any retail / wealth contact who emerged in the 60d sprint into the room. First Q3 warm meeting already in the diary.',
    owner: 'NT + SC',
    due_date: '2026-08-15',
    evidence: { source_doc: 'OP_Pohjola_60Day_Outreach_Light.html', q3_lookahead: true, derived_from: 'Prep August omnichannel session' },
  },
  {
    horizon: '90d', category: 'partner_led', priority: 9,
    title: 'Execute EY joint approach to retail or wealth stakeholder',
    rationale: 'June-30 gate had EY joint approach AGREED with named contact + access. Q3 is the EXECUTION — co-positioned conversation with one of (a) retail segment head, (b) Hanna Porkka, or (c) a level below. EY is the warm route, Backbase is the platform.',
    owner: 'FV + NT',
    due_date: '2026-07-31',
    evidence: { source_doc: 'OP_Pohjola_60Day_Outreach_Light.html', q3_lookahead: true, derived_from: 'EY joint approach — move to active co-positioning' },
  },
  {
    horizon: '90d', category: 'stakeholder_outreach', priority: 9,
    title: 'Convert June hypothesis call → discovery meeting (retail or wealth)',
    rationale: 'Whichever P&L owner had the June hypothesis call: convert to formal discovery — capability mapping, scoping, and named-stakeholder map. The point of the 60-day sprint is to make Q3 about discovery, not introduction.',
    owner: 'NT',
    due_date: '2026-07-15',
    evidence: { source_doc: 'OP_Pohjola_60Day_Outreach_Light.html', q3_lookahead: true, derived_from: 'Follow up retail segment head + Follow up Hanna Porkka' },
  },
  {
    horizon: '90d', category: 'partner_led', priority: 8,
    title: 'Aladdin co-pitch w/ BlackRock + OP wealth (post-webinar)',
    rationale: 'If the June BlackRock webinar landed warm with Porkka or Sanna Holm: schedule a joint Aladdin × Backbase conversation framing the engagement-layer-on-top-of-investment-intelligence story. Backbase + BlackRock to OP wealth is the single highest-leverage commercial move in this account.',
    owner: 'FV + NT',
    due_date: '2026-07-31',
    evidence: { source_doc: 'OP_Pohjola_60Day_Outreach_Light.html', q3_lookahead: true, derived_from: 'BlackRock wealth webinar' },
  },
  {
    horizon: '90d', category: 'marketing_event', priority: 6,
    title: 'Nordic Fintech Summit — attend with OP contacts',
    rationale: 'Roundtable invites went out Week 4 of the 60d sprint. Q3 execution: attend the summit with whoever responded — Tuomas, Antti, and any retail/wealth contacts. Use the side-meetings + dinner format to deepen newly-warm relationships.',
    owner: 'BB + NT',
    due_date: '2026-08-31',
    evidence: { source_doc: 'OP_Pohjola_60Day_Outreach_Light.html', q3_lookahead: true, derived_from: 'Nordic Fintech Summit invites' },
  },
  {
    horizon: '90d', category: 'stakeholder_outreach', priority: 7,
    title: 'Q3 close-out review w/ Tuomas — landscape + relationship status',
    rationale: 'End-of-Q3 check-in with the warmest contact (Tuomas Lappi). Review: post-AI-demo learnings, status of channel transformation Phase 1, where the technical relationship sits relative to the 2027–2028 application-layer decision. Plant the framing for Q4 conversation.',
    owner: 'NT',
    due_date: '2026-09-30',
    evidence: { source_doc: 'OP_Pohjola_60Day_Outreach_Light.html', q3_lookahead: true, derived_from: 'Implied — Q3 close framing' },
  },
];

const db = getDb();

console.log('═'.repeat(70));
console.log('  OP — extend timeline with Q3 (90d) lookahead');
console.log('═'.repeat(70));

// Step 1: re-run auto-gen so DORA briefing + Finland partner event + workshops come back
console.log('\n  Step 1 — Re-run auto-gen (adds 90d items: DORA, partner Finland event, workshops)');
const autoResult = regenerateTimeline(db, BANK_KEY);
console.log(`    ✓ Auto-gen produced ${autoResult.summary.total_actions} actions`);
console.log(`      by_category: ${JSON.stringify(autoResult.summary.by_category)}`);
console.log(`      by_horizon:  ${JSON.stringify(autoResult.summary.by_horizon)}`);

// Step 2: add curated Q3 lookahead actions (idempotent by title)
console.log('\n  Step 2 — Add 6 curated Q3 lookahead actions');
let inserted = 0; let skipped = 0;
for (const a of Q3_ACTIONS) {
  const existing = db.prepare(
    'SELECT id FROM engagement_timeline_actions WHERE bank_key = ? AND LOWER(title) = LOWER(?)'
  ).get(BANK_KEY, a.title);
  if (existing) { skipped += 1; continue; }
  db.prepare(`
    INSERT INTO engagement_timeline_actions (
      id, bank_key, horizon, category, title, rationale,
      evidence_json, status, is_auto_generated, owner, due_date, priority
    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'planned', 0, ?, ?, ?)
  `).run(
    randomUUID(), BANK_KEY, a.horizon, a.category, a.title, a.rationale,
    JSON.stringify(a.evidence), a.owner, a.due_date, a.priority
  );
  inserted += 1;
}
console.log(`    ✓ Inserted ${inserted}/${Q3_ACTIONS.length}  (skipped ${skipped} dupes)`);

// Final summary
console.log('\n  Final OP timeline distribution:');
const dist = db.prepare(`
  SELECT horizon, category, is_auto_generated AS auto, COUNT(*) c
  FROM engagement_timeline_actions
  WHERE bank_key = ? AND status = 'planned'
  GROUP BY horizon, category, is_auto_generated
  ORDER BY horizon, category, auto
`).all(BANK_KEY);
let total = 0;
dist.forEach(r => {
  total += r.c;
  console.log(`    ${r.horizon}  ·  ${r.category.padEnd(22)}  ·  ${r.auto ? 'auto    ' : 'curated '}  →  ${r.c}`);
});
const horizons = db.prepare(`
  SELECT horizon, COUNT(*) c FROM engagement_timeline_actions
  WHERE bank_key = ? AND status = 'planned' GROUP BY horizon
`).all(BANK_KEY);
console.log(`\n    TOTAL: ${total}  ·  ${horizons.map(h => `${h.horizon}: ${h.c}`).join('  ·  ')}`);
