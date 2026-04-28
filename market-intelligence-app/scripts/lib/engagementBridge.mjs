/**
 * Engagement Bridge — AE→VC handoff snapshot generator
 * ────────────────────────────────────────────────────
 * When AE formally hands off a bank to a VC for an engagement, this library
 * produces a structured intel snapshot that:
 *   1. Captures Nova's current understanding (signals, facts, patterns,
 *      drift, Pulse, country intel) at the moment of handoff
 *   2. Persists into the engagement record (engagements.handoff_snapshot_json)
 *   3. Optionally writes a Markdown summary file to disk for the VC
 *      consultant to ingest into their consulting agents
 *
 * The snapshot is the contract between Nova and the VC engagement system.
 * VCs no longer have to "go look at Nova" — they get a curated brief.
 */

import { getDb } from '../db.mjs';
import { getPatternsForBank } from './crossReferenceEngine.mjs';
import { getStakeholderDrift } from './stakeholderDrift.mjs';
import { generatePulseForBank } from './pulseGenerator.mjs';
import { getBankEngagementSummary } from './engagementTracker.mjs';

/**
 * Build a comprehensive handoff snapshot for a bank.
 * Pure read — no side effects, returns the snapshot object.
 */
export function buildHandoffSnapshot(db, bankKey, options = {}) {
  const { includePulse = true, period = '2026-Q2' } = options;

  // Bank profile core
  const bank = db.prepare('SELECT * FROM banks WHERE key = ?').get(bankKey);
  if (!bank) throw new Error(`Bank not found: ${bankKey}`);
  const bankData = JSON.parse(bank.data || '{}');

  // Qualification + competition
  const qual = db.prepare('SELECT data FROM qualification WHERE bank_key = ?').get(bankKey);
  const comp = db.prepare('SELECT data FROM competition WHERE bank_key = ?').get(bankKey);
  const cx = db.prepare('SELECT data FROM cx WHERE bank_key = ?').get(bankKey);

  // Persons (top 10 by influence)
  const persons = db.prepare(`
    SELECT canonical_name, role, role_category, influence_score, engagement_status, lob, note
    FROM persons WHERE bank_key = ?
    ORDER BY influence_score DESC LIMIT 15
  `).all(bankKey);

  // Recent meeting facts (T1 attributed only — high-quality intel for VC)
  const facts = db.prepare(`
    SELECT mf.speaker_name, mf.topic, mf.position, mf.sentiment, mf.evidence_quote,
           mf.meeting_date, mf.confidence_tier, p.role
    FROM meeting_facts mf
    LEFT JOIN persons p ON p.id = mf.speaker_person_id
    WHERE mf.bank_key = ? AND mf.confidence_tier = 1
    ORDER BY mf.meeting_date DESC LIMIT 20
  `).all(bankKey);

  // Stakeholder drift summary
  const drift = getStakeholderDrift(db, bankKey, { includeUnattributed: false });

  // Top corroborated patterns (medium+ confidence)
  const patterns = getPatternsForBank(db, bankKey, { minConfidence: 'medium' }).slice(0, 10);

  // Recent high-grade signals
  const signals = db.prepare(`
    SELECT signal_category, title, source_url, source_grade, publisher_name,
           detected_at, severity, evidence_quote
    FROM deal_signals
    WHERE deal_id = ? AND COALESCE(is_demo, 0) = 0
      AND source_grade IN ('A', 'B')
    ORDER BY detected_at DESC LIMIT 15
  `).all(bankKey);

  // Latest Pulse (if available + requested)
  let pulse = null;
  if (includePulse) {
    try {
      const row = db.prepare(`
        SELECT payload_json FROM pulses
        WHERE account_id = ? AND period_id = ?
      `).get(bankKey, period);
      if (row) pulse = JSON.parse(row.payload_json);
    } catch { /* swallow */ }
  }

  // Engagement state
  const engagement = getBankEngagementSummary(db, bankKey);

  return {
    snapshot_at: new Date().toISOString(),
    bank: {
      key: bankKey,
      name: bank.bank_name,
      country: bank.country,
      tagline: bankData.tagline,
      operational_profile: bankData.operational_profile || null,
      backbase_qualification: bankData.backbase_qualification || null,
    },
    qualification: qual ? JSON.parse(qual.data) : null,
    competition: comp ? JSON.parse(comp.data) : null,
    cx: cx ? JSON.parse(cx.data) : null,
    stakeholders: {
      total: persons.length,
      top: persons.slice(0, 10),
    },
    meeting_intel: {
      attributed_fact_count: facts.length,
      facts,
      drift_summary: {
        total_cells: drift.length,
        improving: drift.filter(c => c.trend === 'improving').length,
        deteriorating: drift.filter(c => c.trend === 'deteriorating').length,
        mixed: drift.filter(c => c.trend === 'mixed').length,
        stable: drift.filter(c => c.trend === 'stable').length,
        cells: drift.slice(0, 10),
      },
    },
    patterns: {
      total: patterns.length,
      top: patterns,
    },
    recent_high_grade_signals: signals,
    pulse_period: period,
    pulse,
    existing_engagements: engagement,
  };
}

/**
 * Render a handoff snapshot as a Markdown brief for the VC consultant.
 * This is the deliverable that gets attached to the engagement folder.
 */
export function snapshotToMarkdown(snap) {
  const lines = [];
  lines.push(`# AE→VC Handoff Brief — ${snap.bank.name}`);
  lines.push('');
  lines.push(`**Country**: ${snap.bank.country}`);
  lines.push(`**Snapshot taken**: ${snap.snapshot_at}`);
  lines.push(`**Tagline**: ${snap.bank.tagline || '—'}`);
  lines.push('');

  if (snap.qualification?.score != null) {
    lines.push(`**Qualification score**: ${snap.qualification.score}/10`);
  }
  if (snap.bank.backbase_qualification) {
    const q = snap.bank.backbase_qualification;
    lines.push(`**Deal size**: ${q.deal_size || '—'} · **Timing**: ${q.timing || '—'}`);
  }
  lines.push('');

  lines.push('## Top Stakeholders');
  if (snap.stakeholders.top.length === 0) {
    lines.push('_No stakeholders on file._');
  } else {
    snap.stakeholders.top.forEach(p => {
      lines.push(`- **${p.canonical_name}** — ${p.role || 'role unknown'} · influence ${p.influence_score || '—'} · ${p.engagement_status || 'unknown engagement'}`);
    });
  }
  lines.push('');

  lines.push('## Meeting Intelligence');
  lines.push(`- ${snap.meeting_intel.attributed_fact_count} attributed facts (T1) on file`);
  lines.push(`- Drift: ${snap.meeting_intel.drift_summary.improving} improving · ${snap.meeting_intel.drift_summary.deteriorating} deteriorating · ${snap.meeting_intel.drift_summary.mixed} mixed`);
  lines.push('');
  if (snap.meeting_intel.facts.length > 0) {
    lines.push('### Recent attributed facts');
    snap.meeting_intel.facts.slice(0, 8).forEach(f => {
      lines.push(`- **${f.speaker_name}** (${f.role || '—'}) on **${f.topic}** [${f.sentiment}] — "${f.position}"`);
      if (f.evidence_quote) lines.push(`  - *Verbatim*: "${f.evidence_quote}"`);
    });
    lines.push('');
  }

  lines.push('## Corroborated Patterns');
  if (snap.patterns.total === 0) {
    lines.push('_No corroborated patterns yet._');
  } else {
    snap.patterns.top.forEach(p => {
      const gap = p.time_gap_days >= 0 ? `signal ${p.time_gap_days}d after meeting` : `signal ${Math.abs(p.time_gap_days)}d before meeting`;
      lines.push(`- **${p.pattern_type}** · ${p.topic} · ${p.confidence}${p.signal_grade ? ` · grade ${p.signal_grade}` : ''} — ${p.summary}`);
      lines.push(`  - ${gap}; signal: ${p.signal_title || '(none)'}`);
    });
  }
  lines.push('');

  lines.push('## Recent High-Grade Signals');
  if (snap.recent_high_grade_signals.length === 0) {
    lines.push('_No A/B-grade signals in window._');
  } else {
    snap.recent_high_grade_signals.slice(0, 8).forEach(s => {
      lines.push(`- [${s.source_grade}] ${s.title}${s.publisher_name ? ` (${s.publisher_name})` : ''}${s.source_url ? ` — [link](${s.source_url})` : ''}`);
    });
  }
  lines.push('');

  if (snap.pulse) {
    lines.push(`## Latest Pulse (${snap.pulse_period})`);
    Object.entries(snap.pulse.sections || {}).forEach(([key, sec]) => {
      lines.push(`### ${key.replace(/_/g, ' ')}`);
      lines.push(sec.synthesis || '_(no synthesis)_');
      lines.push('');
    });
  }

  if (snap.existing_engagements?.has_active_engagement) {
    lines.push('## ⚠ Existing engagements');
    snap.existing_engagements.active_engagements.forEach(e => {
      lines.push(`- **${e.engagement_type}** in state \`${e.state}\` — ${e.title || 'untitled'}`);
    });
  }

  lines.push('');
  lines.push('---');
  lines.push('_Generated by Nova engagementBridge. Every claim above traces to a Nova source record. Click links for verification._');
  return lines.join('\n');
}
