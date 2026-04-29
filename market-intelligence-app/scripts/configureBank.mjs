#!/usr/bin/env node
/**
 * configureBank.mjs — small CLI for bank-level config + persons
 * ─────────────────────────────────────────────────────────────
 * Two operations:
 *   1. Set timeline_exclusions on banks.data (keywords to filter out of
 *      timeline action generation — e.g. "bancassurance" for OP)
 *   2. Add a person to the persons table with minimal data; AE/VC can
 *      enrich later via PersonIntelCard
 *
 * Usage:
 *   # Set exclusions
 *   node scripts/configureBank.mjs exclude --bank=<key> --keywords=bancassurance,wealth
 *
 *   # Add a person
 *   node scripts/configureBank.mjs add-person --bank=<key> \
 *     --name="Kasimir Loikkanen" --role="Group CIO" --influence=9
 */

import dotenv from 'dotenv';
dotenv.config({ override: true, quiet: true });

import { randomUUID } from 'node:crypto';
import { getDb } from './db.mjs';

const args = process.argv.slice(2);
const cmd = args[0];
const get = (key) => args.find(a => a.startsWith(`--${key}=`))?.split('=')[1];

const db = getDb();

function setExclusions(bankKey, keywords) {
  const row = db.prepare('SELECT data FROM banks WHERE key = ?').get(bankKey);
  if (!row) throw new Error(`Bank not found: ${bankKey}`);
  const data = JSON.parse(row.data || '{}');
  data.timeline_exclusions = keywords;
  db.prepare("UPDATE banks SET data = ?, updated_at = datetime('now') WHERE key = ?")
    .run(JSON.stringify(data), bankKey);
  return data.timeline_exclusions;
}

function addPerson({ bankKey, name, role, influence, engagement, lob, note }) {
  const row = db.prepare('SELECT key FROM banks WHERE key = ?').get(bankKey);
  if (!row) throw new Error(`Bank not found: ${bankKey}`);

  // Idempotent: don't duplicate if a person with the same canonical_name
  // already exists at this bank
  const existing = db.prepare(
    'SELECT id FROM persons WHERE bank_key = ? AND LOWER(canonical_name) = LOWER(?)'
  ).get(bankKey, name);
  if (existing) {
    console.log(`  ⊙ Person already exists (id ${existing.id.slice(0, 8)}…) — skipping insert.`);
    return existing.id;
  }

  const id = randomUUID().replace(/-/g, '').slice(0, 32);
  db.prepare(`
    INSERT INTO persons (
      id, bank_key, canonical_name, role, role_category,
      influence_score, engagement_status, lob, note, discovery_source
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'manual_cli')
  `).run(
    id, bankKey, name, role || null, deriveRoleCategory(role),
    influence != null ? Number(influence) : null,
    engagement || 'unknown',
    lob || null,
    note || null
  );
  return id;
}

function deriveRoleCategory(role) {
  if (!role) return null;
  const lower = role.toLowerCase();
  if (/\b(ceo|cio|cto|cfo|cdo|coo|chro|chair|president|head of|chief|managing director)\b/.test(lower)) return 'executive';
  if (/\b(director|svp|evp|vp)\b/.test(lower)) return 'leadership';
  if (/\b(architect|engineer|product|ops)\b/.test(lower)) return 'practitioner';
  return 'other';
}

switch (cmd) {
  case 'exclude': {
    const bank = get('bank');
    const keywords = (get('keywords') || '').split(',').map(s => s.trim()).filter(Boolean);
    if (!bank || keywords.length === 0) {
      console.error('Usage: configureBank.mjs exclude --bank=<key> --keywords=a,b,c');
      process.exit(1);
    }
    const result = setExclusions(bank, keywords);
    console.log(`✓ ${bank} timeline_exclusions = ${JSON.stringify(result)}`);
    break;
  }
  case 'add-person': {
    const bank = get('bank');
    const name = get('name');
    if (!bank || !name) {
      console.error('Usage: configureBank.mjs add-person --bank=<key> --name="<full name>" [--role="..."] [--influence=N] [--engagement=...] [--lob=...] [--note="..."]');
      process.exit(1);
    }
    const id = addPerson({
      bankKey: bank,
      name,
      role: get('role'),
      influence: get('influence'),
      engagement: get('engagement'),
      lob: get('lob'),
      note: get('note'),
    });
    console.log(`✓ Person ${id.slice(0, 8)}… (${name}) added to ${bank}`);
    break;
  }
  case 'show': {
    const bank = get('bank');
    if (!bank) { console.error('Usage: configureBank.mjs show --bank=<key>'); process.exit(1); }
    const row = db.prepare('SELECT data FROM banks WHERE key = ?').get(bank);
    const data = JSON.parse(row?.data || '{}');
    console.log(`Bank: ${bank}`);
    console.log(`  timeline_exclusions: ${JSON.stringify(data.timeline_exclusions || [])}`);
    const persons = db.prepare('SELECT canonical_name, role, influence_score, engagement_status FROM persons WHERE bank_key = ? ORDER BY influence_score DESC').all(bank);
    console.log(`  Persons: ${persons.length}`);
    persons.forEach(p => console.log(`    · ${p.canonical_name} — ${p.role || '?'} · influence ${p.influence_score || '?'} · ${p.engagement_status || '?'}`));
    break;
  }
  default:
    console.log('Commands: exclude · add-person · show');
    console.log('  exclude --bank=<key> --keywords=a,b');
    console.log('  add-person --bank=<key> --name="<name>" [--role="..." --influence=N --engagement=... --lob=... --note="..."]');
    console.log('  show --bank=<key>');
    break;
}
