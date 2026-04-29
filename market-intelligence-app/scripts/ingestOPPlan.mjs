#!/usr/bin/env node
/**
 * ingestOPPlan.mjs — ingest the curated 60-Day OP Pohjola Outreach plan
 * ─────────────────────────────────────────────────────────────────────
 * One-shot ingestion of the Sandy/Backbase 60-day execution plan
 * (OP_Pohjola_60Day_Outreach_Light.html) into Nova:
 *
 *   1. Add stakeholders mentioned in the plan that aren't yet in persons
 *      (idempotent — skips if canonical_name already exists)
 *   2. Pin a bank_note referencing the source plan
 *   3. Clear OP's prior auto-generated planned actions
 *   4. Insert 25 curated timeline actions (is_auto_generated=0) with
 *      proper owners, due dates, categories, and rationale
 *
 * Run once. Re-running is safe — the people add is idempotent and the
 * timeline insert dedups by title.
 *
 * Usage:
 *   node scripts/ingestOPPlan.mjs
 */

import dotenv from 'dotenv';
dotenv.config({ override: true, quiet: true });

import { randomUUID } from 'node:crypto';
import { getDb } from './db.mjs';

const BANK_KEY = 'OP Financial Group_Finland';
const SPRINT_START = '2026-05-01';

// Convert "Week N" → ISO due date (sprint anchored May 1)
const weekToDate = (n) => {
  const d = new Date(SPRINT_START);
  d.setDate(d.getDate() + n * 7 - 1); // end-of-week
  return d.toISOString().slice(0, 10);
};
const DAY1     = '2026-05-01';
const W1_END   = weekToDate(1);   // May 7
const W2_END   = weekToDate(2);   // May 14
const W3_END   = weekToDate(3);   // May 21
const W4_END   = weekToDate(4);   // May 28
const JUN_15   = '2026-06-15';    // mid-June (Weeks 5-7)
const JUN_21   = '2026-06-21';
const JUN_30   = '2026-06-30';

// ──────────────────────────────────────────────────────────────────────
// Stakeholders to add (idempotent — skip if already exists)
// ──────────────────────────────────────────────────────────────────────
const PEOPLE_TO_ADD = [
  {
    name: 'Tuomas Lappi',
    role: 'Head of Digital Channels',
    influence: 8,
    engagement: 'engaged',
    lob: 'Digital Channels',
    note: 'Warmest relationship at OP. AI demo target. Source: 60-day outreach plan May–Jun 2026.',
  },
  {
    name: 'Antti Kurtelius',
    role: 'Channel Technology Tribe Lead',
    influence: 7,
    engagement: 'engaged',
    lob: 'Digital Channels — Technology',
    note: 'Most technically engaged contact. Demo focus: memory mgmt in large projects, agentic SDLC, SDK + AI integration. Source: 60-day plan.',
  },
  {
    name: 'Sanna Holm',
    role: 'Wealth Management — Digital / Operational Lead',
    influence: 6,
    engagement: 'unknown',
    lob: 'Wealth Management',
    note: 'Operational entry point to Hanna Porkka if direct route to Porkka stalls. Source: 60-day plan.',
  },
  {
    name: 'Matti Mikkonen',
    role: 'Omnichannel Lead',
    influence: 6,
    engagement: 'engaged',
    lob: 'Digital Channels — Omnichannel',
    note: 'Joint omnichannel session scheduled August 2026 with Tuomas. Source: 60-day plan.',
  },
  {
    name: 'OP Retail Segment Head (TBD)',
    role: 'Retail Segment Head — P&L Owner',
    influence: 9,
    engagement: 'unknown',
    lob: 'Retail Banking',
    note: 'PRIORITY: name to be identified by May 8. -31% retail operating profit, 450 positions restructured, Nordea offensive. Burning-platform target. Source: 60-day plan.',
  },
];

// ──────────────────────────────────────────────────────────────────────
// 25 curated timeline actions from the source plan
// ──────────────────────────────────────────────────────────────────────
const ACTIONS = [
  // ─── WEEKS 1–2 · Research & Arm ───
  {
    week: 'Day 1', owner: 'OA', due: DAY1, priority: 10, category: 'stakeholder_outreach', horizon: '60d',
    title: 'Identify Retail Banking segment head',
    rationale: 'OP Pohjola post-Oct 2025 rebrand, restructuring press release (450 positions), LinkedIn. Find name, title, direct email or LinkedIn. Every downstream move depends on it.',
  },
  {
    week: 'W1', owner: 'OA', due: W1_END, priority: 9, category: 'stakeholder_outreach', horizon: '60d',
    title: 'Map Hanna Porkka\'s team — find Sanna Holm',
    rationale: 'LinkedIn deep-dive into Wealth Management org. Identify Sanna Holm + any digital experience lead below Porkka. Confirm whether BlackRock Aladdin has reached OP Wealth — determines the entry angle.',
  },
  {
    week: 'W1', owner: 'OA', due: W1_END, priority: 10, category: 'stakeholder_outreach', horizon: '60d',
    title: 'Write the commercial hypothesis one-pager',
    rationale: 'NII compression · Nordea threat · retail profit −31% · wealth growth mandate w/ flat fees · the central question. Short, sharp, no product. Every team member uses it in every outreach. Must exist before the first message.',
  },
  {
    week: 'W1', owner: 'FV', due: W1_END, priority: 9, category: 'partner_led', horizon: '60d',
    title: 'Contact EY Finland — identify the right partner',
    rationale: 'Who at EY Finland has active OP Pohjola relationships? Who advises on their digital transformation / Simplicity Programme equivalent? Find the name. Frederico checks EY partnership roster + reaches directly.',
  },
  {
    week: 'W2', owner: 'FV', due: W2_END, priority: 8, category: 'partner_led', horizon: '60d',
    title: 'BlackRock Aladdin — confirm global rollout status at OP',
    rationale: 'Aladdin live in Switzerland — global rollout TBD. Determines whether Backbase entry is "complement to what you have" vs "platform you need before Aladdin can scale." Confirm via BlackRock partner team.',
  },
  {
    week: 'W2', owner: 'NT + SC + OA', due: W2_END, priority: 9, category: 'stakeholder_outreach', horizon: '60d',
    title: 'Brief Backbase AI experts for the Tuomas/Antti demo',
    rationale: 'Share Mar 2026 transcript sections — Antti\'s Qs on memory mgmt in large software projects, agentic SDLC roles, forward-deployed engineer model. Experts must know exactly what to prepare. Review session plan with Sam before final.',
  },
  {
    week: 'W2', owner: 'NT', due: W2_END, priority: 7, category: 'marketing_event', horizon: '60d',
    title: 'Brief Lars — ABM targets and content direction',
    rationale: '2 named targets: retail segment head (identified by Week 2) + Hanna Porkka. Content anchored in commercial hypothesis (NII compression / Nordea / personalization gap) — not product features. LinkedIn sequences + event invites ready for Week 3.',
  },

  // ─── WEEKS 3–4 · First Reach-Outs ───
  {
    week: 'W3', owner: 'NT', due: W3_END, priority: 10, category: 'stakeholder_outreach', horizon: '60d',
    title: 'First reach-out to Retail segment head',
    rationale: 'LinkedIn connection + short message anchored in commercial hypothesis. Do NOT pitch. 1 sentence on NII compression context, 1 on Nordea, 1 question. If no response in 5 days, find a warm route via EY / Accenture instead of cold follow-up.',
  },
  {
    week: 'W3', owner: 'NT', due: W3_END, priority: 10, category: 'stakeholder_outreach', horizon: '60d',
    title: 'First reach-out to Hanna Porkka',
    rationale: 'LinkedIn message anchored in wealth growth mandate — "seeking significant growth in savings & investment, and we\'ve been thinking about what the digital delivery mechanism looks like for that ambition." 1 question, not a pitch. 30-second read.',
  },
  {
    week: 'W3', owner: 'FV', due: W3_END, priority: 9, category: 'partner_led', horizon: '60d',
    title: 'EY Finland alignment call',
    rationale: 'First call w/ EY Finland partner. Agenda: understand OP relationship depth · propose joint positioning conversation · gauge appetite for co-approach to retail or wealth stakeholders. Frederico leads — partner development conversation, not a pitch.',
  },
  {
    week: 'W3', owner: 'NT + SC', due: W3_END, priority: 9, category: 'stakeholder_outreach', horizon: '60d',
    title: 'Confirm AI demo date with Tuomas + Antti',
    rationale: 'Demo must happen in June — confirm specific date in Week 3. Frame agenda: hands-on, developer-perspective, agentic SDLC + memory mgmt. No slides. No corporate overview. 60 minutes max.',
  },
  {
    week: 'W4', owner: 'FV + NT', due: W4_END, priority: 8, category: 'partner_led', horizon: '60d',
    title: 'BlackRock wealth webinar — confirm or schedule',
    rationale: 'Confirm format + timing. Co-hosted? Co-attended? Joint customer conversation? Lock format and invite OP wealth contacts (Porkka or Sanna Holm). First warm-touch for wealth stakeholders who may not respond to cold LinkedIn.',
  },
  {
    week: 'W4', owner: 'FV', due: W4_END, priority: 7, category: 'partner_led', horizon: '60d',
    title: 'Accenture — check OP relationship scope',
    rationale: 'Accenture inside OP on Pohjola Insurance (Guidewire). Is there a banking-channel team beyond insurance? Who at Accenture Finland could bridge to retail/wealth? Frederico checks Backbase partner roster.',
  },
  {
    week: 'W4', owner: 'BB + NT', due: W4_END, priority: 6, category: 'marketing_event', horizon: '60d',
    title: 'Nordic Fintech Summit invites — send to OP contacts',
    rationale: 'Roundtable invitations to Tuomas, Antti, and any new contacts identified Weeks 1–3. Lars executes. Frame as peer thought leadership forum. If Porkka or retail head responded positively in Week 3, extend invitation to them too.',
  },

  // ─── WEEKS 5–7 · Conversations ───
  {
    week: 'June', owner: 'NT + SC + OA', due: JUN_15, priority: 10, category: 'stakeholder_outreach', horizon: '60d',
    title: 'Deliver AI demo — Tuomas + Antti',
    rationale: 'Critical session. Agentic SDLC (BA/QA agents) · memory mgmt in large projects · forward-deployed engineers reviewing not writing · SDK + docs AI integration. No slides, real dev environment if possible. End w/ planted Q: "What would similar capability mean for your Phase 1 migration timeline?"',
  },
  {
    week: 'June', owner: 'NT', due: JUN_15, priority: 10, category: 'stakeholder_outreach', horizon: '60d',
    title: 'Follow up retail segment head — hypothesis call',
    rationale: 'If Week 3 message acknowledged: 20-min hypothesis call. Goal: 1 question — "What does NII compression + Nordea pressure mean for your digital investment priorities this year?" Listen. Do not pitch. If no Week 3 response, escalate to EY/Accenture or try different contact.',
  },
  {
    week: 'June', owner: 'NT', due: JUN_15, priority: 10, category: 'stakeholder_outreach', horizon: '60d',
    title: 'Follow up Hanna Porkka — schedule hypothesis meeting',
    rationale: 'If Week 3 LinkedIn acknowledged: propose 20-min call — "We\'ve been thinking about what the digital delivery mechanism looks like for OP\'s wealth growth ambition and I\'d value your perspective." If no response, try Sanna Holm — operational relationship that leads to Porkka.',
  },
  {
    week: 'June', owner: 'FV + NT', due: JUN_21, priority: 9, category: 'partner_led', horizon: '60d',
    title: 'EY joint approach — move to active co-positioning',
    rationale: 'Based on Week 3 EY alignment call: agree on joint approach to specific OP stakeholder, OR identify next milestone before EY can co-introduce Backbase. Q3 goal "EY joint approach live" must be prepped before end of June or Q3 starts from scratch.',
  },
  {
    week: 'June', owner: 'OA + SC', due: JUN_15, priority: 8, category: 'stakeholder_outreach', horizon: '60d',
    title: 'Post-demo: debrief, TCO seed, document learnings',
    rationale: 'Immediately after Tuomas/Antti demo: document what landed, new questions surfaced, who they mentioned to speak to. Plant TCO Q: "We\'ve been helping banks model cost of building/owning the horizontal service layer vs adopting it — happy to share the framework if useful." Record reaction. Update stakeholder map.',
  },
  {
    week: 'June', owner: 'FV', due: JUN_15, priority: 7, category: 'partner_led', horizon: '60d',
    title: 'MSFT first catch-up via Andy Oliff',
    rationale: 'First Microsoft check-in. Agenda: where is OP in Phase 1 cloud migration? Which MSFT teams engaged? Backbase-on-Azure co-sell or reference architecture as warm route to OP cloud-migration team — different door to Antti + tech tribe vs existing channel relationship.',
  },

  // ─── WEEKS 8–9 · Close the Loop ───
  {
    week: 'W8-9', owner: 'NT + OA', due: JUN_30, priority: 10, category: 'stakeholder_outreach', horizon: '60d',
    title: '60-day status assessment — deal or conversation? (gate)',
    rationale: 'Formal internal review. Per stakeholder: responded / met / warm / cold / not reached. Retail + wealth: have we had a hypothesis conversation? Partners: which are active? Binary Q: have we moved from "live conversation" to "live deal" for any part of the account? Update Salesforce. Define Q3.',
  },
  {
    week: 'W8-9', owner: 'NT', due: JUN_30, priority: 9, category: 'stakeholder_outreach', horizon: '60d',
    title: 'Re-engage non-responders via alternate route',
    rationale: 'Retail head not responding to LinkedIn? Try Accenture/EY route. Porkka not responding? Approach Sanna Holm. No route at all? Escalate to Jouk for executive reach-out. Rule: NO stakeholder leaves the 60-day sprint unreached without alternate route attempted.',
  },
  {
    week: 'W8-9', owner: 'OA', due: JUN_30, priority: 7, category: 'stakeholder_outreach', horizon: '60d',
    title: 'Update account plan + stakeholder map (Q3 brief)',
    rationale: 'Refresh w/ 60-day learnings: new contacts, updated relationship status, confirmed/eliminated partner routes, Aladdin status, retail+wealth conversation outcomes. Becomes the brief for Q3 execution — what we now know, what remains unknown, where commercial conversations are.',
  },
  {
    week: 'W8-9', owner: 'NT', due: JUN_30, priority: 8, category: 'stakeholder_outreach', horizon: '60d',
    title: 'Prep August omnichannel session with Tuomas + Matti',
    rationale: 'Scheduled Aug omnichannel follow-up w/ Tuomas + Matti Mikkonen. Prepare agenda now: AI-demo learnings, new questions to raise. If retail/wealth contacts emerged, explore including or following up from August session. Q3 starts w/ a warm meeting in the diary.',
  },
  {
    week: 'W8-9', owner: 'FV', due: JUN_30, priority: 9, category: 'partner_led', horizon: '60d',
    title: 'Partner status: which route is live for Q3? (gate)',
    rationale: 'Review all 4 partner conversations: EY · BlackRock · Accenture · MSFT. Per partner: active joint approach? named contact w/ OP access? specific next milestone? At least 1 must be live and progressing into Q3, or only route to new OP stakeholders is cold outreach — slowest + least effective for a Finnish cooperative.',
  },
];

// ──────────────────────────────────────────────────────────────────────
// Execution
// ──────────────────────────────────────────────────────────────────────

const db = getDb();

function deriveRoleCategory(role) {
  if (!role) return null;
  const lower = role.toLowerCase();
  if (/\b(ceo|cio|cto|cfo|cdo|coo|chro|chair|president|head of|chief|managing director)\b/.test(lower)) return 'executive';
  if (/\b(director|svp|evp|vp|tribe lead)\b/.test(lower)) return 'leadership';
  if (/\b(architect|engineer|product|ops|operational)\b/.test(lower)) return 'practitioner';
  return 'other';
}

console.log('═'.repeat(70));
console.log('  Ingest OP Pohjola 60-Day Outreach Plan');
console.log('═'.repeat(70));

// Step 1: Add stakeholders (idempotent)
console.log('\n  Step 1 — Add stakeholders (idempotent)');
let peopleAdded = 0;
for (const p of PEOPLE_TO_ADD) {
  const existing = db.prepare(
    'SELECT id FROM persons WHERE bank_key = ? AND LOWER(canonical_name) = LOWER(?)'
  ).get(BANK_KEY, p.name);
  if (existing) {
    console.log(`    ⊙ ${p.name} — already exists, skipping`);
    continue;
  }
  const id = randomUUID().replace(/-/g, '').slice(0, 32);
  db.prepare(`
    INSERT INTO persons (
      id, bank_key, canonical_name, role, role_category,
      influence_score, engagement_status, lob, note, discovery_source
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'op_60day_plan_ingest')
  `).run(
    id, BANK_KEY, p.name, p.role, deriveRoleCategory(p.role),
    p.influence, p.engagement, p.lob, p.note
  );
  peopleAdded += 1;
  console.log(`    ✓ ${p.name} — ${p.role} · influence ${p.influence}`);
}
console.log(`  Added ${peopleAdded}/${PEOPLE_TO_ADD.length}`);

// Step 2: Pin a bank note
console.log('\n  Step 2 — Pin source bank note');
const noteBody = `60-Day Outreach Plan ingested (May–June 2026).
Sprint anchored on May 1, 2026. End-of-sprint gate: June 30, 2026.

Source artifact: OP_Pohjola_60Day_Outreach_Light.html

Key commercial context:
  • OP retail operating profit −31%; 450 positions restructured (Oct 2025 rebrand)
  • Nordea published 2026–2030 strategy as direct competitive threat
  • Wealth Management public growth mandate (Hanna Porkka acting CEO)
  • BlackRock Aladdin Wealth deployed in Switzerland; global rollout TBD
  • Phase 1 cloud migration → Microsoft Azure (Andy Oliff = MSFT contact)
  • Pohjola Insurance modernization → Accenture (Guidewire)
  • August 2026 follow-up session scheduled with Tuomas Lappi + Matti Mikkonen

25 curated timeline actions and 5 stakeholders ingested. Auto-generated
suggestions remain available alongside via Regenerate.`;

const existingNote = db.prepare(
  `SELECT id FROM bank_notes WHERE bank_key = ? AND author_role = 'system' AND body LIKE '60-Day Outreach Plan ingested%'`
).get(BANK_KEY);
if (existingNote) {
  db.prepare(`UPDATE bank_notes SET body = ?, updated_at = datetime('now'), pinned = 1 WHERE id = ?`)
    .run(noteBody, existingNote.id);
  console.log(`    ⊙ Existing note updated (id ${existingNote.id.slice(0, 8)}…)`);
} else {
  const noteId = randomUUID();
  db.prepare(`
    INSERT INTO bank_notes (id, bank_key, author, author_role, body, pinned)
    VALUES (?, ?, 'OP 60-Day Plan ingest', 'system', ?, 1)
  `).run(noteId, BANK_KEY, noteBody);
  console.log(`    ✓ Pinned note created (id ${noteId.slice(0, 8)}…)`);
}

// Step 3: Clear OP's prior auto-generated planned actions
console.log('\n  Step 3 — Clear OP\'s auto-generated planned actions');
const removed = db.prepare(`
  DELETE FROM engagement_timeline_actions
  WHERE bank_key = ? AND is_auto_generated = 1 AND status = 'planned'
`).run(BANK_KEY);
console.log(`    ✓ Removed ${removed.changes} auto-generated planned actions`);

// Step 4: Insert curated actions (dedup by title)
console.log('\n  Step 4 — Insert 25 curated timeline actions');
let inserted = 0; let skipped = 0;
for (const a of ACTIONS) {
  const existing = db.prepare(
    'SELECT id FROM engagement_timeline_actions WHERE bank_key = ? AND LOWER(title) = LOWER(?)'
  ).get(BANK_KEY, a.title);
  if (existing) {
    skipped += 1;
    continue;
  }
  const evidence = {
    source_doc: 'OP_Pohjola_60Day_Outreach_Light.html',
    week_label: a.week,
    owner_codes: a.owner,
  };
  db.prepare(`
    INSERT INTO engagement_timeline_actions (
      id, bank_key, horizon, category, title, rationale,
      evidence_json, status, is_auto_generated, owner, due_date, priority
    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'planned', 0, ?, ?, ?)
  `).run(
    randomUUID(), BANK_KEY, a.horizon, a.category, a.title, a.rationale,
    JSON.stringify(evidence), a.owner, a.due, a.priority
  );
  inserted += 1;
}
console.log(`    ✓ Inserted ${inserted}/${ACTIONS.length}  (skipped ${skipped} duplicates)`);

console.log('\n' + '═'.repeat(70));
console.log('  Done.');
console.log('═'.repeat(70));

// Summary
const final = db.prepare(`
  SELECT category, horizon, COUNT(*) c FROM engagement_timeline_actions
  WHERE bank_key = ? AND status = 'planned'
  GROUP BY category, horizon ORDER BY category, horizon
`).all(BANK_KEY);
console.log('\n  OP timeline now contains (planned actions):');
final.forEach(r => console.log(`    ${r.category.padEnd(22)} ${r.horizon}  →  ${r.c}`));
const totalPlanned = db.prepare(`SELECT COUNT(*) c FROM engagement_timeline_actions WHERE bank_key = ? AND status = 'planned'`).get(BANK_KEY).c;
console.log(`    Total planned: ${totalPlanned}`);
