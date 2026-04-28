/**
 * Portfolio Query NL Translator — B3 (post-Sprint-5)
 * ──────────────────────────────────────────────────
 * Translates natural-language phrasing into a STRUCTURED PREDICATE JSON
 * that the existing portfolioQuery engine consumes. Critically: the LLM
 * does NOT execute the query, does NOT emit SQL, and does NOT name banks.
 * It only maps a phrase to a filter object whose schema we already trust.
 *
 * Why this preserves the moat:
 *   • The LLM is bounded to a closed predicate vocabulary
 *   • Output is validated against the schema; invalid → rejected
 *   • User sees the parsed predicates BEFORE running, can edit any of them
 *   • Same query → same answer, always (because the engine is deterministic)
 *
 * Failure modes are explicit:
 *   • Unknown predicate type → reject with "I can't map that phrase"
 *   • Unknown enum value → reject with the closest valid options listed
 *   • Empty predicates → reject (means LLM didn't understand the query)
 */

import { callClaude, isApiKeyConfigured } from '../fetchers/claudeClient.mjs';

// Mirror of the predicate schema in portfolioQuery.mjs — single source of truth
// for what the LLM is allowed to emit.
const PREDICATE_SCHEMA = {
  has_pattern: {
    description: 'Bank has a corroborated pattern (internal fact ↔ external signal)',
    args: {
      grade: { type: 'enum', values: ['A', 'B', 'C', 'D'], note: 'min source grade' },
      op: { type: 'enum', values: ['eq', 'gte'], default: 'gte' },
      topic: { type: 'enum', values: ['budget', 'vendors', 'timeline', 'politics', 'technical', 'blockers', 'other'], optional: true },
      confidence: { type: 'enum', values: ['high', 'medium', 'low'], optional: true },
      type: { type: 'enum', values: ['corroborates', 'contradicts', 'evolves'], optional: true },
      within_days: { type: 'number', optional: true },
    },
  },
  has_drift_trend: {
    description: 'A stakeholder drift trend matches (≥2 facts on same topic)',
    args: {
      trend: { type: 'enum', values: ['improving', 'deteriorating', 'mixed'] },
      topic: { type: 'enum', values: ['budget', 'vendors', 'timeline', 'politics', 'technical', 'blockers', 'other'], optional: true },
      min_facts: { type: 'number', default: 2 },
    },
  },
  has_signal: {
    description: 'A deal_signal matches the constraints',
    args: {
      grade: { type: 'enum', values: ['A', 'B', 'C', 'D'], optional: true },
      op: { type: 'enum', values: ['eq', 'gte'], default: 'gte' },
      category: { type: 'enum', values: ['strategic', 'momentum', 'stakeholder', 'competitive', 'regulatory', 'market', 'internal'], optional: true },
      severity: { type: 'enum', values: ['urgent', 'attention', 'info'], optional: true },
      within_days: { type: 'number', optional: true },
    },
  },
  pulse_score_change: {
    description: 'A pulse section score changed across two periods',
    args: {
      section: { type: 'enum', values: ['engagement_trend', 'market_signals', 'strategic_posture'], default: 'engagement_trend' },
      op: { type: 'enum', values: ['gte', 'lte', 'gt', 'lt'], default: 'lt' },
      value: { type: 'number', default: 0 },
      from: { type: 'string', default: '2026-Q1', note: 'period id like "2026-Q1"' },
      to: { type: 'string', default: '2026-Q2' },
    },
  },
  has_meeting_fact: {
    description: 'A meeting_fact matches the constraints',
    args: {
      topic: { type: 'enum', values: ['budget', 'vendors', 'timeline', 'politics', 'technical', 'blockers', 'other'], optional: true },
      sentiment: { type: 'enum', values: ['positive', 'neutral', 'mixed', 'negative'], optional: true },
      confidence_tier: { type: 'enum', values: [1, 2, 3], optional: true },
      within_days: { type: 'number', optional: true },
    },
  },
  country: {
    description: 'Bank is in a country',
    args: { equals: { type: 'string', note: 'country name like "Sweden"' } },
  },
  qualification_score: {
    description: 'Computed qualification score passes a threshold (0-10 scale)',
    args: {
      op: { type: 'enum', values: ['gte', 'lte', 'gt', 'lt'], default: 'gte' },
      value: { type: 'number' },
    },
  },
};

const VALID_TYPES = Object.keys(PREDICATE_SCHEMA);

const SYSTEM_PROMPT = `You translate a natural-language portfolio query into a STRUCTURED PREDICATE JSON.

You do NOT:
- Emit SQL
- Name specific banks
- Generate prose
- Execute the query

You DO:
- Map the user's phrasing to a JSON filter that the deterministic engine will run

Predicate schema (the only types you may emit):
${JSON.stringify(PREDICATE_SCHEMA, null, 2)}

Output shape:
{
  "filter": { "op": "and" | "or", "predicates": [<predicate>, ...] },
  "explanation": "1-sentence plain-English description of what you parsed",
  "warnings": ["any phrases you couldn't map", ...]
}

Each <predicate> is:
{
  "type": "<one of ${VALID_TYPES.join(' | ')}>",
  "<arg_key>": <value>,
  ...
}

STRICT RULES:
1. Only emit predicate types from the schema. If a phrase doesn't fit any of them, ADD a string to "warnings" instead of inventing a predicate.
2. Only emit enum values listed in the schema. Map common synonyms (e.g., "budget" → topic:"budget", "Q1" → "2026-Q1").
3. Default to op:"and" for combining multiple constraints, unless the phrase explicitly says "or" / "either".
4. Return ONLY the JSON object. No markdown, no commentary, no preamble.
5. If you can't parse the query at all, return {"filter":{"op":"and","predicates":[]},"explanation":"…","warnings":["…"]}.`;

function validatePredicate(p) {
  if (!p || typeof p !== 'object' || !p.type) return { ok: false, error: 'predicate missing type' };
  const schema = PREDICATE_SCHEMA[p.type];
  if (!schema) return { ok: false, error: `unknown predicate type: ${p.type}` };
  for (const [key, val] of Object.entries(p)) {
    if (key === 'type') continue;
    const argSchema = schema.args[key];
    if (!argSchema) {
      // Unknown arg — strip silently rather than fail (forward-compat)
      continue;
    }
    if (argSchema.type === 'enum' && !argSchema.values.includes(val)) {
      return { ok: false, error: `${p.type}.${key}=${val} not in ${argSchema.values.join('|')}` };
    }
    if (argSchema.type === 'number' && typeof val !== 'number') {
      return { ok: false, error: `${p.type}.${key} must be a number` };
    }
  }
  return { ok: true };
}

function validateFilter(filter) {
  if (!filter || typeof filter !== 'object') return { ok: false, error: 'filter missing' };
  const op = filter.op || 'and';
  if (op !== 'and' && op !== 'or') return { ok: false, error: `invalid op: ${op}` };
  const preds = filter.predicates || [];
  if (!Array.isArray(preds)) return { ok: false, error: 'predicates must be array' };
  const errors = [];
  for (const p of preds) {
    const r = validatePredicate(p);
    if (!r.ok) errors.push(r.error);
  }
  return { ok: errors.length === 0, errors };
}

/**
 * Translate a natural-language portfolio query into a structured filter.
 *
 * Returns:
 *   { ok: true, filter, explanation, warnings, predicate_count }
 *   { ok: false, error, validation_errors? }
 */
export async function translateQuery(naturalLanguage) {
  if (!isApiKeyConfigured()) {
    return { ok: false, error: 'ANTHROPIC_API_KEY not configured — NL translation unavailable.' };
  }
  if (!naturalLanguage || typeof naturalLanguage !== 'string' || naturalLanguage.trim().length < 3) {
    return { ok: false, error: 'Query too short.' };
  }

  let raw;
  try {
    raw = await callClaude(SYSTEM_PROMPT, naturalLanguage.trim(), { maxTokens: 800, timeout: 30000 });
  } catch (err) {
    return { ok: false, error: `Claude call failed: ${err.message}` };
  }

  const cleaned = raw.replace(/^```json?\s*/i, '').replace(/```$/, '').trim();
  let parsed;
  try { parsed = JSON.parse(cleaned); } catch {
    return { ok: false, error: 'Could not parse Claude response as JSON.' };
  }

  const filter = parsed.filter;
  const validation = validateFilter(filter);
  if (!validation.ok) {
    return {
      ok: false,
      error: 'Generated filter failed validation.',
      validation_errors: validation.errors,
      filter,  // return so UI can show what was attempted
      explanation: parsed.explanation,
      warnings: parsed.warnings,
    };
  }

  if (!filter.predicates || filter.predicates.length === 0) {
    return {
      ok: false,
      error: parsed.warnings?.length
        ? `Couldn't map your phrasing to any predicate: ${parsed.warnings.join('; ')}`
        : `No predicates generated. Try rephrasing using primitives like "deteriorating CFOs", "high-grade signals in last 30 days", "Swedish banks".`,
      explanation: parsed.explanation,
      warnings: parsed.warnings || [],
    };
  }

  return {
    ok: true,
    filter,
    explanation: parsed.explanation || '(no explanation provided)',
    warnings: parsed.warnings || [],
    predicate_count: filter.predicates.length,
  };
}

export { PREDICATE_SCHEMA, VALID_TYPES };
