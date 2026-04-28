/**
 * Transcript Ingestor — paste a meeting transcript, get structured intel
 * ─────────────────────────────────────────────────────────────────────
 * Closes the meeting-intel input loop. AE pastes a transcript (Zoom,
 * Teams, Otter, etc.) → this lib extracts:
 *   1. Meeting metadata (date, attendees, key topics, outcome)
 *   2. Stakeholder facts (delegated to existing meetingFactExtractor —
 *      same anti-hallucination guardrails: speaker matches persons,
 *      verbatim quotes required)
 *
 * The transcript ingestor is a THIN ORCHESTRATOR — it doesn't reinvent
 * fact extraction. It uses Claude to identify metadata + structure, then
 * persists the meeting and hands off to meetingFactExtractor.
 */

import { callClaude, isApiKeyConfigured } from '../fetchers/claudeClient.mjs';
import { extractFactsFromMeeting, persistFacts } from './meetingFactExtractor.mjs';
import { randomUUID } from 'node:crypto';

const SYSTEM_PROMPT = `You extract structured metadata from a banking sales meeting transcript.

Given a raw transcript (which may include speaker labels, timestamps, or be plain prose),
produce a JSON object with this exact shape:

{
  "meeting_date": "YYYY-MM-DD" (your best inference; default to today if unknown),
  "meeting_type": "client" | "internal" | "discovery" | "demo" | "negotiation" | "kickoff",
  "attendees": "Comma-separated list of attendee names (and roles where mentioned)",
  "key_topics": ["topic 1", "topic 2", ...] (3-7 items, plain strings),
  "outcome": "scheduled" | "progressed" | "stalled" | "closed_won" | "closed_lost" | "no_decision",
  "notes": "A faithful 3-5 sentence summary of what was discussed and decided. Plain prose. No invention.",
  "objections_raised": "Concise list of objections raised, separated by semicolons. Empty string if none.",
  "commitments_made": "Concise list of commitments/next steps committed to, separated by semicolons. Empty string if none."
}

STRICT RULES:
1. Never invent attendees who weren't named in the transcript.
2. Never invent commitments that weren't stated.
3. The "notes" field MUST be a faithful summary — do not extrapolate beyond what's said.
4. If the transcript is too short or noisy to extract any meaningful structure, return notes="(transcript too brief to extract structure)" and other fields blank.
5. Return ONLY the JSON. No markdown, no commentary.`;

/**
 * Extract metadata from a transcript and persist a meeting_history row.
 *
 * @param {Database} db
 * @param {object} input
 *   bank_key: string (required)
 *   transcript: string (required) — raw paste
 *   meeting_date: string (optional override)
 *   meeting_type: string (optional override)
 * @returns { meeting_id, metadata, facts_extracted }
 */
export async function ingestTranscript(db, input) {
  const { bank_key, transcript, meeting_date: overrideDate, meeting_type: overrideType } = input;
  if (!bank_key) throw new Error('bank_key required');
  if (!transcript || transcript.length < 50) {
    throw new Error('transcript too short — paste at least 50 characters');
  }
  if (!isApiKeyConfigured()) {
    throw new Error('ANTHROPIC_API_KEY not configured — transcript ingest requires Claude.');
  }

  // Truncate excessively long transcripts (Claude context limits)
  const safeTranscript = transcript.slice(0, 30000);

  // Call Claude to extract structured metadata
  const userMessage = `BANK: ${bank_key}
${overrideDate ? `\n(Date hint: ${overrideDate})` : ''}
${overrideType ? `\n(Type hint: ${overrideType})` : ''}

TRANSCRIPT:
${safeTranscript}

Extract structured metadata as JSON.`;

  let raw;
  try {
    raw = await callClaude(SYSTEM_PROMPT, userMessage, { maxTokens: 1500, timeout: 60000 });
  } catch (err) {
    throw new Error(`Claude call failed: ${err.message}`);
  }

  const cleaned = raw.replace(/^```json?\s*/i, '').replace(/```$/, '').trim();
  let metadata;
  try {
    metadata = JSON.parse(cleaned);
  } catch {
    throw new Error('Could not parse Claude response as JSON.');
  }

  // Apply overrides if provided
  if (overrideDate) metadata.meeting_date = overrideDate;
  if (overrideType) metadata.meeting_type = overrideType;

  // Sanitize fields
  const meetingDate = metadata.meeting_date || new Date().toISOString().slice(0, 10);
  const meetingType = metadata.meeting_type || 'client';
  const attendees = metadata.attendees || '';
  const keyTopics = Array.isArray(metadata.key_topics) ? JSON.stringify(metadata.key_topics) : '';
  const outcome = metadata.outcome || 'progressed';
  const notes = metadata.notes || '';
  const objections = metadata.objections_raised || '';
  const commitments = metadata.commitments_made || '';

  // Persist to meeting_history
  const meetingId = randomUUID();
  db.prepare(`
    INSERT INTO meeting_history (
      id, bank_key, meeting_date, meeting_type, attendees, key_topics,
      outcome, notes, objections_raised, commitments_made
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    meetingId, bank_key, meetingDate, meetingType, attendees, keyTopics,
    outcome, notes, objections, commitments
  );

  // Hand off to meetingFactExtractor for fact-level structuring
  const persons = db.prepare(
    `SELECT id, canonical_name, role, role_category FROM persons WHERE bank_key = ? ORDER BY influence_score DESC`
  ).all(bank_key);

  const meetingRow = db.prepare('SELECT * FROM meeting_history WHERE id = ?').get(meetingId);
  const facts = await extractFactsFromMeeting(meetingRow, persons);
  persistFacts(db, meetingId, facts);

  return {
    meeting_id: meetingId,
    metadata: {
      meeting_date: meetingDate,
      meeting_type: meetingType,
      attendees,
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
