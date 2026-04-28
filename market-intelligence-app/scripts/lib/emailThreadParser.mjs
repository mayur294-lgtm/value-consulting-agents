/**
 * Email Thread Parser — paste an email thread, get stakeholder positions
 * ─────────────────────────────────────────────────────────────────────
 * Same input-loop closing as transcriptIngestor but for email threads.
 * AE pastes a reply chain, this lib:
 *   1. Extracts each named sender's stated positions, sentiment shifts,
 *      and topics raised (one synthetic "meeting" per thread)
 *   2. Persists as a meeting_history row of type='email'
 *   3. Hands off to meetingFactExtractor for structured facts
 *
 * Same anti-hallucination guardrails apply via the downstream extractor:
 * speakers must match persons, evidence quotes must be verbatim.
 */

import { callClaude, isApiKeyConfigured } from '../fetchers/claudeClient.mjs';
import { extractFactsFromMeeting, persistFacts } from './meetingFactExtractor.mjs';
import { randomUUID } from 'node:crypto';

const SYSTEM_PROMPT = `You extract structured intel from a banking sales email thread.

Given a raw paste of email replies (which may include "From:" headers, "On X wrote:" markers,
quoted-text indentation, signatures), produce a JSON object with this exact shape:

{
  "thread_date": "YYYY-MM-DD" (date of the most recent email; default to today if unclear),
  "subject": "Best inference of the thread subject (or empty string)",
  "participants": "Comma-separated list of named participants (and roles where mentioned)",
  "key_topics": ["topic 1", "topic 2", ...] (3-6 items, plain strings),
  "outcome": "progressed" | "stalled" | "scheduled" | "closed_won" | "closed_lost" | "no_decision",
  "notes": "Faithful 3-5 sentence summary of the thread's substance — what's being discussed, what positions emerged, what's resolved vs open. No invention.",
  "objections_raised": "Objections raised in the thread, separated by semicolons. Empty string if none.",
  "commitments_made": "Commitments / next steps stated in the thread, separated by semicolons. Empty string if none."
}

STRICT RULES:
1. Never invent participants who weren't named in the thread.
2. Never invent commitments that weren't stated.
3. The "notes" field MUST be a faithful summary, no extrapolation.
4. If the thread is too brief or noisy to extract structure, return notes="(thread too brief)".
5. Return ONLY the JSON. No markdown, no commentary.`;

/**
 * Parse an email thread and persist as a meeting_history row of type 'email'.
 *
 * @param {Database} db
 * @param {object} input
 *   bank_key: string (required)
 *   thread: string (required) — raw paste
 *   thread_date: string (optional override)
 * @returns { meeting_id, metadata, facts_extracted }
 */
export async function ingestEmailThread(db, input) {
  const { bank_key, thread, thread_date: overrideDate } = input;
  if (!bank_key) throw new Error('bank_key required');
  if (!thread || thread.length < 50) {
    throw new Error('thread too short — paste at least 50 characters');
  }
  if (!isApiKeyConfigured()) {
    throw new Error('ANTHROPIC_API_KEY not configured — email parse requires Claude.');
  }

  const safeThread = thread.slice(0, 30000);

  const userMessage = `BANK: ${bank_key}
${overrideDate ? `\n(Date hint: ${overrideDate})` : ''}

EMAIL THREAD:
${safeThread}

Extract structured intel as JSON.`;

  let raw;
  try {
    raw = await callClaude(SYSTEM_PROMPT, userMessage, { maxTokens: 1500, timeout: 60000 });
  } catch (err) {
    throw new Error(`Claude call failed: ${err.message}`);
  }

  const cleaned = raw.replace(/^```json?\s*/i, '').replace(/```$/, '').trim();
  let metadata;
  try { metadata = JSON.parse(cleaned); } catch {
    throw new Error('Could not parse Claude response as JSON.');
  }

  if (overrideDate) metadata.thread_date = overrideDate;

  const meetingDate = metadata.thread_date || new Date().toISOString().slice(0, 10);
  const attendees = metadata.participants || '';
  const keyTopics = Array.isArray(metadata.key_topics) ? JSON.stringify(metadata.key_topics) : '';
  const outcome = metadata.outcome || 'progressed';
  // Prefix notes with subject for clarity
  const notes = metadata.subject
    ? `[Email thread: "${metadata.subject}"] ${metadata.notes || ''}`
    : (metadata.notes || '');
  const objections = metadata.objections_raised || '';
  const commitments = metadata.commitments_made || '';

  const meetingId = randomUUID();
  db.prepare(`
    INSERT INTO meeting_history (
      id, bank_key, meeting_date, meeting_type, attendees, key_topics,
      outcome, notes, objections_raised, commitments_made
    ) VALUES (?, ?, ?, 'email', ?, ?, ?, ?, ?, ?)
  `).run(
    meetingId, bank_key, meetingDate, attendees, keyTopics,
    outcome, notes, objections, commitments
  );

  const persons = db.prepare(
    `SELECT id, canonical_name, role, role_category FROM persons WHERE bank_key = ? ORDER BY influence_score DESC`
  ).all(bank_key);

  const meetingRow = db.prepare('SELECT * FROM meeting_history WHERE id = ?').get(meetingId);
  const facts = await extractFactsFromMeeting(meetingRow, persons);
  persistFacts(db, meetingId, facts);

  return {
    meeting_id: meetingId,
    metadata: {
      thread_date: meetingDate,
      subject: metadata.subject || '',
      participants: attendees,
      key_topics: keyTopics ? JSON.parse(keyTopics) : [],
      outcome,
      notes,
      objections_raised: objections,
      commitments_made: commitments,
    },
    facts_extracted: facts.length,
    facts_attributed: facts.filter(f => f.speaker_person_id).length,
  };
}
