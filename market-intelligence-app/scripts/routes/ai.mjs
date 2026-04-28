/**
 * AI / Research route handlers.
 *
 * Endpoints:
 *   GET  /api/status                    — API key check
 *   POST /api/analyze                   — Analyze raw intelligence
 *   POST /api/analyze-news              — Analyze news articles
 *   POST /api/deep-analysis             — Deep bank analysis
 *   GET  /api/research/status           — Research availability
 *   POST /api/research/person           — Person research
 *   POST /api/research/context          — Context enrichment
 *   POST /api/research/meeting-prep     — Meeting prep brief
 *   POST /api/research/landing-zones    — Landing zone matrix
 *   POST /api/research/discovery-storyline — Discovery storyline
 *   POST /api/research/value-hypothesis — Value hypothesis
 *   POST /api/research/engagement-plan  — Post-meeting engagement plan
 */

import crypto from 'node:crypto';
import { structureIntelWithClaude, analyzeNewsForBank, deepAnalyzeBank, isClaudeAvailable } from '../fetchers/claudeAnalyzer.mjs';
import { callClaude } from '../fetchers/claudeClient.mjs';
import { researchPerson, enrichContext, isResearchAvailable } from '../fetchers/personResearch.mjs';
import { generateMeetingPrep, generateEngagementPlan, isMeetingPrepAvailable, formatProvenanceForPrompt, formatMeetingHistoryForPrompt } from '../fetchers/meetingPrepAgent.mjs';
import { getProvenanceForEntity } from '../lib/provenanceWriter.mjs';
import { getChangesForBank, formatChangesForPrompt } from '../lib/changeWriter.mjs';
import { analyzeLandingZones, isLandingZoneAgentAvailable } from '../fetchers/landingZoneAgent.mjs';
import { generateDiscoveryStoryline, isDiscoveryStorylineAvailable } from '../fetchers/discoveryStorylineAgent.mjs';
import { generateValueHypothesisForMeeting, isValueHypothesisAvailable } from '../fetchers/valueHypothesisAgent.mjs';
import { refreshCountryIntelligence, isCountryIntelAvailable } from '../fetchers/countryIntelAgent.mjs';
import { BACKBASE_2026_CONTEXT } from '../lib/backbaseContext.mjs';
import { getValidatedFactsBlockForBank } from '../lib/strategicInsights.mjs';
import { jsonResponse, parseBody, createRateLimiter } from './helpers.mjs';

// Rate limit: max 20 AI requests per minute (generous for normal use, blocks runaways)
const aiRateCheck = createRateLimiter(20, 60_000);

/**
 * Try to handle an AI/research route. Returns true if handled, false if not matched.
 */
export async function handleAiRoute(req, res, { path, db, parseRow }) {
  // ── GET /api/status ──
  if (path === '/api/status' && req.method === 'GET') {
    jsonResponse(res, 200, {
      available: isClaudeAvailable(),
      model: 'claude-sonnet-4-20250514',
      timestamp: new Date().toISOString(),
    });
    return true;
  }

  // ── POST /api/analyze ──
  if (path === '/api/analyze' && req.method === 'POST') {
    if (!aiRateCheck(res)) return true; // 429 already sent
    if (!isClaudeAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured' });
      return true;
    }
    const { category, text, bankContext } = await parseBody(req);
    if (!category || !text) {
      jsonResponse(res, 400, { error: 'Missing required fields: category, text' });
      return true;
    }
    console.log(`🤖 Analyzing ${category} for ${bankContext?.bankName || 'unknown bank'}...`);
    const result = await structureIntelWithClaude(category, text, bankContext || {});
    console.log(`   ✅ Analysis complete`);
    jsonResponse(res, 200, { result, _source: 'claude-ai' });
    return true;
  }

  // ── POST /api/analyze-news ──
  if (path === '/api/analyze-news' && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isClaudeAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured' });
      return true;
    }
    const { bankName, articles } = await parseBody(req);
    if (!bankName || !articles) {
      jsonResponse(res, 400, { error: 'Missing required fields: bankName, articles' });
      return true;
    }
    console.log(`🤖 Analyzing ${articles.length} articles for ${bankName}...`);
    const result = await analyzeNewsForBank(bankName, articles);
    console.log(`   ✅ News analysis complete`);
    jsonResponse(res, 200, { result, _source: 'claude-ai' });
    return true;
  }

  // ── POST /api/deep-analysis ──
  if (path === '/api/deep-analysis' && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isClaudeAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured' });
      return true;
    }
    const { bankName, analysisType, context } = await parseBody(req);
    if (!bankName || !analysisType) {
      jsonResponse(res, 400, { error: 'Missing required fields: bankName, analysisType' });
      return true;
    }
    console.log(`🤖 Deep analysis (${analysisType}) for ${bankName}...`);
    const result = await deepAnalyzeBank(bankName, analysisType, context || {});
    console.log(`   ✅ ${analysisType} analysis complete`);
    jsonResponse(res, 200, { result, _source: 'claude-ai', analysisType });
    return true;
  }

  // ── GET /api/research/status ──
  if (path === '/api/research/status' && req.method === 'GET') {
    jsonResponse(res, 200, { available: isResearchAvailable() });
    return true;
  }

  // ── POST /api/research/person ──
  if (path === '/api/research/person' && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isResearchAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured. Person research requires AI.' });
      return true;
    }
    const { name, role, customRole, bankName, bankKey, bankContext } = await parseBody(req);
    if (!name || !bankName) {
      jsonResponse(res, 400, { error: 'Missing required fields: name, bankName' });
      return true;
    }
    console.log(`🔍 Person research: ${name} at ${bankName}...`);
    const result = await researchPerson({ name, role, customRole, bankName, bankKey, bankContext });
    console.log(`   ✅ Person research complete`);
    jsonResponse(res, 200, { result });
    return true;
  }

  // ── POST /api/research/context ──
  if (path === '/api/research/context' && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isResearchAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured. Context enrichment requires AI.' });
      return true;
    }
    const { bankName, scopeText, painText, attendeeRoles, bankContext } = await parseBody(req);
    if (!bankName) {
      jsonResponse(res, 400, { error: 'Missing required field: bankName' });
      return true;
    }
    console.log(`🔍 Context enrichment for ${bankName}...`);
    const result = await enrichContext({ bankName, scopeText, painText, attendeeRoles, bankContext });
    console.log(`   ✅ Context enrichment complete`);
    jsonResponse(res, 200, { result });
    return true;
  }

  // ── POST /api/research/meeting-prep ──
  // B2 SOFT-DEPRECATED (Strategic Repositioning brief): generates prose-style
  // 5-minute meeting briefs that compete directly with Claude-in-a-chat.
  // Replacement: AE uses the structured Pulse, Stakeholder Intelligence panel,
  // and per-bank ChangeFeed to assemble their own context. Hard delete 2026-05-28.
  if (path === '/api/research/meeting-prep' && req.method === 'POST') {
    res.setHeader('Deprecation', 'true');
    res.setHeader('Sunset', 'Wed, 28 May 2026 00:00:00 GMT');
    res.setHeader('Link', '</docs/strategic-repositioning>; rel="deprecation"');
    console.warn('[deprecated] /api/research/meeting-prep called — Nova does not generate prose-style meeting briefs. Use Pulse + Stakeholder Intelligence panel instead. Hard delete scheduled 2026-05-28.');
    if (!aiRateCheck(res)) return true;
    if (!isMeetingPrepAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured. Meeting prep requires AI.' });
      return true;
    }
    const { bankName, bankKey, attendees, topics, scopeKnown, painPointKnown, scopeText, painText, mode, positionProduct, positionPainPoints, competitors, region } = await parseBody(req);
    if (!bankName || !bankKey || !topics?.length) {
      jsonResponse(res, 400, { error: 'Missing required fields: bankName, bankKey, topics[]' });
      return true;
    }
    const bankRow = db.prepare('SELECT data FROM banks WHERE key = ?').get(bankKey);
    const bankData = bankRow?.data ? JSON.parse(bankRow.data) : {};
    // Layer 1: fetch provenance records and format for prompt injection
    const provenanceRows = getProvenanceForEntity('bank', bankKey);
    const provenanceContext = formatProvenanceForPrompt(provenanceRows);
    // Layer 3: fetch recent changes (last 30 days) for brief context
    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
    const recentChanges = getChangesForBank(bankKey, { since: thirtyDaysAgo, limit: 10 });
    const changesContext = formatChangesForPrompt(recentChanges);
    // Layer 4: fetch prior meeting history for deal context
    const meetingRows = db.prepare(`SELECT * FROM meeting_history WHERE bank_key = ? AND meeting_type = 'client' ORDER BY meeting_date DESC LIMIT 3`).all(bankKey);
    const meetingHistoryContext = formatMeetingHistoryForPrompt(meetingRows.map(r => parseRow('meeting_history', r)));
    const isPositionMode = mode === 'position';
    console.log(`📋 Meeting prep${isPositionMode ? ' [POSITION MODE]' : ''}: ${bankName} | ${isPositionMode ? `Product: ${positionProduct}` : `Topics: ${topics.join(', ')}`}${provenanceRows.length > 0 ? ` | ${provenanceRows.length} provenance records` : ''}${recentChanges.length > 0 ? ` | ${recentChanges.length} recent changes` : ''}${meetingRows.length > 0 ? ` | ${meetingRows.length} prior meetings` : ''}`);
    const result = await generateMeetingPrep({
      bankName, bankKey, attendees, topics,
      scopeKnown, painPointKnown, scopeText, painText, bankData,
      mode, positionProduct, positionPainPoints,
      competitors, region, provenanceContext, changesContext, meetingHistoryContext,
    });
    console.log(`   ✅ Meeting prep complete`);
    jsonResponse(res, 200, { result });
    return true;
  }

  // ── POST /api/research/landing-zones ──
  if (path === '/api/research/landing-zones' && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isLandingZoneAgentAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured. Landing zone analysis requires AI.' });
      return true;
    }
    const { bankName, bankKey, meetingContext } = await parseBody(req);
    if (!bankName || !bankKey) {
      jsonResponse(res, 400, { error: 'Missing required fields: bankName, bankKey' });
      return true;
    }
    const bankRow = db.prepare('SELECT data FROM banks WHERE key = ?').get(bankKey);
    const bankData = bankRow?.data ? JSON.parse(bankRow.data) : {};
    console.log(`🎯 Landing zone analysis: ${bankName}${meetingContext ? ' (meeting-tailored)' : ''}...`);
    const result = await analyzeLandingZones({ bankName, bankKey, bankData, meetingContext });

    db.prepare(`
      INSERT INTO landing_zone_matrix (bank_key, matrix, plays, unconsidered, challenges, top_zones)
      VALUES (?, ?, ?, ?, ?, ?)
      ON CONFLICT(bank_key) DO UPDATE SET
        matrix = excluded.matrix, plays = excluded.plays,
        unconsidered = excluded.unconsidered, challenges = excluded.challenges,
        top_zones = excluded.top_zones, updated_at = datetime('now')
    `).run(
      bankKey,
      JSON.stringify(result.matrix),
      JSON.stringify(result.modernizationPlays),
      JSON.stringify(result.unconsideredNeeds),
      JSON.stringify(result.challenges),
      JSON.stringify(result.topLandingZones)
    );

    console.log(`   ✅ Landing zone analysis complete and persisted`);
    jsonResponse(res, 200, { result });
    return true;
  }

  // ── POST /api/research/discovery-storyline ──
  if (path === '/api/research/discovery-storyline' && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isDiscoveryStorylineAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured. Discovery storyline requires AI.' });
      return true;
    }
    const { bankName, bankKey, meetingContext } = await parseBody(req);
    if (!bankName || !bankKey) {
      jsonResponse(res, 400, { error: 'Missing required fields: bankName, bankKey' });
      return true;
    }
    const bankRow = db.prepare('SELECT data FROM banks WHERE key = ?').get(bankKey);
    const bankData = bankRow?.data ? JSON.parse(bankRow.data) : {};
    const lzRow = db.prepare('SELECT * FROM landing_zone_matrix WHERE bank_key = ?').get(bankKey);
    const lzMatrixData = lzRow ? parseRow('landing_zone_matrix', lzRow) : null;
    console.log(`\n🎯 Discovery storyline generation: ${bankName}${meetingContext ? ' (meeting-tailored)' : ''}...`);
    const result = await generateDiscoveryStoryline({ bankName, bankKey, bankData, lzMatrixData, meetingContext });

    db.prepare(`
      INSERT INTO discovery_storylines (bank_key, storyline, roi_estimate, next_steps)
      VALUES (?, ?, ?, ?)
      ON CONFLICT(bank_key) DO UPDATE SET
        storyline = excluded.storyline, roi_estimate = excluded.roi_estimate,
        next_steps = excluded.next_steps, updated_at = datetime('now')
    `).run(
      bankKey,
      JSON.stringify(result),
      JSON.stringify(result.illustrativeRoi || null),
      JSON.stringify(result.nextSteps || null)
    );

    console.log(`   ✅ Discovery storyline complete and persisted`);
    jsonResponse(res, 200, { result });
    return true;
  }

  // ── POST /api/research/value-hypothesis ──
  if (path === '/api/research/value-hypothesis' && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isValueHypothesisAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured.' });
      return true;
    }
    const { bankName, bankKey, meetingContext } = await parseBody(req);
    if (!bankName || !bankKey) {
      jsonResponse(res, 400, { error: 'Missing required fields: bankName, bankKey' });
      return true;
    }
    const bankRow = db.prepare('SELECT data FROM banks WHERE key = ?').get(bankKey);
    const bankData = bankRow?.data ? JSON.parse(bankRow.data) : {};
    const vsRow = db.prepare('SELECT data FROM value_selling WHERE bank_key = ?').get(bankKey);
    const existingHypothesis = vsRow?.data ? JSON.parse(vsRow.data)?.value_hypothesis || null : null;

    console.log(`\n🎯 Value hypothesis generation: ${bankName} (meeting-tailored)...`);
    const result = await generateValueHypothesisForMeeting({
      bankName, bankData, meetingContext, existingHypothesis,
    });
    console.log(`   ✅ Value hypothesis complete`);
    jsonResponse(res, 200, { result });
    return true;
  }

  // ── POST /api/banks/:key/meetings/extract — AI transcript extraction (Layer 4) ──
  const extractMatch = path.match(/^\/api\/banks\/([^/]+)\/meetings\/extract$/);
  if (extractMatch && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isClaudeAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured. Transcript extraction requires AI.' });
      return true;
    }
    const bankKey = decodeURIComponent(extractMatch[1]);
    const { transcript } = await parseBody(req);
    if (!transcript) {
      jsonResponse(res, 400, { error: 'Missing required field: transcript' });
      return true;
    }
    if (transcript.length > 50000) {
      jsonResponse(res, 400, { error: 'Transcript too long — please trim to the relevant portion (max 50,000 characters)' });
      return true;
    }

    console.log(`📝 Transcript extraction: ${bankKey} (${transcript.length} chars)...`);

    const extractionPrompt = `You are a meeting transcript analyzer for B2B fintech sales. Extract structured meeting data from the raw transcript below.

TRANSCRIPT FORMAT HANDLING:
- Ignore speaker labels (e.g., "Speaker 1:", "Oumaima:", "John Smith:")
- Ignore timestamps (e.g., "00:14:32", "[14:32]", "2:30 PM")
- Ignore filler words, greetings, and small talk
- Focus ONLY on substantive business content
- If the transcript is messy, incomplete, or has formatting artifacts, extract what you can and note gaps

EXTRACTION RULES:
- attendees: Extract names and roles mentioned. If only first names appear, use them. If roles aren't stated, infer from context or use null.
- key_topics: Maximum 5 topics. Use short, specific labels (e.g., "digital onboarding timeline" not "technology discussion").
- objections_raised: Only include genuine concerns or pushback from the CLIENT side, not questions or clarifications.
- commitments_made: Each commitment must have an owner. If the owner isn't clear, use "unclear". All commitments start with fulfilled: false. Include deadline if mentioned.
- outcome: Infer from the overall tone and ending:
  "progressed" = positive momentum, next steps agreed
  "stalled" = no clear next step, unresolved blockers
  "lost" = explicit rejection or deal-ending language
  "won" = explicit agreement to proceed with purchase/POC
  If truly ambiguous, use "progressed" as default.
- notes: 2-3 sentence summary capturing the key takeaway a rep needs before the next meeting.

Return ONLY valid JSON. No markdown code fences. No preamble. No explanation.

{
  "meeting_date": "YYYY-MM-DD or null if not mentioned",
  "attendees": [
    { "name": "Person Name", "role": "Their Role or null" }
  ],
  "key_topics": ["topic1", "topic2"],
  "objections_raised": ["objection text"],
  "commitments_made": [
    { "commitment": "What was committed", "owner": "Who owns it", "deadline": "By when or null", "fulfilled": false }
  ],
  "outcome": "progressed",
  "notes": "2-3 sentence summary"
}`;

    const { callClaude } = await import('../fetchers/claudeClient.mjs');
    const raw = await callClaude(extractionPrompt, transcript, { maxTokens: 2048, timeout: 60000 });

    try {
      const jsonStr = raw.replace(/```json\n?|\n?```/g, '').trim();
      const result = JSON.parse(jsonStr);
      result._source = 'transcript_extraction';
      console.log(`   ✅ Transcript extraction complete: ${result.attendees?.length || 0} attendees, ${result.key_topics?.length || 0} topics`);
      jsonResponse(res, 200, { result });
    } catch (err) {
      console.error(`   Warning: Failed to parse extraction response: ${err.message}`);
      jsonResponse(res, 200, {
        result: {
          meeting_date: null,
          attendees: [],
          key_topics: [],
          objections_raised: [],
          commitments_made: [],
          outcome: 'progressed',
          notes: 'Transcript extraction failed — please enter meeting details manually.',
          _source: 'extraction_fallback',
          _error: err.message,
        }
      });
    }
    return true;
  }

  // ── POST /api/research/engagement-plan ──
  if (path === '/api/research/engagement-plan' && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isMeetingPrepAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured. Engagement plan requires AI.' });
      return true;
    }
    const { bankName, originalBrief, outcome, resonatedPriorities, clientAskedFor, agreedNextStep, attendees } = await parseBody(req);
    if (!bankName || !outcome) {
      jsonResponse(res, 400, { error: 'Missing required fields: bankName, outcome' });
      return true;
    }
    console.log(`📋 Engagement plan: ${bankName} (${outcome})`);
    const result = await generateEngagementPlan({
      bankName, originalBrief, outcome, resonatedPriorities,
      clientAskedFor, agreedNextStep, attendees,
    });
    console.log(`   ✅ Engagement plan complete`);
    jsonResponse(res, 200, { result });
    return true;
  }

  // ── POST /api/research/executive-brief — AI-synthesized narrative briefing ──
  // B2 SOFT-DEPRECATED (Strategic Repositioning brief): generates prospect-facing
  // narrative briefs — exactly the prose drift Nova should not produce. AEs use
  // the Pulse HTML export for leadership shares (carries source provenance) and
  // Claude-in-a-chat for any narrative writing they need. Hard delete 2026-05-28.
  if (path === '/api/research/executive-brief' && req.method === 'POST') {
    res.setHeader('Deprecation', 'true');
    res.setHeader('Sunset', 'Wed, 28 May 2026 00:00:00 GMT');
    res.setHeader('Link', '</docs/strategic-repositioning>; rel="deprecation"');
    console.warn('[deprecated] /api/research/executive-brief called — Nova does not generate narrative briefs. Use Pulse HTML export for source-cited leadership shares. Hard delete scheduled 2026-05-28.');
    if (!aiRateCheck(res)) return true;
    if (!isClaudeAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured.' });
      return true;
    }
    const { bankKey } = await parseBody(req);
    if (!bankKey) { jsonResponse(res, 400, { error: 'Missing bankKey' }); return true; }

    // Gather full bank context from all tables
    const bankRow = db.prepare('SELECT * FROM banks WHERE key = ?').get(bankKey);
    if (!bankRow) { jsonResponse(res, 404, { error: 'Bank not found' }); return true; }
    const bd = JSON.parse(bankRow.data || '{}');
    const qualRow = db.prepare('SELECT data FROM qualification WHERE bank_key = ?').get(bankKey);
    const qd = qualRow ? JSON.parse(qualRow.data) : null;
    const cxRow = db.prepare('SELECT * FROM cx WHERE bank_key = ?').get(bankKey);
    const compRow = db.prepare('SELECT data FROM competition WHERE bank_key = ?').get(bankKey);
    const comp = compRow ? JSON.parse(compRow.data) : null;
    const vsRow = db.prepare('SELECT data FROM value_selling WHERE bank_key = ?').get(bankKey);
    const vs = vsRow ? JSON.parse(vsRow.data) : null;

    console.log(`📋 AI Executive Brief: ${bankRow.bank_name}`);

    const systemPrompt = `You are a senior Value Consultant at Backbase, the AI-native Banking OS / AI-Powered Banking Platform vendor, preparing an executive briefing for a sales meeting with a bank. Write a concise, narrative-style intelligence brief that a consultant would actually send before a customer call.

${BACKBASE_2026_CONTEXT}

WRITING STYLE:
- Write in the first person plural ("we", "our opportunity")
- Lead with the strategic narrative, not a data dump
- Connect pain points to landing zones to value — tell the STORY of why this bank needs Backbase
- Highlight what makes this bank unique — don't be generic
- Be honest about data gaps and risks — consultants lose credibility by overselling
- End with a clear recommended approach and next steps
- Keep it to 400-600 words — this is a briefing, not a report

STRUCTURE (use these exact headings):
## Strategic Context
Why this bank matters and what's happening in their market right now.

## Key Opportunity
The 2-3 strongest reasons Backbase fits this bank, tied to specific pain points and evidence.

## Decision Landscape
Who makes the decision, what's the timeline, what could block us.

## Risks & Data Gaps
What we don't know and what assumptions we're making.

## Recommended Approach
Specific next steps — who to contact, what to lead with, what to avoid.

Return the brief as plain text with ## headings. Do NOT wrap in JSON or code blocks.`;

    // Pack C: validated-facts injection (acknowledged signals)
    const validatedFactsBlock = getValidatedFactsBlockForBank(db, bankKey);

    const userPrompt = `Bank: ${bankRow.bank_name} (${bankRow.country})
Score: ${bankRow.tagline || ''}

${validatedFactsBlock ? validatedFactsBlock + '\n\n' : ''}Overview: ${(bd.overview || '').substring(0, 500)}

Financials: ${bd.operational_profile ? JSON.stringify(bd.operational_profile) : 'Not available'}

Pain Points:
${(bd.pain_points || []).map(p => `- ${p.title}: ${p.detail}`).join('\n')}

Signals:
${(bd.signals || []).map(s => `- ${s.signal}: ${s.implication}`).join('\n')}

Landing Zones:
${(bd.backbase_landing_zones || []).map(z => `- ${z.zone} (${z.fit_score}/10): ${z.rationale}`).join('\n')}

Value Hypothesis: ${vs?.value_hypothesis?.one_liner || 'Not defined'}
IF: ${vs?.value_hypothesis?.if_condition || 'N/A'}
THEN: ${vs?.value_hypothesis?.then_outcome || 'N/A'}
BY: ${vs?.value_hypothesis?.by_deploying || 'N/A'}

Qualification: ${qd ? Object.entries(qd).map(([k, v]) => `${k}: ${v.score}/10 — ${v.note}`).join('\n') : 'Not scored'}

Deal Context: ${bd.backbase_qualification ? `Deal size: ${bd.backbase_qualification.deal_size || 'N/A'}, Timing: ${bd.backbase_qualification.timing || 'N/A'}, Risk: ${bd.backbase_qualification.risk || 'N/A'}` : 'Not available'}

Competition: ${comp ? `Core: ${comp.core_banking || 'N/A'}, Digital: ${comp.digital_platform || 'N/A'}, Vendors: ${(comp.key_vendors || []).join(', ')}, Risk: ${comp.vendor_risk || 'N/A'}` : 'Not available'}

CX: ${cxRow ? `iOS: ${cxRow.app_rating_ios || 'N/A'}, Android: ${cxRow.app_rating_android || 'N/A'}` : 'Not available'}

Key People:
${(bd.key_decision_makers || []).filter(k => k.name && !k.name.startsWith('(')).slice(0, 8).map(k => `- ${k.name}: ${k.role}${k.note ? ' — ' + k.note.substring(0, 80) : ''}`).join('\n')}

Recommended Approach: ${bd.recommended_approach || 'Not defined'}`;

    try {
      const raw = await callClaude(systemPrompt, userPrompt, { maxTokens: 2048, timeout: 60000 });
      console.log(`   ✅ AI Executive Brief complete`);
      jsonResponse(res, 200, { brief: raw });
    } catch (err) {
      console.error(`   ❌ AI Brief failed: ${err.message}`);
      jsonResponse(res, 500, { error: 'Brief generation failed: ' + err.message });
    }
    return true;
  }

  // ── POST /api/generate-account-plan — Full account plan document generation ──
  if (path === '/api/generate-account-plan' && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isClaudeAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured.' });
      return true;
    }
    const { bankKey, manualInputs } = await parseBody(req);
    if (!bankKey) { jsonResponse(res, 400, { error: 'Missing bankKey' }); return true; }

    const bankRow = db.prepare('SELECT * FROM banks WHERE key = ?').get(bankKey);
    if (!bankRow) { jsonResponse(res, 404, { error: 'Bank not found' }); return true; }
    const bd = JSON.parse(bankRow.data || '{}');
    const qualRow = db.prepare('SELECT data FROM qualification WHERE bank_key = ?').get(bankKey);
    const qd = qualRow ? JSON.parse(qualRow.data) : null;
    const cxRow = db.prepare('SELECT * FROM cx WHERE bank_key = ?').get(bankKey);
    const compRow = db.prepare('SELECT data FROM competition WHERE bank_key = ?').get(bankKey);
    const comp = compRow ? JSON.parse(compRow.data) : null;
    const vsRow = db.prepare('SELECT data FROM value_selling WHERE bank_key = ?').get(bankKey);
    const vs = vsRow ? JSON.parse(vsRow.data) : null;
    const persons = db.prepare('SELECT canonical_name, role, role_category, note FROM persons WHERE bank_key = ? ORDER BY role_category').all(bankKey);

    console.log(`📋 Account Plan Doc: ${bankRow.bank_name}`);

    // Strategic Repositioning Sprint 0.4 — schema refactored to remove prose.
    // REMOVED: `pov_summary` (2-3 sentence narrative POV — drifted toward
    //          editorial commentary), `business_overview.description`
    //          (2-3 paragraph generic company description — the brief
    //          explicitly calls this out as commodity Wikipedia-dump content).
    // ADDED:   `pov_anchors` (structured points), `business_overview.key_facts`
    //          (fact rows with sources). Same intelligence, no prose.
    const systemPrompt = `You are Nova, assembling a STRUCTURED account plan for ${bankRow.bank_name}. This is internal AE intelligence, not a prospect-facing document. Every field must be populated with specific, sourced facts — never placeholder text, never generic commentary, never prose narrative.

${BACKBASE_2026_CONTEXT}

When mapping value to capabilities, use current product names: Banking OS, APA (Agentic Process Automation), CLO (Customer Lifetime Orchestrator), and segment OSes (Wealth OS, Commercial OS, Small Business OS, Private Banking OS, Retail OS). Reference the three commercial entry points (Conversational Banking, Agentic Servicing, Agentic Onboarding & Origination) where they fit the deal stage.

Return ONLY valid JSON matching the schema below. No markdown fences. No preamble. NO PROSE NARRATIVE FIELDS.

{
  "account_snapshot": {
    "strategic_initiatives": [
      { "initiative": "string", "challenge": "string", "backbase_advantage": "string" }
    ],
    "backbase_proposition": ["string"],
    "responsive_measures": ["string"],
    "proactive_measures": ["string"],
    "potential_risks": ["string"],
    "next_steps": ["string"]
  },
  "strategic_objectives": ["string — 4 items"],
  "key_initiatives": ["string — 4 items"],
  "landing_zones": {
    "retail": { "onboarding": bool, "servicing": bool, "loan_origination": bool, "investing": bool, "assist_engage": bool },
    "sme": { "onboarding": bool, "servicing": bool, "loan_origination": bool, "investing": bool, "assist_engage": bool },
    "commercial": { "onboarding": bool, "servicing": bool, "loan_origination": bool, "investing": bool, "assist_engage": bool },
    "wealth": { "onboarding": bool, "servicing": bool, "loan_origination": bool, "investing": bool, "assist_engage": bool }
  },
  "pov_anchors": [
    { "anchor": "string — one specific dimension where the bank's situation creates a Backbase opening", "evidence": "string — the specific signal, fact, or data point this anchor rests on", "why_now": "string — what makes this a 2026 priority not 2027", "source": "bank_data|inferred" }
  ],
  "key_kpis": [
    { "label": "string", "current": "string", "benchmark": "string", "gap": "string", "source": "bank_data|estimated" }
  ],
  "roadmap": [
    { "initiative": "string", "h1_2026": "string or empty", "h2_2026": "string or empty", "h1_2027": "string or empty", "h2_2027": "string or empty", "h1_2028": "string or empty", "arr_potential": "string" }
  ],
  "three_year_arr": { "h1_2026": "string", "h2_2026": "string", "h1_2027": "string", "h2_2027": "string", "h1_2028": "string" },
  "engagement_plan": [
    { "category": "Value Consulting|Solutions Engineering|Field Marketing|Alliance Partner|Fintech Add-on", "activity": "string", "month": "Jan|Feb|...|Dec", "status": "planned|confirmed|completed" }
  ],
  "business_overview": {
    "key_facts": [
      { "fact": "string — discrete factual claim", "source": "string — where this came from", "source_date": "YYYY-MM-DD or empty", "confidence_tier": 1, "category": "scale|operations|strategy|technology|leadership|risk" }
    ],
    "today_vs_ambition": [
      { "dimension": "string", "today": "string", "ambition": "string" }
    ]
  },
  "stakeholder_map": {
    "executive_sponsor": [{ "name": "string", "title": "string" }],
    "budget_owner": [{ "name": "string", "title": "string" }],
    "operational": [{ "name": "string", "title": "string" }],
    "key_influencer": [{ "name": "string", "title": "string" }],
    "business_sponsor": [{ "name": "string", "title": "string" }],
    "external_allies": [{ "name": "string", "title": "string" }]
  },
  "confidence_flags": {
    "account_snapshot": "high|medium|low",
    "roadmap": "high|medium|low",
    "kpis": "high|medium|low",
    "stakeholder_map": "high|medium|low"
  }
}

RULES:
- strategic_initiatives: Map EVERY pain point from the bank data to a strategic initiative. Do not skip any pain points — if the bank has 5 pain points, produce 5 strategic initiatives. Each initiative must trace back to a specific pain point from the data.
- pov_anchors: 3-5 STRUCTURED anchors. Each anchor is one specific dimension where the bank's situation creates a Backbase opening. NO prose narrative. NO editorial commentary. NO multi-sentence summaries. Just discrete anchors with evidence + why-now + source.
- business_overview.key_facts: 5-8 discrete factual claims about the bank, each with a source and confidence tier. NO prose paragraph descriptions. If a fact lacks a source, mark confidence_tier = 3 (estimated). Categories: scale, operations, strategy, technology, leadership, risk.
- landing_zones: set true ONLY for zones where the bank data shows genuine fit
- roadmap: 3-5 initiatives phased realistically across H1/H2 periods
- engagement_plan: 8-12 activities across all categories, spread across months. Each activity that references a person MUST use a real name from the Key People list provided.
- stakeholder_map: assign ONLY real persons from the provided Key People list. For "external_allies", use partner firms mentioned in the Competition/Vendors data (e.g., system integrators, consulting partners). Do NOT assign internal bank employees to external_allies — that category is for outside partners, consultants, and SI firms who could support the deal. If no partners are known, set external_allies to an empty array.
- key_kpis: 4-6 KPIs. For each KPI, add a "source" field: "bank_data" if the current value comes from the provided operational profile or CX data, or "estimated" if you inferred it. Example: { "label": "Cost-to-Income", "current": "46%", "benchmark": "40%", "gap": "6%", "source": "bank_data" }. NEVER present an estimated value as if it came from the bank's data.
- confidence_flags: high = based on verified data, medium = inferred from partial data, low = estimated
- ABSOLUTE: NO prose narrative anywhere. No "story arc," no "executive summary," no editorial framing. If you find yourself writing a paragraph of prose, stop and convert it into structured fields.`;

    // Pack C: validated-facts injection
    const validatedFactsBlockAP = getValidatedFactsBlockForBank(db, bankKey);

    const userPrompt = `Bank: ${bankRow.bank_name} (${bankRow.country})
Manual inputs: ${JSON.stringify(manualInputs || {})}

${validatedFactsBlockAP ? validatedFactsBlockAP + '\n\n' : ''}Bank Overview: ${(bd.overview || '').substring(0, 800)}
Operational Profile: ${JSON.stringify(bd.operational_profile || {})}
Digital Strategy: ${typeof bd.digital_strategy === 'string' ? bd.digital_strategy.substring(0, 400) : ''}
Strategic Initiatives: ${typeof bd.strategic_initiatives === 'string' ? bd.strategic_initiatives.substring(0, 400) : ''}

Pain Points:
${(bd.pain_points || []).slice(0, 6).map(p => `- ${p.title}: ${p.detail}`).join('\n')}

Signals:
${(bd.signals || []).slice(0, 6).map(s => `- ${s.signal}: ${s.implication}`).join('\n')}

Landing Zones:
${(bd.backbase_landing_zones || []).map(z => `- ${z.zone} (${z.fit_score}/10): ${z.rationale}`).join('\n')}

Value Hypothesis: ${vs?.value_hypothesis?.one_liner || 'Not defined'}
IF: ${vs?.value_hypothesis?.if_condition || 'N/A'}
THEN: ${vs?.value_hypothesis?.then_outcome || 'N/A'}
BY: ${vs?.value_hypothesis?.by_deploying || 'N/A'}
RESULT: ${vs?.value_hypothesis?.resulting_in || 'N/A'}

Qualification: ${qd ? Object.entries(qd).map(([k, v]) => `${k}: ${v.score}/10 — ${v.note}`).join('\n') : 'Not scored'}

Deal Context: ${bd.backbase_qualification ? `Type: ${bd.backbase_qualification.bank_type || 'N/A'}, Deal: ${bd.backbase_qualification.deal_size || 'N/A'}, Cycle: ${bd.backbase_qualification.sales_cycle || 'N/A'}, Timing: ${bd.backbase_qualification.timing || 'N/A'}` : 'N/A'}

Competition: ${comp ? `Core: ${comp.core_banking || 'N/A'}, Digital: ${comp.digital_platform || 'N/A'}, Vendors: ${(comp.key_vendors || []).join(', ')}` : 'N/A'}

CX: ${cxRow ? `iOS: ${cxRow.app_rating_ios || 'N/A'}, Android: ${cxRow.app_rating_android || 'N/A'}` : 'N/A'}

Key People (${persons.length}):
${persons.slice(0, 12).map(p => `- ${p.canonical_name} | ${p.role} | ${p.role_category || 'N/A'}${p.note ? ' | ' + p.note.substring(0, 60) : ''}`).join('\n')}

Recommended Approach: ${(bd.recommended_approach || '').substring(0, 300)}

Generate the complete account plan JSON now.`;

    try {
      const raw = await callClaude(systemPrompt, userPrompt, { maxTokens: 6000, timeout: 120000 });
      const cleaned = raw.replace(/```json\n?|\n?```/g, '').trim();
      const result = JSON.parse(cleaned);
      // Cache the result in SQLite
      const planId = crypto.randomUUID();
      db.prepare('DELETE FROM account_plans WHERE bank_key = ?').run(bankKey); // Only keep latest
      db.prepare('INSERT INTO account_plans (id, bank_key, inputs, result) VALUES (?, ?, ?, ?)').run(
        planId, bankKey, JSON.stringify(manualInputs || {}), JSON.stringify(result)
      );
      console.log(`   ✅ Account Plan Doc complete (cached as ${planId.slice(0, 8)})`);
      jsonResponse(res, 200, { result, cached: false });
    } catch (err) {
      console.error(`   ❌ Account Plan Doc failed: ${err.message}`);
      jsonResponse(res, 500, { error: 'Account plan generation failed: ' + err.message });
    }
    return true;
  }

  // ── GET /api/conversation-intelligence — Cross-meeting pattern analysis ──
  if (path === '/api/conversation-intelligence' && req.method === 'GET') {
    const meetings = db.prepare("SELECT bank_key, meeting_date, attendees, key_topics, objections_raised, commitments_made, outcome FROM meeting_history WHERE meeting_type = 'client' ORDER BY meeting_date DESC LIMIT 50").all();

    if (meetings.length < 3) {
      jsonResponse(res, 200, { insights: [], message: 'Need at least 3 client meetings for pattern analysis', meetingCount: meetings.length });
      return true;
    }

    // Parse JSON fields
    const parsed = meetings.map(m => ({
      ...m,
      attendees: m.attendees ? JSON.parse(m.attendees) : [],
      key_topics: m.key_topics ? JSON.parse(m.key_topics) : [],
      objections_raised: m.objections_raised ? JSON.parse(m.objections_raised) : [],
      commitments_made: m.commitments_made ? JSON.parse(m.commitments_made) : [],
    }));

    // Pattern 1: Outcome by attendee role
    const roleOutcomes = {};
    parsed.forEach(m => {
      const roles = m.attendees.map(a => a.role || 'Unknown').filter(Boolean);
      roles.forEach(role => {
        if (!roleOutcomes[role]) roleOutcomes[role] = { progressed: 0, stalled: 0, total: 0 };
        roleOutcomes[role][m.outcome] = (roleOutcomes[role][m.outcome] || 0) + 1;
        roleOutcomes[role].total++;
      });
    });

    // Pattern 2: Most common objections
    const objectionCounts = {};
    parsed.forEach(m => {
      m.objections_raised.forEach(obj => {
        const key = typeof obj === 'string' ? obj.toLowerCase().substring(0, 50) : String(obj).toLowerCase().substring(0, 50);
        objectionCounts[key] = (objectionCounts[key] || 0) + 1;
      });
    });
    const topObjections = Object.entries(objectionCounts).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([obj, count]) => ({ objection: obj, count }));

    // Pattern 3: Topic effectiveness (topics in progressed vs stalled meetings)
    const topicOutcomes = {};
    parsed.forEach(m => {
      m.key_topics.forEach(topic => {
        const key = typeof topic === 'string' ? topic.toLowerCase() : String(topic).toLowerCase();
        if (!topicOutcomes[key]) topicOutcomes[key] = { progressed: 0, stalled: 0, total: 0 };
        topicOutcomes[key][m.outcome] = (topicOutcomes[key][m.outcome] || 0) + 1;
        topicOutcomes[key].total++;
      });
    });

    // Pattern 4: Commitment fulfillment rate
    let totalCommitments = 0;
    let fulfilledCommitments = 0;
    parsed.forEach(m => {
      m.commitments_made.forEach(c => {
        totalCommitments++;
        if (c.fulfilled) fulfilledCommitments++;
      });
    });

    // Build insights
    const insights = [];

    // Win rate
    const progressed = parsed.filter(m => m.outcome === 'progressed').length;
    const total = parsed.length;
    insights.push({
      type: 'win_rate',
      title: 'Meeting Progression Rate',
      value: Math.round((progressed / total) * 100) + '%',
      detail: `${progressed} of ${total} meetings progressed the deal forward`,
    });

    // Commitment rate
    if (totalCommitments > 0) {
      insights.push({
        type: 'commitment_rate',
        title: 'Commitment Fulfillment',
        value: Math.round((fulfilledCommitments / totalCommitments) * 100) + '%',
        detail: `${fulfilledCommitments} of ${totalCommitments} commitments fulfilled`,
      });
    }

    // Top objections
    if (topObjections.length > 0) {
      insights.push({
        type: 'objections',
        title: 'Most Common Objections',
        items: topObjections,
        detail: 'Prepare responses for these recurring objections',
      });
    }

    // Role effectiveness
    const roleInsights = Object.entries(roleOutcomes)
      .filter(([, data]) => data.total >= 2)
      .map(([role, data]) => ({
        role,
        progressRate: data.total > 0 ? Math.round((data.progressed / data.total) * 100) : 0,
        total: data.total,
      }))
      .sort((a, b) => b.progressRate - a.progressRate);

    if (roleInsights.length > 0) {
      insights.push({
        type: 'role_effectiveness',
        title: 'Meeting Outcomes by Attendee Role',
        items: roleInsights.slice(0, 5),
        detail: 'Roles with highest meeting progression rates',
      });
    }

    jsonResponse(res, 200, { insights, meetingCount: total });
    return true;
  }

  // ── POST /api/research/battlecard — Generate context-specific competitive battlecard ──
  if (path === '/api/research/battlecard' && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isClaudeAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured.' });
      return true;
    }
    const { bankKey, competitor } = await parseBody(req);
    if (!bankKey || !competitor) {
      jsonResponse(res, 400, { error: 'Missing bankKey or competitor' });
      return true;
    }

    const bankRow = db.prepare('SELECT bank_name, data FROM banks WHERE key = ?').get(bankKey);
    if (!bankRow) { jsonResponse(res, 404, { error: 'Bank not found' }); return true; }
    const bd = JSON.parse(bankRow.data || '{}');
    const compRow = db.prepare('SELECT data FROM competition WHERE bank_key = ?').get(bankKey);
    const comp = compRow ? JSON.parse(compRow.data) : null;

    // Win/loss data against this competitor
    const outcomes = db.prepare("SELECT outcome, lessons_learned FROM deal_outcomes WHERE competitor_won = ? OR bank_key IN (SELECT bank_key FROM competition WHERE data LIKE ?)").all(competitor, `%${competitor}%`);

    console.log(`⚔️ Battlecard: ${competitor} at ${bankRow.bank_name}`);

    const systemPrompt = `You are a senior competitive strategist at Backbase, the AI-native Banking OS / AI-Powered Banking Platform vendor. Generate a battlecard for competing against ${competitor} at ${bankRow.bank_name}.

${BACKBASE_2026_CONTEXT}

Position our advantages using current product framing — Banking OS as the Control Plane above cores, APA + CLO + segment OSes (Wealth OS / Commercial OS / Small Business OS / Private Banking OS / Retail OS), Decision Token governance, Elastic Operations outcome, and the three commercial entry points (Conversational Banking, Agentic Servicing, Agentic Onboarding & Origination).

Return ONLY valid JSON:
{
  "competitor_overview": "2-3 sentences about the competitor's positioning and typical approach",
  "their_strengths": ["3-4 genuine strengths — be honest, not dismissive"],
  "their_weaknesses": ["3-4 real weaknesses that matter for this specific bank"],
  "our_advantages": ["3-4 Backbase advantages that directly counter their weaknesses"],
  "landmines": ["2-3 questions to plant that expose their weaknesses without being obvious"],
  "trap_questions": ["2-3 questions the competitor will try to use against us, with suggested responses"],
  "win_strategy": "2-3 sentence strategy for winning against this competitor at this specific bank",
  "killer_fact": "One specific, verifiable data point that undermines the competitor's position"
}

Be specific to THIS bank. Generic competitive talking points are useless. Reference the bank's actual pain points and how each competitor's approach fails to address them.`;

    // Pack C: validated-facts injection
    const validatedFactsBlockBC = getValidatedFactsBlockForBank(db, bankKey);

    const userPrompt = `Bank: ${bankRow.bank_name}
Competitor: ${competitor}
${validatedFactsBlockBC ? '\n' + validatedFactsBlockBC + '\n' : ''}Bank pain points: ${(bd.pain_points || []).map(p => p.title + ': ' + p.detail).join('\n')}
Current vendors: ${comp ? `Core: ${comp.core_banking}, Digital: ${comp.digital_platform}, Vendors: ${(comp.key_vendors || []).join(', ')}` : 'Unknown'}
Vendor risk: ${comp?.vendor_risk || 'Unknown'}
${outcomes.length > 0 ? 'Win/loss history against this competitor:\n' + outcomes.map(o => `${o.outcome}: ${o.lessons_learned || 'No notes'}`).join('\n') : ''}`;

    try {
      const raw = await callClaude(systemPrompt, userPrompt, { maxTokens: 2000, timeout: 45000 });
      const cleaned = raw.replace(/```json\n?|\n?```/g, '').trim();
      const result = JSON.parse(cleaned);
      console.log(`   ✅ Battlecard complete`);
      jsonResponse(res, 200, { result, competitor, bankName: bankRow.bank_name });
    } catch (err) {
      console.error(`   ❌ Battlecard failed: ${err.message}`);
      jsonResponse(res, 500, { error: 'Battlecard generation failed: ' + err.message });
    }
    return true;
  }

  // ── GET /api/competitive-landscape — Cross-deal competitor frequency ──
  if (path === '/api/competitive-landscape' && req.method === 'GET') {
    const banks = db.prepare('SELECT key, bank_name, data FROM banks').all();
    const competitorFrequency = {};

    for (const bank of banks) {
      const compRow = db.prepare('SELECT data FROM competition WHERE bank_key = ?').get(bank.key);
      if (!compRow) continue;
      const comp = JSON.parse(compRow.data || '{}');
      const vendors = [comp.core_banking, comp.digital_platform, ...(comp.key_vendors || [])].filter(Boolean);
      for (const v of vendors) {
        const name = v.trim();
        if (!name || name === 'N/A' || name.toLowerCase().includes('in-house')) continue;
        if (!competitorFrequency[name]) competitorFrequency[name] = { name, count: 0, banks: [] };
        competitorFrequency[name].count++;
        competitorFrequency[name].banks.push(bank.bank_name);
      }
    }

    const sorted = Object.values(competitorFrequency).sort((a, b) => b.count - a.count);

    // Win/loss by competitor
    const outcomes = db.prepare("SELECT competitor_won, outcome FROM deal_outcomes WHERE competitor_won IS NOT NULL").all();
    const winLoss = {};
    outcomes.forEach(o => {
      if (!winLoss[o.competitor_won]) winLoss[o.competitor_won] = { wins: 0, losses: 0 };
      if (o.outcome === 'won') winLoss[o.competitor_won].wins++;
      else if (o.outcome === 'lost') winLoss[o.competitor_won].losses++;
    });

    jsonResponse(res, 200, { competitors: sorted.slice(0, 15), winLoss });
    return true;
  }

  // ── POST /api/research/meeting-deck — DEPRECATED 2026-04 ──
  // Strategic Repositioning Sprint 0.2: Nova does not produce prospect-facing
  // presentation decks. Brief forbids "POV one-pagers, narrative decks,
  // persuasive collateral."
  //
  // Endpoint stays alive for 30 days (until 2026-05-28) for any in-flight
  // integration. Returns deprecation headers + console warning. Hard delete
  // after 2026-05-28.
  //
  // Replacement: AEs take the structured intelligence (MeetingPrepBrief
  // strategicPriorities, attendees, topicInsights) and build their own deck
  // in PowerPoint/Keynote/Claude-in-a-chat.
  if (path === '/api/research/meeting-deck' && req.method === 'POST') {
    res.setHeader('Deprecation', 'true');
    res.setHeader('Sunset', 'Wed, 28 May 2026 00:00:00 GMT');
    res.setHeader('Link', '</docs/strategic-repositioning>; rel="deprecation"');
    console.warn('[deprecated] /api/research/meeting-deck called — Nova does not produce prospect-facing decks. Hard delete scheduled 2026-05-28.');
    if (!aiRateCheck(res)) return true;
    if (!isClaudeAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured.' });
      return true;
    }
    const { bankKey, attendees, topics } = await parseBody(req);
    if (!bankKey) { jsonResponse(res, 400, { error: 'Missing bankKey' }); return true; }

    const bankRow = db.prepare('SELECT bank_name, country, data FROM banks WHERE key = ?').get(bankKey);
    if (!bankRow) { jsonResponse(res, 404, { error: 'Bank not found' }); return true; }
    const bd = JSON.parse(bankRow.data || '{}');
    const vsRow = db.prepare('SELECT data FROM value_selling WHERE bank_key = ?').get(bankKey);
    const vs = vsRow ? JSON.parse(vsRow.data) : null;

    console.log(`🎬 Meeting deck: ${bankRow.bank_name}`);

    const systemPrompt = `You are a senior Value Consultant at Backbase, the AI-native Banking OS / AI-Powered Banking Platform vendor, creating a 5-slide meeting deck for a client meeting at ${bankRow.bank_name}. Each slide must be specific, insightful, and demonstrate deep understanding of the bank.

${BACKBASE_2026_CONTEXT}

Use current product framing throughout: Banking OS, APA, CLO, segment OSes (Wealth/Commercial/Small Business/Private Banking/Retail OS); Operational Layers (Nexus/Sentinel/Grand Central/Process Studio/Agent Studio/Intelligence); proof-point ranges (30-40% cost-to-serve, 50-90% faster execution, 3x productivity, 2-4x growth); and the three commercial entry points where they fit the meeting's purpose.

Return ONLY valid JSON with this structure:
{
  "slides": [
    {
      "title": "string",
      "subtitle": "string",
      "bullets": ["string — 3-4 per slide"],
      "speaker_notes": "string — 2-3 sentences of what to SAY when presenting this slide"
    }
  ]
}

The 5 slides MUST follow this structure:
1. "What We Know About [Bank]" — proves you did research. Reference specific KPIs, strategic priorities, recent events.
2. "The Challenge We See" — the specific pain point most relevant to the attendees. Be precise, not generic.
3. "How Others Have Solved It" — reference customers and outcomes. Real numbers where available.
4. "What We'd Propose" — specific Backbase solution mapped to their needs. Landing zone + products.
5. "What Success Looks Like" — quantified outcomes, timeline, next steps.

Each bullet must be specific to THIS bank. No generic fintech platitudes.`;

    const attendeeContext = attendees?.length > 0
      ? `Attendees: ${attendees.map(a => `${a.name || 'Unknown'} (${a.role || a.roleKey || 'Unknown role'})`).join(', ')}`
      : '';

    // Pack C: validated-facts injection
    const validatedFactsBlockMD = getValidatedFactsBlockForBank(db, bankKey);

    const userPrompt = `Bank: ${bankRow.bank_name} (${bankRow.country})
${attendeeContext}
${validatedFactsBlockMD ? '\n' + validatedFactsBlockMD : ''}
${topics?.length > 0 ? 'Topics: ' + topics.join(', ') : ''}

Bank overview: ${(bd.overview || '').substring(0, 400)}
Pain points: ${(bd.pain_points || []).slice(0, 4).map(p => p.title + ': ' + p.detail).join('\n')}
Landing zones: ${(bd.backbase_landing_zones || []).slice(0, 3).map(z => z.zone + ' (' + z.fit_score + '/10): ' + z.rationale).join('\n')}
Value hypothesis: ${vs?.value_hypothesis?.one_liner || 'Not defined'}
Reference customers: ${(vs?.reference_customers || []).slice(0, 3).map(r => r.name + ' (' + r.region + '): ' + r.relevance).join('\n') || 'None'}
Key people: ${(bd.key_decision_makers || []).filter(k => k.name && !k.name.startsWith('(')).slice(0, 5).map(k => k.name + ' — ' + k.role).join(', ')}
Recent signals: ${(bd.signals || []).slice(0, 3).map(s => s.signal).join(', ')}`;

    try {
      const raw = await callClaude(systemPrompt, userPrompt, { maxTokens: 2000, timeout: 45000 });
      const cleaned = raw.replace(/```json\n?|\n?```/g, '').trim();
      const result = JSON.parse(cleaned);
      console.log(`   ✅ Meeting deck complete (${result.slides?.length || 0} slides)`);
      jsonResponse(res, 200, { result });
    } catch (err) {
      console.error(`   ❌ Meeting deck failed: ${err.message}`);
      jsonResponse(res, 500, { error: 'Meeting deck generation failed: ' + err.message });
    }
    return true;
  }

  // ══════════════════════════════════════════════════════════════
  // INTELLIGENCE LAYER — Play Generation + Deal Twin Recalculation
  // ══════════════════════════════════════════════════════════════

  // ── POST /api/deals/:dealId/plays/regenerate-stale — Prepare stale plays for re-generation ──
  // Finds all active plays in the deal that have ≥1 stale output, deletes the stale outputs,
  // and returns the play IDs the client should sequentially POST to /generate.
  // (We don't AI-generate here because it would block for minutes; the client orchestrates
  //  the loop and shows per-play progress.)
  const bulkRegenMatch = path.match(/^\/api\/deals\/([^/]+)\/plays\/regenerate-stale$/);
  if (bulkRegenMatch && req.method === 'POST') {
    const dealId = decodeURIComponent(bulkRegenMatch[1]);
    const stalePlays = db.prepare(`
      SELECT DISTINCT dp.id, dp.play_type
      FROM deal_plays dp
      JOIN play_outputs po ON po.play_id = dp.id
      WHERE dp.deal_id = ? AND dp.status = 'active' AND po.confidence_tier = 'stale'
      ORDER BY dp.created_at ASC
    `).all(dealId);

    let deletedCount = 0;
    const deleteStmt = db.prepare("DELETE FROM play_outputs WHERE play_id = ? AND confidence_tier = 'stale'");
    for (const p of stalePlays) {
      const r = deleteStmt.run(p.id);
      deletedCount += r.changes;
    }

    jsonResponse(res, 200, {
      plays_to_regenerate: stalePlays.map(p => ({ play_id: p.id, play_type: p.play_type })),
      stale_outputs_deleted: deletedCount,
      message: stalePlays.length === 0
        ? 'No stale plays found.'
        : `Cleared ${deletedCount} stale outputs. Call /generate for each play_id to refresh.`,
    });
    return true;
  }

  // ── POST /api/deals/:dealId/plays/:playId/generate — AI-generate play outputs ──
  const playGenMatch = path.match(/^\/api\/deals\/([^/]+)\/plays\/([^/]+)\/generate$/);
  if (playGenMatch && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isClaudeAvailable()) { jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured.' }); return true; }

    const dealId = decodeURIComponent(playGenMatch[1]);
    const playId = decodeURIComponent(playGenMatch[2]);

    const play = db.prepare('SELECT * FROM deal_plays WHERE id = ?').get(playId);
    if (!play) { jsonResponse(res, 404, { error: 'Play not found' }); return true; }

    // Gather deal context
    const bankRow = db.prepare('SELECT bank_name, country, data FROM banks WHERE key = ?').get(dealId);
    if (!bankRow) { jsonResponse(res, 404, { error: 'Bank/deal not found' }); return true; }
    const bd = JSON.parse(bankRow.data || '{}');
    const persons = db.prepare('SELECT canonical_name, role, role_category, note FROM persons WHERE bank_key = ? ORDER BY role_category').all(dealId);
    const meetings = db.prepare("SELECT meeting_date, outcome, key_topics, objections_raised FROM meeting_history WHERE bank_key = ? AND meeting_type = 'client' ORDER BY meeting_date DESC LIMIT 5").all(dealId);
    const vsRow = db.prepare('SELECT data FROM value_selling WHERE bank_key = ?').get(dealId);
    const vs = vsRow ? JSON.parse(vsRow.data) : null;
    const compRow = db.prepare('SELECT data FROM competition WHERE bank_key = ?').get(dealId);
    const comp = compRow ? JSON.parse(compRow.data) : null;
    const signals = db.prepare('SELECT title, signal_category, severity FROM deal_signals WHERE deal_id = ? ORDER BY detected_at DESC LIMIT 10').all(dealId);

    // Build context strings
    const stakeholderCtx = persons.slice(0, 10).map(p => `- ${p.canonical_name} (${p.role}): ${p.note || 'No notes'}`).join('\n');
    const meetingCtx = meetings.map(m => {
      const topics = m.key_topics ? JSON.parse(m.key_topics).join(', ') : 'N/A';
      const objections = m.objections_raised ? JSON.parse(m.objections_raised).join('; ') : '';
      return `- ${m.meeting_date}: ${m.outcome || 'N/A'} — Topics: ${topics}${objections ? ' — Objections: ' + objections : ''}`;
    }).join('\n');
    const signalCtx = signals.map(s => `- [${s.severity}] ${s.title}`).join('\n');

    // Gather outputs from OTHER plays on this deal (cross-play context)
    const otherPlays = db.prepare("SELECT id, play_type FROM deal_plays WHERE deal_id = ? AND id != ? AND status IN ('active', 'completed')").all(dealId, playId);
    let crossPlayCtx = '';
    for (const op of otherPlays) {
      const outputs = db.prepare('SELECT output_type, title, content FROM play_outputs WHERE play_id = ? LIMIT 3').all(op.id);
      if (outputs.length > 0) {
        crossPlayCtx += `\n--- From ${op.play_type} play ---\n`;
        outputs.forEach(o => { crossPlayCtx += `[${o.output_type}] ${o.title}: ${(o.content || '').substring(0, 300)}...\n`; });
      }
    }

    // Gather feedback from previous outputs (what worked, what didn't)
    const feedbackCtx = db.prepare(`
      SELECT po.output_type, po.title, po.feedback, of.notes
      FROM play_outputs po LEFT JOIN output_feedback of ON of.play_output_id = po.id
      WHERE po.play_id IN (SELECT id FROM deal_plays WHERE deal_id = ?) AND po.feedback IS NOT NULL
      LIMIT 10
    `).all(dealId).map(f => `- ${f.output_type} "${f.title}": ${f.feedback}${f.notes ? ' — ' + f.notes : ''}`).join('\n');

    // Play-type-specific system prompts (enhanced with spec templates)
    const PLAY_PROMPTS = {
      discovery: {
        system: `You are Nova, a B2B sales intelligence assistant for Backbase value consultants. Backbase is the AI-native Banking OS / AI-Powered Banking Platform vendor.

${BACKBASE_2026_CONTEXT}

You generate highly specific, research-backed discovery guides — never generic sales questions. Every question must reference something specific we know about the bank or stakeholder. Questions should uncover information gaps, validate hypotheses, and advance the deal. Frame Backbase value using current product names (Banking OS, APA, CLO, segment OSes) and the three commercial entry points.`,
        instruction: `Generate discovery outputs:
1. A DISCOVERY GUIDE with 3-5 specific questions per stakeholder. Each question must:
   - Reference something specific we know about the bank or stakeholder
   - Target a specific information gap we need to fill
   - Be framed as a consultative question (not interrogation)
2. A STAKEHOLDER BRIEF per person: role, known priorities, communication approach, what they care about mapped to Backbase value props
3. CROSS-CUTTING QUESTIONS that apply to multiple stakeholders
4. HYPOTHESES TO VALIDATE — 3-5 assumptions we're making that need confirmation`,
      },
      value: {
        system: `You are Nova, building a business case framework for a Backbase deal. Backbase is the AI-native Banking OS / AI-Powered Banking Platform vendor.

${BACKBASE_2026_CONTEXT}

Every value claim must be connected to a specific stakeholder priority confirmed in meetings or inferred from bank data. Use conservative estimates and cite proof-point ranges (30-40% cost-to-serve, 50-90% faster execution, 3x productivity, 2-4x growth) when they apply. Map drivers to current product names (Banking OS, APA, CLO, segment OSes).`,
        instruction: `Generate value outputs:
1. A VALUE FRAMEWORK with:
   - Value drivers mapped to specific stakeholders who care about them
   - Benchmark ranges from similar banks (size, segment, geography)
   - Conservative / base / optimistic scenarios
   - Data points still needed from the bank to sharpen the case
2. STAKEHOLDER-SPECIFIC VALUE NARRATIVES — for each key decision-maker, 2-3 paragraphs connecting their stated priority to a specific Backbase capability to a specific financial outcome
3. PEER BANK EVIDENCE — reference customers matched to this deal's context
${crossPlayCtx ? '\nINSIGHTS FROM DISCOVERY PLAY:\n' + crossPlayCtx : ''}`,
      },
      competitive: {
        system: `You are Nova, generating deal-specific competitive intelligence for Backbase, the AI-native Banking OS / AI-Powered Banking Platform vendor.

${BACKBASE_2026_CONTEXT}

Not generic battlecards — specific to what THIS bank cares about and what THIS competitor's weaknesses are in this context. Anchor differentiation to current Backbase product framing: Banking OS as Control Plane above cores, APA + CLO + segment OSes, Decision Token governance, Elastic Operations outcome.`,
        instruction: `Generate competitive outputs:
1. COMPETITIVE BRIEF — deal-specific positioning: where we win, where we need to address concerns, recommended framing for each stakeholder
2. OBJECTION MAP — anticipated objections based on competitive context, each tied to a specific stakeholder concern, with recommended responses
3. DIFFERENTIATION TALKING POINTS — 3-5 crisp statements connecting Backbase's unique capabilities to this bank's specific needs in a way the competitor cannot match
4. LANDMINE QUESTIONS — 2-3 questions to ask the bank that subtly expose competitor weaknesses
${comp ? '' : '\nNOTE: No specific competitors identified. Analyze based on common competitive patterns for this bank segment. Flag that competitor-specific intelligence would improve this analysis.'}`,
      },
      // Strategic Repositioning Sprint 0.3 — proposal play refactored from
      // "narrative generator" to "deal-readiness intelligence assembler."
      // The brief forbids prose proposal collateral. The play now produces
      // STRUCTURED INTELLIGENCE the AE uses to build the proposal in their
      // own writing tool of choice.
      //
      // REMOVED outputs: PROPOSAL NARRATIVE, EXECUTIVE SUMMARY DRAFT.
      // KEPT outputs:    RISK REGISTER, PER-STAKEHOLDER PROOF POINTS.
      // ADDED outputs:   BUYER-READINESS MATRIX, OPEN-CRITERIA REGISTER,
      //                  PRE-PROPOSAL CHECKLIST.
      proposal: {
        system: `You are Nova, assembling deal-readiness intelligence for the AE who is preparing to write a proposal. You do NOT write the proposal narrative — that is the AE's job. Your output is the structured set of facts, gaps, and risks they need to write a defensible proposal.

${BACKBASE_2026_CONTEXT}

You have access to outputs from discovery, value, and competitive plays. Surface what is known, what is unknown, and what the AE must validate before sending a proposal. Use current product framing where relevant (Banking OS, APA, CLO, segment OSes), but do NOT compose persuasive prose.`,
        instruction: `Generate STRUCTURED proposal-readiness intelligence (no prose narrative — return JSON-friendly structured data):

1. BUYER-READINESS MATRIX — for each named decision-maker: { name, role, position (champion/coach/blocker/skeptic/unknown), readiness_state (engaged/aware/cold), open_question, evidence }. Be honest about "unknown" — guesses without evidence are blockers, not readiness.

2. OPEN-CRITERIA REGISTER — what the bank's evaluation criteria actually are (only what we have evidence for from discovery), and what's still unknown. Each criterion: { criterion, status (validated/inferred/unknown), source }.

3. RISK REGISTER — what could derail this deal: stakeholder gaps, competitive threats, timing risks, missing information. Each risk: { risk, severity (high/medium/low), mitigation_action, owner }.

4. PER-STAKEHOLDER PROOF POINTS — for each key decision-maker: the single strongest evidence point we can cite to them, with source. Format: { stakeholder, proof_point, source, source_date, confidence_tier }.

5. PRE-PROPOSAL CHECKLIST — the discrete validation gates the AE should close before sending a proposal: { gate, status (closed/open), action_to_close }. Examples: "Power-map confirmed with champion," "Pricing benchmark validated," "Reference customer matched."

DO NOT produce: executive summary prose, story-arc narrative, persuasive copy, or any text addressed to a prospect. The AE writes those.${crossPlayCtx ? '\n\nFROM OTHER PLAYS:\n' + crossPlayCtx : ''}`,
      },
      expansion: {
        system: `You are Nova, analyzing expansion opportunities for an existing Backbase customer. Backbase is the AI-native Banking OS / AI-Powered Banking Platform vendor.

${BACKBASE_2026_CONTEXT}

Map expansion paths to current product additions (e.g., adding APA on top of Banking OS, adopting CLO, layering a segment OS like Wealth OS / Commercial OS / Small Business OS / Private Banking OS / Retail OS, or unlocking a new commercial entry point — Conversational Banking, Agentic Servicing, Agentic Onboarding & Origination).`,
        instruction: `Generate expansion outputs:
1. EXPANSION MAP — current product footprint vs. available Backbase capabilities, prioritized by fit and timing
2. UPSELL BUSINESS CASE — specific to the expansion opportunity, using customer's own metrics where available
3. RE-ENGAGEMENT BRIEF — who's new since last engagement, what's changed, recommended approach and timing`,
      },
    };

    const playPrompt = PLAY_PROMPTS[play.play_type] || PLAY_PROMPTS.discovery;

    console.log(`🎭 Play generation: ${play.play_type} for ${bankRow.bank_name} (cross-play context: ${otherPlays.length} plays)`);

    const userPrompt = `Deal: ${bankRow.bank_name} (${bankRow.country})
Play type: ${play.play_type}

BANK PROFILE:
${(bd.overview || '').substring(0, 500)}
Operational: ${JSON.stringify(bd.operational_profile || {}).substring(0, 200)}

PAIN POINTS:
${(bd.pain_points || []).slice(0, 5).map(p => `- ${p.title}: ${p.detail}`).join('\n') || 'None identified'}

VALUE HYPOTHESIS: ${vs?.value_hypothesis?.one_liner || 'Not defined'}
IF: ${vs?.value_hypothesis?.if_condition || 'N/A'}
THEN: ${vs?.value_hypothesis?.then_outcome || 'N/A'}

STAKEHOLDERS:
${stakeholderCtx || 'None identified'}

MEETING HISTORY:
${meetingCtx || 'No meetings yet'}

RECENT SIGNALS:
${signalCtx || 'None'}

COMPETITION: ${comp ? `Core: ${comp.core_banking || 'N/A'}, Digital: ${comp.digital_platform || 'N/A'}, Vendors: ${(comp.key_vendors || []).join(', ')}, Risk: ${comp.vendor_risk || 'N/A'}` : 'Unknown'}

LANDING ZONES: ${(bd.backbase_landing_zones || []).map(z => `${z.zone}(${z.fit_score}/10)`).join(', ') || 'None'}

${feedbackCtx ? 'FEEDBACK ON PREVIOUS OUTPUTS (what worked/missed):\n' + feedbackCtx + '\n' : ''}
${playPrompt.instruction}

Return ONLY valid JSON:
{
  "outputs": [
    {
      "output_type": "talking_points|discovery_guide|value_framework|competitive_brief|proposal_narrative|objection_map|stakeholder_brief|deck_section|email_draft",
      "title": "string — descriptive title",
      "content": "string — rich markdown",
      "confidence_tier": "verified|inferred",
      "stakeholder_name": "string or null — if this output targets a specific person"
    }
  ]
}`;

    try {
      const raw = await callClaude(playPrompt.system, userPrompt, { maxTokens: 4000, timeout: 90000 });
      const cleaned = raw.replace(/```json\n?|\n?```/g, '').trim();
      const result = JSON.parse(cleaned);

      // Store outputs in play_outputs table
      const outputIds = [];
      for (const output of (result.outputs || [])) {
        const outputId = crypto.randomUUID();
        db.prepare(`INSERT INTO play_outputs (id, play_id, output_type, title, content, confidence_tier, stakeholder_id)
          VALUES (?, ?, ?, ?, ?, ?, ?)`).run(
          outputId, playId, output.output_type, output.title, output.content,
          output.confidence_tier || 'inferred', output.stakeholder_name || null
        );
        outputIds.push(outputId);
      }

      // Update play timestamp
      db.prepare("UPDATE deal_plays SET updated_at = datetime('now') WHERE id = ?").run(playId);

      console.log(`   ✅ Generated ${outputIds.length} outputs for ${play.play_type} play`);
      jsonResponse(res, 200, { outputs_created: outputIds.length, output_ids: outputIds });
    } catch (err) {
      console.error(`   ❌ Play generation failed: ${err.message}`);
      jsonResponse(res, 500, { error: 'Play generation failed: ' + err.message });
    }
    return true;
  }

  // ── POST /api/deals/:dealId/twin/recalculate — AI-powered deal health calculation ──
  const twinRecalcMatch = path.match(/^\/api\/deals\/([^/]+)\/twin\/recalculate$/);
  if (twinRecalcMatch && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isClaudeAvailable()) { jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured.' }); return true; }

    const dealId = decodeURIComponent(twinRecalcMatch[1]);
    const bankRow = db.prepare('SELECT bank_name, data FROM banks WHERE key = ?').get(dealId);
    if (!bankRow) { jsonResponse(res, 404, { error: 'Bank/deal not found' }); return true; }

    // Gather all deal context for scoring
    const persons = db.prepare('SELECT canonical_name, role FROM persons WHERE bank_key = ?').all(dealId);
    const meetingCount = db.prepare("SELECT COUNT(*) as c FROM meeting_history WHERE bank_key = ? AND meeting_type = 'client'").get(dealId).c;
    const lastMeeting = db.prepare("SELECT meeting_date FROM meeting_history WHERE bank_key = ? AND meeting_type = 'client' ORDER BY meeting_date DESC LIMIT 1").get(dealId);
    const activePlays = db.prepare("SELECT play_type, status FROM deal_plays WHERE deal_id = ? AND status = 'active'").all(dealId);
    const signalCount = db.prepare('SELECT COUNT(*) as c FROM deal_signals WHERE deal_id = ?').get(dealId).c;
    const unackedSignals = db.prepare('SELECT COUNT(*) as c FROM deal_signals WHERE deal_id = ? AND acknowledged_at IS NULL').get(dealId).c;
    const bd = JSON.parse(bankRow.data || '{}');
    const compRow = db.prepare('SELECT data FROM competition WHERE bank_key = ?').get(dealId);
    const comp = compRow ? JSON.parse(compRow.data) : null;
    const prevState = db.prepare('SELECT deal_health_score FROM deal_twin_state WHERE deal_id = ?').get(dealId);

    console.log(`🔮 Deal Twin recalculate: ${bankRow.bank_name}`);

    const systemPrompt = `You are Nova's Deal Twin engine. Score a B2B sales deal's health across 6 dimensions (0-100 each). Be rigorous and evidence-based. Return ONLY valid JSON.`;

    const userPrompt = `Deal: ${bankRow.bank_name}
Stakeholders: ${persons.length} identified (${persons.slice(0, 5).map(p => `${p.canonical_name} — ${p.role}`).join(', ')})
Meetings: ${meetingCount} total, last: ${lastMeeting?.meeting_date || 'never'}
Active plays: ${activePlays.map(p => p.play_type).join(', ') || 'none'}
Signals: ${signalCount} total, ${unackedSignals} unacknowledged
Pain points: ${(bd.pain_points || []).map(p => p.title).join(', ') || 'none'}
Landing zones: ${(bd.backbase_landing_zones || []).map(z => `${z.zone}(${z.fit_score})`).join(', ') || 'none'}
Competition: ${comp ? (comp.key_vendors || []).join(', ') : 'unknown'}
Previous health score: ${prevState?.deal_health_score ?? 'none (first calculation)'}

Score each dimension 0-100:
{
  "stakeholder_alignment": number,
  "strategic_fit": number,
  "competitive_position": number,
  "momentum": number,
  "value_clarity": number,
  "information_completeness": number,
  "deal_health_score": number (weighted average),
  "deal_health_trend": "improving|stable|declining",
  "top_risks": [{"risk": "string", "severity": "high|medium|low", "mitigation": "string"}],
  "recommended_actions": [{"action": "string", "rationale": "string", "priority": "high|medium|low"}]
}`;

    try {
      const raw = await callClaude(systemPrompt, userPrompt, { maxTokens: 2000, timeout: 60000 });
      const cleaned = raw.replace(/```json\n?|\n?```/g, '').trim();
      const result = JSON.parse(cleaned);

      // Upsert deal_twin_state
      db.prepare(`INSERT INTO deal_twin_state (id, deal_id, stakeholder_alignment, strategic_fit, competitive_position, momentum, value_clarity, information_completeness, deal_health_score, deal_health_trend, top_risks, recommended_actions, last_calculated_at, calculation_inputs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?)
        ON CONFLICT(deal_id) DO UPDATE SET
          stakeholder_alignment = excluded.stakeholder_alignment, strategic_fit = excluded.strategic_fit,
          competitive_position = excluded.competitive_position, momentum = excluded.momentum,
          value_clarity = excluded.value_clarity, information_completeness = excluded.information_completeness,
          deal_health_score = excluded.deal_health_score, deal_health_trend = excluded.deal_health_trend,
          top_risks = excluded.top_risks, recommended_actions = excluded.recommended_actions,
          last_calculated_at = datetime('now'), calculation_inputs = excluded.calculation_inputs`).run(
        crypto.randomUUID(), dealId,
        result.stakeholder_alignment, result.strategic_fit, result.competitive_position,
        result.momentum, result.value_clarity, result.information_completeness,
        result.deal_health_score, result.deal_health_trend,
        JSON.stringify(result.top_risks || []), JSON.stringify(result.recommended_actions || []),
        JSON.stringify({ persons: persons.length, meetings: meetingCount, signals: signalCount })
      );

      // Save history snapshot
      db.prepare(`INSERT INTO deal_twin_history (id, deal_id, deal_health_score, stakeholder_alignment, strategic_fit, competitive_position, momentum, value_clarity, information_completeness)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`).run(
        crypto.randomUUID(), dealId, result.deal_health_score,
        result.stakeholder_alignment, result.strategic_fit, result.competitive_position,
        result.momentum, result.value_clarity, result.information_completeness
      );

      console.log(`   ✅ Deal Twin: health score ${result.deal_health_score} (${result.deal_health_trend})`);
      jsonResponse(res, 200, result);
    } catch (err) {
      console.error(`   ❌ Deal Twin recalculation failed: ${err.message}`);
      jsonResponse(res, 500, { error: 'Recalculation failed: ' + err.message });
    }
    return true;
  }

  // ── GET /api/morning-brief — Daily command center aggregation ──
  if (path === '/api/morning-brief' && req.method === 'GET') {
    const banks = db.prepare('SELECT key, bank_name, country, data FROM banks').all();
    const now = Date.now();
    const DAY = 86400000;

    const priorities = [];
    const staleDeals = [];
    const recentSignals = [];
    const upcomingActions = [];

    for (const bank of banks) {
      const bd = JSON.parse(bank.data || '{}');
      const qualRow = db.prepare('SELECT data FROM qualification WHERE bank_key = ?').get(bank.key);
      const qd = qualRow ? JSON.parse(qualRow.data) : null;

      // Calculate score
      let score = 0;
      if (qd) {
        const fw = { firmographics: 0.10, technographics: 0.15, decision_process: 0.10, landing_zones: 0.20, pain_push: 0.20, power_map: 0.15, partner_access: 0.10 };
        for (const [dim, weight] of Object.entries(fw)) {
          if (qd[dim]?.score) score += qd[dim].score * weight;
        }
      }

      // Last meeting date
      const lastMeeting = db.prepare("SELECT meeting_date FROM meeting_history WHERE bank_key = ? AND meeting_type = 'client' ORDER BY meeting_date DESC LIMIT 1").get(bank.key);
      const lastMeetingDate = lastMeeting?.meeting_date ? new Date(lastMeeting.meeting_date) : null;
      const daysSinceContact = lastMeetingDate ? Math.floor((now - lastMeetingDate.getTime()) / DAY) : null;

      // Outstanding commitments
      const meetings = db.prepare("SELECT commitments_made FROM meeting_history WHERE bank_key = ? AND meeting_type = 'client' ORDER BY meeting_date DESC LIMIT 3").all(bank.key);
      let outstandingCommitments = 0;
      for (const m of meetings) {
        const comms = m.commitments_made ? JSON.parse(m.commitments_made) : [];
        outstandingCommitments += comms.filter(c => !c.fulfilled).length;
      }

      // Recent entity changes
      const changes = db.prepare("SELECT field_path, old_value, new_value, changed_at FROM entity_history WHERE entity_key = ? AND changed_at > datetime('now', '-7 days') ORDER BY changed_at DESC LIMIT 3").all(bank.key);

      // Recent live signals (pipeline-detected)
      const signals = db.prepare("SELECT title, relevance_score, fetched_at FROM live_signals WHERE bank_key = ? AND fetched_at > datetime('now', '-7 days') AND relevance_score >= 7 ORDER BY relevance_score DESC LIMIT 2").all(bank.key);

      // Key contacts for action recommendations
      const persons = db.prepare('SELECT canonical_name, role FROM persons WHERE bank_key = ? ORDER BY role_category LIMIT 10').all(bank.key);

      // Infer deal stage
      let dealStage = 'unengaged';
      const hasAccountPlan = !!db.prepare('SELECT 1 FROM account_plans WHERE bank_key = ?').get(bank.key);
      const meetingCount = db.prepare("SELECT COUNT(*) as c FROM meeting_history WHERE bank_key = ? AND meeting_type = 'client'").get(bank.key).c;
      const dealOutcome = db.prepare("SELECT outcome FROM deal_outcomes WHERE bank_key = ? ORDER BY created_at DESC LIMIT 1").get(bank.key);

      if (dealOutcome?.outcome === 'won') dealStage = 'won';
      else if (dealOutcome?.outcome === 'lost') dealStage = 'lost';
      else if (hasAccountPlan) dealStage = 'qualification';
      else if (meetingCount >= 3) dealStage = 'discovery_deep';
      else if (meetingCount >= 1) dealStage = 'discovery';
      else if (score >= 5) dealStage = 'prospecting';
      else dealStage = 'unengaged';

      // Get key contacts for action recommendations
      const topContact = persons.length > 0 ? persons[0] : null;
      const cfo = persons.find(p => /CFO|Chief Financial/i.test(p.role));
      const cto = persons.find(p => /CTO|CIO|Chief Technology|Chief Information|Head.*IT|Head.*Digital/i.test(p.role));

      // Stale deal detection — with recommended actions
      if (daysSinceContact !== null && daysSinceContact > 30 && score >= 5 && !['won', 'lost'].includes(dealStage)) {
        const reEngageContact = topContact || cto || cfo;
        const actions = [];
        if (reEngageContact) {
          actions.push({ type: 'email', label: `Draft re-engagement email to ${reEngageContact.canonical_name}`, target: reEngageContact.canonical_name, targetRole: reEngageContact.role });
        }
        actions.push({ type: 'meeting_prep', label: 'Prepare a fresh brief' });
        if (dealStage === 'prospecting') {
          actions.push({ type: 'stage_change', label: 'Move to Discovery', newStage: 'discovery' });
        }
        staleDeals.push({
          bankKey: bank.key, bankName: bank.bank_name, country: bank.country,
          score: Math.round(score * 10) / 10, daysSinceContact, dealStage,
          reason: daysSinceContact > 60 ? 'Critical — no contact in ' + daysSinceContact + ' days'
            : 'Stale — ' + daysSinceContact + ' days since last contact',
          actions,
        });
      }

      // High-impact changes → priorities with "so what" implications and actions
      for (const change of changes) {
        let description = '';
        let implication = '';
        const actions = [];

        if (change.field_path.includes('stock') && change.old_value && change.new_value) {
          const oldP = parseFloat(change.old_value);
          const newP = parseFloat(change.new_value);
          if (oldP && newP) {
            const pct = Math.round(((newP - oldP) / oldP) * 100);
            description = `Stock ${pct > 0 ? 'up' : 'down'} ${Math.abs(pct)}% (${change.old_value} → ${change.new_value})`;
            if (pct < -10) {
              implication = 'Cost pressure increasing — strengthens efficiency and platform consolidation messaging';
              if (cfo) actions.push({ type: 'email', label: `Email ${cfo.canonical_name} about cost optimization`, target: cfo.canonical_name, targetRole: cfo.role, emailType: 'value_prop' });
              actions.push({ type: 'update_brief', label: 'Regenerate brief with cost pressure angle' });
            } else if (pct > 10) {
              implication = 'Strong performance — bank may have budget for strategic investments';
              actions.push({ type: 'update_brief', label: 'Regenerate brief with growth narrative' });
            }
          }
        } else if (change.field_path.includes('app_rating')) {
          const oldR = parseFloat(change.old_value);
          const newR = parseFloat(change.new_value);
          description = `App rating changed: ${change.old_value} → ${change.new_value}`;
          if (newR < oldR) {
            implication = 'CX declining — strengthens digital experience modernization pitch';
            if (cto) actions.push({ type: 'email', label: `Email ${cto.canonical_name} about CX gap`, target: cto.canonical_name, targetRole: cto.role, emailType: 'value_prop' });
          } else {
            implication = 'CX improving — bank is investing in digital, may be open to platform partnership';
          }
        } else if (change.field_path.includes('role')) {
          description = `Role change: ${change.old_value} → ${change.new_value}`;
          implication = 'Leadership change creates window for new vendor conversations';
          actions.push({ type: 'email', label: 'Draft introduction email to new contact', emailType: 'cold_intro' });
        }

        if (description) {
          if (actions.length === 0) actions.push({ type: 'view_bank', label: 'Review bank profile' });
          priorities.push({
            bankKey: bank.key, bankName: bank.bank_name, score: Math.round(score * 10) / 10,
            type: 'change', description, implication, date: change.changed_at, actions,
          });
        }
      }

      // High-relevance signals → with contextual actions
      for (const sig of signals) {
        const actions = [];
        const sigLower = sig.title.toLowerCase();
        if (/appoint|hire|new.*ceo|new.*cto|new.*cio|leadership/i.test(sigLower)) {
          actions.push({ type: 'email', label: 'Draft intro to new executive', emailType: 'cold_intro' });
          actions.push({ type: 'research', label: 'Research new contact' });
        } else if (/transform|digital|platform|moderniz/i.test(sigLower)) {
          actions.push({ type: 'meeting_prep', label: 'Prepare brief with this signal' });
          if (cto) actions.push({ type: 'email', label: `Email ${cto.canonical_name}`, target: cto.canonical_name, emailType: 'follow_up' });
        } else if (/merger|acqui|consolidat/i.test(sigLower)) {
          actions.push({ type: 'update_brief', label: 'Update account plan with merger intel' });
          actions.push({ type: 'meeting_prep', label: 'Prepare multi-entity positioning brief' });
        } else {
          actions.push({ type: 'view_bank', label: 'Review in context' });
        }
        recentSignals.push({
          bankKey: bank.key, bankName: bank.bank_name, score: Math.round(score * 10) / 10,
          title: sig.title, relevance: sig.relevance_score, date: sig.fetched_at, actions,
        });
      }

      // Outstanding commitments → actions
      if (outstandingCommitments > 0) {
        upcomingActions.push({
          bankKey: bank.key, bankName: bank.bank_name,
          type: 'commitment', count: outstandingCommitments,
          description: outstandingCommitments + ' unfulfilled commitment' + (outstandingCommitments > 1 ? 's' : ''),
        });
      }
    }

    // Sort and limit
    staleDeals.sort((a, b) => b.daysSinceContact - a.daysSinceContact);
    priorities.sort((a, b) => b.score - a.score);
    recentSignals.sort((a, b) => b.relevance - a.relevance);

    // Pipeline summary
    const allStages = banks.map(b => {
      const hasAP = !!db.prepare('SELECT 1 FROM account_plans WHERE bank_key = ?').get(b.key);
      const mc = db.prepare("SELECT COUNT(*) as c FROM meeting_history WHERE bank_key = ? AND meeting_type = 'client'").get(b.key).c;
      const outcome = db.prepare("SELECT outcome FROM deal_outcomes WHERE bank_key = ? ORDER BY created_at DESC LIMIT 1").get(b.key);
      if (outcome?.outcome === 'won') return 'won';
      if (outcome?.outcome === 'lost') return 'lost';
      if (hasAP) return 'qualification';
      if (mc >= 3) return 'discovery_deep';
      if (mc >= 1) return 'discovery';
      return 'prospecting';
    });
    const pipeline = {};
    allStages.forEach(s => { pipeline[s] = (pipeline[s] || 0) + 1; });

    jsonResponse(res, 200, {
      generatedAt: new Date().toISOString(),
      priorities: priorities.slice(0, 5),
      staleDeals: staleDeals.slice(0, 5),
      recentSignals: recentSignals.slice(0, 8),
      upcomingActions: upcomingActions.slice(0, 5),
      pipeline,
      totalBanks: banks.length,
    });
    return true;
  }

  // ── POST /api/research/email-draft — DEPRECATED 2026-04 ──
  // Strategic Repositioning Sprint 0: Nova does not draft prospect-facing
  // outreach copy. The brief is explicit: "Nova does not generate, draft,
  // template, or assist with executive-to-executive correspondence ... Nova
  // does not draft connection requests, comment templates, DMs, or
  // multi-touch outreach copy."
  //
  // Endpoint stays alive for 30 days (until 2026-05-28) so any in-flight
  // integration doesn't 404. Returns deprecation headers + a console
  // warning. Hard delete after 2026-05-28.
  //
  // Replacement: AEs use the structured intelligence (PersonSignalsPanel,
  // mentioned_stakeholders cross-link, MEDDICC role, signal action_points)
  // and write their own outreach in Claude-in-a-chat or by hand.
  if (path === '/api/research/email-draft' && req.method === 'POST') {
    res.setHeader('Deprecation', 'true');
    res.setHeader('Sunset', 'Wed, 28 May 2026 00:00:00 GMT');
    res.setHeader('Link', '</docs/strategic-repositioning>; rel="deprecation"');
    console.warn('[deprecated] /api/research/email-draft called — Nova does not generate prospect-facing outreach copy. Hard delete scheduled 2026-05-28.');
    if (!aiRateCheck(res)) return true;
    if (!isClaudeAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured.' });
      return true;
    }
    const { bankKey, recipientName, recipientRole, emailType, context } = await parseBody(req);
    if (!bankKey || !recipientName || !emailType) {
      jsonResponse(res, 400, { error: 'Missing required fields: bankKey, recipientName, emailType' });
      return true;
    }

    const bankRow = db.prepare('SELECT bank_name, country, data FROM banks WHERE key = ?').get(bankKey);
    if (!bankRow) { jsonResponse(res, 404, { error: 'Bank not found' }); return true; }
    const bd = JSON.parse(bankRow.data || '{}');
    const vsRow = db.prepare('SELECT data FROM value_selling WHERE bank_key = ?').get(bankKey);
    const vs = vsRow ? JSON.parse(vsRow.data) : null;

    const emailTypes = {
      'cold_intro': 'Write a cold introduction email. The sender has never met this person. The goal is to get a 30-minute discovery call. Be concise (under 150 words), specific to their role, and reference one concrete insight about their bank.',
      'follow_up': 'Write a follow-up email after a meeting. Reference specific topics discussed. Propose clear next steps. Keep it warm and action-oriented.',
      'intro_request': 'Write an email asking a known contact to introduce you to another person at the bank. Be specific about why you want to connect and what value you can bring.',
      'value_prop': 'Write a value proposition email. Lead with a specific challenge the bank faces, connect it to a quantified outcome, and propose a brief call to discuss. Include one reference customer if available.',
      'event_invite': 'Write an invitation to a Backbase event, webinar, or roundtable. Make it relevant to their role and current challenges.',
    };

    const typeInstruction = emailTypes[emailType] || emailTypes.cold_intro;

    // Fetch deal context for tone awareness
    const stageRow = db.prepare('SELECT status FROM pipeline_settings WHERE bank_key = ?').get(bankKey);
    const dealStage = stageRow?.status || 'prospect';
    const lastMeeting = db.prepare("SELECT meeting_date, outcome, key_topics FROM meeting_history WHERE bank_key = ? AND meeting_type = 'client' ORDER BY meeting_date DESC LIMIT 1").get(bankKey);
    const meetingCount = db.prepare("SELECT COUNT(*) as c FROM meeting_history WHERE bank_key = ? AND meeting_type = 'client'").get(bankKey).c;

    // Stage-aware tone guidance
    const toneByStage = {
      prospect: 'This is a NEW prospect — we have never engaged. Tone: curious, value-led, zero assumption of prior relationship. Do NOT reference past meetings.',
      discovery: 'We are in EARLY DISCOVERY — we have had ' + meetingCount + ' meeting(s). Tone: warm, building on established rapport. Reference shared context if available.',
      qualification: 'We are in QUALIFICATION — multiple meetings have happened. Tone: collaborative, solution-oriented. Reference specific challenges discussed.',
      proof_of_value: 'We are in PROOF OF VALUE — the bank is evaluating us. Tone: confident, evidence-driven. Reference ROI and reference customers.',
      negotiation: 'We are in NEGOTIATION — deal is close. Tone: professional, clear on next steps. Do not oversell — focus on removing blockers.',
      won: 'Deal is WON — this is a customer. Tone: partnership, onboarding support, long-term relationship.',
      lost: 'We LOST this deal previously. Tone: humble, re-engagement. Acknowledge the past, offer fresh perspective without pressure.',
    };
    const stageContext = toneByStage[dealStage] || toneByStage.prospect;

    console.log(`📧 Email draft: ${emailType} to ${recipientName} at ${bankRow.bank_name} (stage: ${dealStage})`);

    const systemPrompt = `You are a senior Value Consultant at Backbase, the AI-native Banking OS / AI-Powered Banking Platform vendor, writing a professional email. You write like a real person — no corporate jargon, no filler, no "I hope this email finds you well." Every sentence earns its place. When referencing Backbase capabilities, use current product names (Banking OS, APA, CLO, segment OSes) — never the older "engagement banking platform" framing.

${typeInstruction}

DEAL STAGE CONTEXT:
${stageContext}

Rules:
- Subject line must be specific and intriguing (not generic like "Partnership opportunity")
- Opening sentence must be relevant to the recipient's role or a recent bank event
- Body must reference at least one specific data point about the bank
- The tone MUST match the deal stage described above — a cold intro to a prospect sounds completely different from a follow-up to someone in negotiation
- Close with a clear, low-friction ask (suggest specific times, not "let me know")
- Sign off as the sender (Backbase Value Consultant)
- Total email under 200 words unless it's a value proposition (under 300)

Return ONLY valid JSON:
{
  "subject": "string",
  "body": "string (use \\n for line breaks)",
  "tone_notes": "1 sentence explaining the tone choice for this recipient and deal stage"
}`;

    const lastMeetingContext = lastMeeting
      ? `\nLast meeting: ${lastMeeting.meeting_date}, outcome: ${lastMeeting.outcome || 'unknown'}${lastMeeting.key_topics ? ', topics: ' + JSON.parse(lastMeeting.key_topics).join(', ') : ''}`
      : '';

    const userPrompt = `Recipient: ${recipientName}, ${recipientRole || 'Executive'} at ${bankRow.bank_name}
Bank: ${bankRow.bank_name} (${bankRow.country})
Deal stage: ${dealStage} (${meetingCount} meetings logged)
Email type: ${emailType}
${context ? 'Additional context: ' + context : ''}${lastMeetingContext}

Bank overview: ${(bd.overview || '').substring(0, 300)}
Key pain points: ${(bd.pain_points || []).slice(0, 3).map(p => p.title).join(', ')}
Value hypothesis: ${vs?.value_hypothesis?.one_liner || 'Not defined'}
Recent signals: ${(bd.signals || []).slice(0, 3).map(s => s.signal).join(', ')}
Reference customers: ${(vs?.reference_customers || []).slice(0, 2).map(r => r.name + ' (' + r.region + ')').join(', ') || 'None'}`;

    try {
      const raw = await callClaude(systemPrompt, userPrompt, { maxTokens: 1000, timeout: 30000 });
      const cleaned = raw.replace(/```json\n?|\n?```/g, '').trim();
      const result = JSON.parse(cleaned);
      console.log(`   ✅ Email draft complete`);
      jsonResponse(res, 200, { result });
    } catch (err) {
      console.error(`   ❌ Email draft failed: ${err.message}`);
      jsonResponse(res, 500, { error: 'Email draft failed: ' + err.message });
    }
    return true;
  }

  // ── GET /api/account-plan/:bankKey — Retrieve cached account plan ──
  const cachedPlanMatch = path.match(/^\/api\/account-plan\/([^/]+)$/);
  if (cachedPlanMatch && req.method === 'GET') {
    const bk = decodeURIComponent(cachedPlanMatch[1]);
    const cached = db.prepare('SELECT * FROM account_plans WHERE bank_key = ? ORDER BY generated_at DESC LIMIT 1').get(bk);
    if (!cached) {
      jsonResponse(res, 404, { error: 'No cached account plan for this bank' });
    } else {
      const result = JSON.parse(cached.result);
      const inputs = cached.inputs ? JSON.parse(cached.inputs) : {};
      jsonResponse(res, 200, { result, inputs, generated_at: cached.generated_at, cached: true });
    }
    return true;
  }

  // ── POST /api/research/account-plan — Generate close plan or late-stage entry framing ──
  if (path === '/api/research/account-plan' && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isClaudeAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured. Account plan requires AI.' });
      return true;
    }
    const body = await parseBody(req);
    const { type, bankName, bankKey, inputs } = body;
    if (!type || !bankName) {
      jsonResponse(res, 400, { error: 'Missing required fields: type, bankName' });
      return true;
    }

    // Fetch bank context from DB
    let bankContext = {};
    if (bankKey) {
      const bankRow = db.prepare('SELECT data FROM banks WHERE key = ?').get(bankKey);
      if (bankRow) {
        const bd = JSON.parse(bankRow.data || '{}');
        bankContext = {
          overview: (bd.overview || '').substring(0, 500),
          strategic_initiatives: typeof bd.strategic_initiatives === 'string' ? bd.strategic_initiatives.substring(0, 300) : '',
          pain_points: (bd.pain_points || []).slice(0, 5).map(p => p.title).join(', '),
          signals: (bd.signals || []).slice(0, 5).map(s => s.signal).join(', '),
        };
      }
    }

    console.log(`📋 Account plan (${type}): ${bankName}`);

    let systemPrompt = `You are a senior Value Consultant at Backbase, the AI-native Banking OS / AI-Powered Banking Platform vendor.

${BACKBASE_2026_CONTEXT}

You are helping a sales team manage a complex B2B deal with ${bankName}. You reason like an experienced enterprise software salesperson combined with a strategy consultant. Use current product framing throughout (Banking OS, APA, CLO, segment OSes; the three commercial entry points).
Return ONLY valid JSON. No markdown fences. No preamble. No explanation.`;

    let userPrompt = '';

    if (type === 'close-plan') {
      userPrompt = `Generate a mutual close plan for this deal.

Bank: ${bankName}
Overview: ${bankContext.overview || 'Not provided'}
Strategic initiatives: ${bankContext.strategic_initiatives || 'Not provided'}
Key pain points: ${bankContext.pain_points || 'Not provided'}
Recent signals: ${bankContext.signals || 'Not provided'}
Target close date: ${inputs?.closeDate || 'Not specified'}
AE owner: ${inputs?.aeOwner || 'Not specified'}
Estimated ARR: ${inputs?.dealSizeEstimate || 'Not specified'}
Known stakeholders: ${inputs?.knownStakeholders || 'Not specified'}
Open items / blockers: ${inputs?.openItems || 'Not specified'}

Return JSON:
{
  "summary": "2-3 sentence strategic close narrative",
  "timeline": [
    {
      "phase": "phase name",
      "target_date": "Month Year",
      "activities": ["activity 1", "activity 2", "activity 3"],
      "owner": "who owns this phase",
      "customer_ask": "what we need the customer to do",
      "go_no_go": "condition that must be true to proceed"
    }
  ],
  "risks": ["risk 1", "risk 2", "risk 3"],
  "next_immediate_action": "the single most important action this week"
}
Include 4-6 phases sequencing from today to close. Be specific to this bank.`;
    } else if (type === 'late-stage-entry') {
      userPrompt = `Generate a late-stage VC entry framing for this deal.

Bank: ${bankName}
Overview: ${bankContext.overview || 'Not provided'}
Key pain points: ${bankContext.pain_points || 'Not provided'}
Deal stage: ${inputs?.dealStage || 'Not specified'}
Estimated close date: ${inputs?.closeDateEstimate || 'Not specified'}
Estimated ARR: ${inputs?.arrEstimate || 'Not specified'}
Competitor involved: ${inputs?.competitorInvolved || 'None known'}

Return JSON:
{
  "vc_entry_point": "When and how the VC should enter this deal now",
  "deal_engineering_framing": "How to reframe the value conversation at this late stage",
  "executive_decision_paper": {
    "option_a": { "label": "Option A name", "description": "what this is", "vc_angle": "how to position" },
    "option_b": { "label": "Option B name", "description": "what this is", "vc_angle": "how to position" },
    "option_c": { "label": "Option C name", "description": "what this is", "vc_angle": "how to position" }
  },
  "deal_pricing_angle": "Structural framing for the commercial discussion",
  "ae_approach_script": "Exact language VC should use approaching the AE"
}`;
    } else {
      jsonResponse(res, 400, { error: 'Invalid type. Use "close-plan" or "late-stage-entry".' });
      return true;
    }

    try {
      const raw = await callClaude(systemPrompt, userPrompt, { maxTokens: 4096, timeout: 90000 });
      const cleaned = raw.replace(/```json\n?|\n?```/g, '').trim();
      const result = JSON.parse(cleaned);
      console.log(`   ✅ Account plan complete`);
      jsonResponse(res, 200, { result });
    } catch (err) {
      console.error(`   ❌ Account plan failed: ${err.message}`);
      jsonResponse(res, 500, { error: 'Account plan generation failed: ' + err.message });
    }
    return true;
  }

  // ── POST /api/banks/:key/power-map — Generate MEDDICC power map via AI ──
  const powerMapPostMatch = path.match(/^\/api\/banks\/([^/]+)\/power-map$/);
  if (powerMapPostMatch && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isClaudeAvailable()) {
      jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured.' });
      return true;
    }
    const bankKey = decodeURIComponent(powerMapPostMatch[1]);
    const body = await parseBody(req);
    const persona = body?.persona || null;

    // Fetch persons + bank context
    const personsRows = db.prepare('SELECT canonical_name, role, role_category, lob, note, linkedin_url, confidence_tier FROM persons WHERE bank_key = ? ORDER BY role_category').all(bankKey);
    if (personsRows.length === 0) {
      jsonResponse(res, 400, { error: 'No persons found for this bank. Seed the database first.' });
      return true;
    }
    const bankRow = db.prepare('SELECT data FROM banks WHERE key = ?').get(bankKey);
    const bankData = bankRow?.data ? JSON.parse(bankRow.data) : {};
    const qualRow = db.prepare('SELECT data FROM qualification WHERE bank_key = ?').get(bankKey);
    const qualData = qualRow?.data ? JSON.parse(qualRow.data) : {};

    const personsContext = personsRows.map(p =>
      `- ${p.canonical_name} | ${p.role} | ${p.role_category || 'unknown'} | LOB: ${p.lob || 'unknown'}${p.note ? ' | Note: ' + p.note.substring(0, 150) : ''}`
    ).join('\n');

    const bankContext = [
      bankData.bank_name ? `Bank: ${bankData.bank_name}` : '',
      bankData.country ? `Country: ${bankData.country}` : '',
      bankData.overview ? `Overview: ${bankData.overview.substring(0, 300)}` : '',
      bankData.pain_points?.length ? `Pain Points: ${bankData.pain_points.map(p => p.title).join(', ')}` : '',
      qualData.landing_zones ? `Landing Zone Score: ${qualData.landing_zones.score}/10` : '',
    ].filter(Boolean).join('\n');

    const systemPrompt = `You are an expert B2B enterprise sales strategist. Analyze these contacts at a bank and produce a MEDDICC power map.

CRITICAL RULE: Every assessment MUST be grounded in evidence from the provided data. If you are inferring from role title alone (no notes, no signals), explicitly say "Inferred from role — no direct evidence available." Do NOT present inferences as confirmed facts.

For each person, assign:
- meddicc_roles: array of MEDDICC roles this person plays (can have multiple):
  * 'economic_buyer' — final budget authority
  * 'champion' — internal advocate who wants you to win
  * 'decision_criteria' — defines what the solution must do
  * 'decision_process' — controls the procurement/approval process
  * 'identify_pain' — feels the pain most acutely, motivated to change
  * 'metrics' — cares about ROI and quantifiable outcomes
  * 'competition' — may prefer a competitor or status quo
- influence_score: integer 1-10 (10 = highest decision power)
- influence_reasoning: 1-2 sentences explaining WHY this score. Reference specific evidence: role seniority, budget authority, org position, or signals from notes.
- engagement_status: 'engaged' | 'neutral' | 'unaware' | 'blocker'
- engagement_reasoning: 1-2 sentences explaining WHY this status. Reference evidence: public speaking, news mentions, research signals. If no evidence, say "No direct engagement signals — defaulting to neutral based on role."
- recommended_action: one sentence — what should the sales rep do with this person?
- action_reasoning: 1 sentence explaining WHY this action, specific to this person.
- political_notes: any inferred political dynamics (reporting lines, cross-functional influence, allies or blockers)

Base your analysis on: role seniority, LOB relevance to Backbase's digital banking proposition, typical banking org dynamics, and any signals in the person notes.

Return ONLY valid JSON. No markdown code fences. Schema:
{
  "generated_at": "ISO date",
  "methodology": "MEDDICC",
  "methodology_note": "Brief explanation of data availability and what was inferred vs. evidenced",
  "economic_buyer_confidence": "high|medium|low",
  "champion_identified": true|false,
  "contacts": [
    {
      "canonical_name": "Person Name",
      "meddicc_roles": ["economic_buyer"],
      "influence_score": 9,
      "influence_reasoning": "As CEO, final budget authority for strategic investments. Controls group-level digital strategy.",
      "engagement_status": "neutral",
      "engagement_reasoning": "No direct engagement signals. CEO-level contacts rarely engage without exec sponsor intro.",
      "recommended_action": "Secure exec sponsor meeting via peer-level Backbase leadership introduction.",
      "action_reasoning": "CEO engagement requires top-down approach — peer CEO intro is most effective.",
      "political_notes": "Final authority but delegates day-to-day tech decisions to CTO/CIO."
    }
  ],
  "deal_risks": ["Risk 1"],
  "risk_reasoning": ["Why this is a risk — what evidence supports it"],
  "recommended_entry_sequence": ["Step 1", "Step 2"],
  "sequence_reasoning": "2-3 sentences explaining the strategic logic — why start with person X, why Y before Z."
}`;

    const userMessage = `BANK CONTEXT:\n${bankContext}\n\nCONTACTS (${personsRows.length} people):\n${personsContext}${persona ? `\n\nMEETING PERSONA CONTEXT: ${persona}` : ''}`;

    console.log(`\n🎯 Power map generation: ${bankKey} (${personsRows.length} persons)...`);
    try {
      const raw = await callClaude(systemPrompt, userMessage, { maxTokens: 4096, timeout: 120000 });
      const jsonStr = raw.replace(/```json\n?|\n?```/g, '').trim();
      const result = JSON.parse(jsonStr);

      // Cache in power_maps table (upsert by bank_key)
      const id = crypto.randomUUID();
      db.prepare('DELETE FROM power_maps WHERE bank_key = ?').run(bankKey);
      db.prepare('INSERT INTO power_maps (id, bank_key, result, persona) VALUES (?, ?, ?, ?)').run(
        id, bankKey, JSON.stringify(result), persona
      );

      // ── Sync per-contact assignments back to persons table ──
      // The power_maps row is the AI-generated cache; persons.* columns hold the
      // consultant-editable overrides. We write the AI assignments to persons so
      // the stakeholder map matrix renders with MEDDICC roles, influence scores,
      // and engagement positions out of the box. Consultants can still override
      // any field via the PersonIntelCard.
      let synced = 0;
      try {
        const updateStmt = db.prepare(`
          UPDATE persons
          SET meddicc_roles = ?, influence_score = ?, engagement_status = ?, support_status = ?,
              updated_at = datetime('now')
          WHERE bank_key = ? AND canonical_name = ?
        `);
        for (const contact of (result.contacts || [])) {
          const meddiccArr = Array.isArray(contact.meddicc_roles) ? contact.meddicc_roles : [];
          // Derive support_status from MEDDICC + engagement signals
          const meddiccLower = meddiccArr.map(r => String(r).toLowerCase());
          let supportStatus;
          if (meddiccLower.includes('champion')) supportStatus = 'champion';
          else if (contact.engagement_status === 'blocker' || meddiccLower.includes('competition')) supportStatus = 'blocker';
          else if (contact.engagement_status === 'engaged') supportStatus = 'supporter';
          else supportStatus = 'neutral';
          const r = updateStmt.run(
            JSON.stringify(meddiccArr),
            contact.influence_score ?? null,
            contact.engagement_status || 'neutral',
            supportStatus,
            bankKey,
            contact.canonical_name
          );
          if (r.changes > 0) synced++;
        }
      } catch (syncErr) {
        // Sync failure shouldn't fail the whole request — power_maps row is still cached
        console.error(`   ⚠️  Power map → persons sync error: ${syncErr.message}`);
      }

      console.log(`   ✅ Power map complete: ${result.contacts?.length || 0} contacts mapped, ${synced} synced to persons`);
      jsonResponse(res, 200, { result, synced_to_persons: synced });
    } catch (err) {
      console.error(`   ❌ Power map failed: ${err.message}`);
      jsonResponse(res, 500, { error: 'Power map generation failed: ' + err.message });
    }
    return true;
  }

  // ── GET /api/banks/:key/power-map — Return cached power map ──
  const powerMapGetMatch = path.match(/^\/api\/banks\/([^/]+)\/power-map$/);
  if (powerMapGetMatch && req.method === 'GET') {
    const bankKey = decodeURIComponent(powerMapGetMatch[1]);
    const row = db.prepare('SELECT * FROM power_maps WHERE bank_key = ? ORDER BY generated_at DESC LIMIT 1').get(bankKey);
    if (!row) {
      jsonResponse(res, 404, { error: 'No power map generated yet. Use POST to generate.' });
      return true;
    }
    const parsed = { ...row };
    try { parsed.result = JSON.parse(row.result); } catch (e) { /* keep as string */ }
    jsonResponse(res, 200, parsed);
    return true;
  }

  // ── POST /api/countries/:name/refresh-intelligence — AI-powered country market intelligence ──
  const countryRefreshMatch = path.match(/^\/api\/countries\/([^/]+)\/refresh-intelligence$/);
  if (countryRefreshMatch && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isCountryIntelAvailable()) { jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured.' }); return true; }

    const countryName = decodeURIComponent(countryRefreshMatch[1]);
    const body = await parseBody(req);
    const sections = body.sections || ['fintech_landscape', 'regulatory_environment', 'market_news', 'customer_needs'];
    const force = body.force || false;

    const countryRow = db.prepare('SELECT * FROM countries WHERE name = ?').get(countryName);
    if (!countryRow) { jsonResponse(res, 404, { error: `Country not found: ${countryName}` }); return true; }

    let existingData;
    try { existingData = JSON.parse(countryRow.data || '{}'); } catch { existingData = {}; }

    const startTime = Date.now();
    try {
      const { refreshed, skipped } = await refreshCountryIntelligence(countryName, existingData, sections, force);

      // Merge refreshed sections into existing data
      const merged = { ...existingData, ...refreshed };
      db.prepare("UPDATE countries SET data = ?, updated_at = datetime('now') WHERE name = ?")
        .run(JSON.stringify(merged), countryName);

      jsonResponse(res, 200, {
        country: countryName,
        refreshed_sections: Object.keys(refreshed),
        skipped_sections: skipped,
        duration_ms: Date.now() - startTime,
        _source: 'claude-ai',
      });
    } catch (err) {
      console.error(`Country intel refresh failed for ${countryName}:`, err);
      jsonResponse(res, 500, { error: err.message || 'Country intelligence refresh failed' });
    }
    return true;
  }

  // ══════════════════════════════════════════════════════════════
  // STRATEGIC ACCOUNT PLAN — AI endpoints
  // ══════════════════════════════════════════════════════════════

  // Shared helper: load full bank context for AI planning
  const loadBankContext = (bankKey) => {
    const bankRow = db.prepare('SELECT * FROM banks WHERE key = ?').get(bankKey);
    if (!bankRow) return null;
    const bank = JSON.parse(bankRow.data || '{}');
    const qualRow = db.prepare('SELECT data FROM qualification WHERE bank_key = ?').get(bankKey);
    const qual = qualRow ? JSON.parse(qualRow.data || '{}') : {};
    const compRow = db.prepare('SELECT data FROM competition WHERE bank_key = ?').get(bankKey);
    const comp = compRow ? JSON.parse(compRow.data || '{}') : {};
    const cxRow = db.prepare('SELECT * FROM cx WHERE bank_key = ?').get(bankKey);
    const cx = cxRow ? { digital_maturity: cxRow.digital_maturity, app_rating_ios: cxRow.app_rating_ios, app_rating_android: cxRow.app_rating_android, ...(JSON.parse(cxRow.data || '{}')) } : {};
    const persons = db.prepare('SELECT canonical_name, role, role_category, lob, meddicc_roles, influence_score, engagement_status, support_status, note FROM persons WHERE bank_key = ? ORDER BY role_category, seniority_order').all(bankKey);
    const signals = db.prepare('SELECT title, implication FROM live_signals WHERE bank_key = ? ORDER BY fetched_at DESC LIMIT 10').all(bankKey);
    return { bank_name: bankRow.bank_name, country: bankRow.country, bank, qual, comp, cx, persons, signals };
  };

  // Helper: upsert account_plans row merging a new section into result JSON
  const upsertAccountPlanSection = (bankKey, sectionKey, sectionPayload) => {
    const existing = db.prepare('SELECT result FROM account_plans WHERE bank_key = ? ORDER BY generated_at DESC LIMIT 1').get(bankKey);
    const base = existing ? (() => { try { return JSON.parse(existing.result); } catch { return {}; } })() : {};
    const merged = { ...base, [sectionKey]: { ...sectionPayload, _generated_at: new Date().toISOString() } };
    // Keep only one row per bank (delete old, insert new)
    db.prepare('DELETE FROM account_plans WHERE bank_key = ?').run(bankKey);
    db.prepare('INSERT INTO account_plans (id, bank_key, result) VALUES (?, ?, ?)')
      .run(crypto.randomUUID(), bankKey, JSON.stringify(merged));
    return merged[sectionKey];
  };

  // ── POST /api/banks/:key/strategic-snapshot — 6-card strategic snapshot ──
  const snapshotMatch = path.match(/^\/api\/banks\/([^/]+)\/strategic-snapshot$/);
  if (snapshotMatch && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isClaudeAvailable()) { jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured.' }); return true; }
    const bankKey = decodeURIComponent(snapshotMatch[1]);
    const ctx = loadBankContext(bankKey);
    if (!ctx) { jsonResponse(res, 404, { error: 'Bank not found' }); return true; }

    const systemPrompt = `You are a senior strategic value consultant for Backbase, the AI-native Banking OS / AI-Powered Banking Platform vendor.

${BACKBASE_2026_CONTEXT}

You produce strategic account analyses for banking deals. Your outputs must be:
- EVIDENCE-BASED: cite specific data points from the inputs
- ACTIONABLE: every recommendation leads to a concrete next step
- STRATEGIC: think like a McKinsey partner, not a sales rep
- HONEST: flag gaps, risks, and competing interests openly
- POSITIONED: reference Banking OS / APA / CLO / segment-specific OSes by name when relevant; cite Operational Layers (Nexus, Sentinel, Grand Central, Process Studio, Agent Studio, Intelligence) and proof-point ranges (30-40% cost-to-serve, 50-90% faster execution, 3x productivity, 2-4x growth) where they sharpen the argument

Output ONLY valid JSON matching the requested schema. No markdown fences, no commentary.`;

    const personSummary = ctx.persons.slice(0, 12).map(p =>
      `- ${p.canonical_name} (${p.role}, ${p.role_category || 'Other'})${p.meddicc_roles ? ' [' + p.meddicc_roles + ']' : ''}${p.note ? ': ' + p.note.substring(0, 100) : ''}`
    ).join('\n');
    const signalSummary = ctx.signals.slice(0, 5).map(s => `- ${s.title}`).join('\n');

    // Pack C: pull consultant-acknowledged signals as VALIDATED FACTS.
    // Empty string when nothing acknowledged — clean prompt either way.
    const validatedFactsBlock = getValidatedFactsBlockForBank(db, bankKey);

    const userPrompt = `Generate a Strategic Account Snapshot for ${ctx.bank_name} (${ctx.country}).

${validatedFactsBlock ? validatedFactsBlock + '\n\n' : ''}BANK CONTEXT:
Overview: ${(ctx.bank.overview || '').substring(0, 1500)}
Strategic Initiatives: ${typeof ctx.bank.strategic_initiatives === 'string' ? ctx.bank.strategic_initiatives.substring(0, 800) : JSON.stringify(ctx.bank.strategic_initiatives || {}).substring(0, 800)}
Pain Points: ${(ctx.bank.pain_points || []).slice(0, 5).map(p => p.title || p).join('; ')}
Backbase Landing Zones: ${(ctx.bank.backbase_landing_zones || []).map(z => z.zone || z).join(', ')}
Tech Stack: Core=${ctx.comp.core_banking || '?'}, Digital=${ctx.comp.digital_platform || '?'}, Risk=${ctx.comp.vendor_risk || '?'}
Digital Maturity: ${ctx.cx.digital_maturity || '?'}

KEY STAKEHOLDERS (${ctx.persons.length}):
${personSummary || 'None identified yet'}

RECENT SIGNALS:
${signalSummary || 'No recent signals'}

Produce JSON with these exact keys:
{
  "strategic_initiatives_summary": ["3-5 bullet points of what THIS BANK is strategically driving"],
  "partner_plan": ["3-5 bullets describing OUR GTM approach for this account — sequencing, motion priority, accounts to reference"],
  "responsive_measures": ["3-5 bullets of what Backbase does when the bank takes specific actions (e.g., 'If they RFP core banking, we position decoupling strategy')"],
  "proactive_measures": ["3-5 bullets of what WE initiate to advance the deal (e.g., 'Executive briefing for CDO on open banking case studies')"],
  "potential_risks": ["3-5 bullets of deal risks — incumbent vendor, budget cycle, political blockers, competitive threats"],
  "backbase_position": ["3-5 bullets describing our competitive position — where we win, where we're weak, Backbase's unique angle"],
  "next_steps": ["3-5 specific actions in priority order, each a concrete next move"]
}

Every bullet must be SPECIFIC to ${ctx.bank_name}, not generic advice.`;

    try {
      const response = await callClaude(systemPrompt, userPrompt, { maxTokens: 2500, timeout: 120000 });
      const cleaned = response.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
      let parsed;
      try { parsed = JSON.parse(cleaned); } catch (e) {
        throw new Error(`AI output was not valid JSON: ${e.message}`);
      }
      const saved = upsertAccountPlanSection(bankKey, 'strategic_snapshot', parsed);
      jsonResponse(res, 200, { bank_key: bankKey, strategic_snapshot: saved, _source: 'claude-ai' });
    } catch (err) {
      console.error('Strategic snapshot failed:', err);
      jsonResponse(res, 500, { error: err.message || 'Snapshot generation failed' });
    }
    return true;
  }

  // ── POST /api/banks/:key/strategic-objectives — Derived objectives + initiatives ──
  const objectivesMatch = path.match(/^\/api\/banks\/([^/]+)\/strategic-objectives$/);
  if (objectivesMatch && req.method === 'POST') {
    if (!aiRateCheck(res)) return true;
    if (!isClaudeAvailable()) { jsonResponse(res, 503, { error: 'ANTHROPIC_API_KEY not configured.' }); return true; }
    const bankKey = decodeURIComponent(objectivesMatch[1]);
    const ctx = loadBankContext(bankKey);
    if (!ctx) { jsonResponse(res, 404, { error: 'Bank not found' }); return true; }

    const systemPrompt = `You are a senior banking strategy consultant working alongside Backbase, the AI-native Banking OS / AI-Powered Banking Platform vendor. Given a bank's annual report content, strategic initiatives, and observable signals, you derive:
1) Concrete strategic objectives (what outcomes they're driving toward)
2) Key initiatives required to execute each objective (reverse-engineered from the objective)
3) Backbase capability mapping (which Backbase products address each initiative)

${BACKBASE_2026_CONTEXT}

CRITICAL RULES:
- Mark each initiative's confidence as "from_report" (explicitly stated) or "ai_inferred" (logical inference)
- Cite evidence — the text snippet that supports each claim, or "Inferred" if pure reasoning
- Backbase capabilities should be SPECIFIC and use current product names — e.g., "Banking OS with Grand Central connectivity", "APA for Wealth (Agentic Process Automation)", "CLO (Customer Lifetime Orchestrator)", "Wealth OS / Commercial OS / Small Business OS / Private Banking OS / Retail OS" — NOT generic "Backbase platform" or "engagement banking"
- Reference Operational Layers (Nexus, Sentinel, Grand Central, Process Studio, Agent Studio, Intelligence) where they sharpen the mapping
- If data is thin, produce fewer high-quality objectives rather than padding

Output ONLY valid JSON.`;

    // Pack C: validated-facts injection
    const validatedFactsBlockSO = getValidatedFactsBlockForBank(db, bankKey);

    const userPrompt = `Analyze strategic objectives for ${ctx.bank_name} (${ctx.country}).

${validatedFactsBlockSO ? validatedFactsBlockSO + '\n\n' : ''}ANNUAL REPORT / OVERVIEW:
${(ctx.bank.overview || '').substring(0, 2000)}

STATED STRATEGIC INITIATIVES:
${typeof ctx.bank.strategic_initiatives === 'string' ? ctx.bank.strategic_initiatives.substring(0, 1500) : JSON.stringify(ctx.bank.strategic_initiatives || {}).substring(0, 1500)}

PAIN POINTS (suggest unstated objectives):
${(ctx.bank.pain_points || []).map(p => '- ' + (p.title || p) + (p.detail ? ': ' + p.detail.substring(0, 100) : '')).join('\n')}

LANDING ZONES (where Backbase fits):
${(ctx.bank.backbase_landing_zones || []).map(z => z.zone || z).join(', ')}

CURRENT TECH STACK:
Core: ${ctx.comp.core_banking || '?'} | Digital: ${ctx.comp.digital_platform || '?'} | Vendor Risk: ${ctx.comp.vendor_risk || 'normal'}

Produce JSON in this exact shape:
{
  "objectives": [
    {
      "objective": "Concrete strategic objective (e.g., 'Become digital-first leader in retail banking')",
      "summary": "1-2 sentences explaining why this matters for this bank",
      "confidence": "from_report" | "ai_inferred" | "mixed",
      "key_initiatives": [
        {
          "name": "Specific initiative name",
          "how": "How the bank will execute this (from report or AI inference)",
          "backbase_capability": "Specific Backbase product/capability that addresses this",
          "evidence": "Supporting text snippet OR 'Inferred from [signal]'"
        }
      ]
    }
  ],
  "methodology_note": "One sentence on how you derived these (what was explicit vs inferred)"
}

Aim for 3-5 objectives, each with 2-3 initiatives. Quality over quantity.`;

    try {
      const response = await callClaude(systemPrompt, userPrompt, { maxTokens: 3500, timeout: 120000 });
      const cleaned = response.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
      let parsed;
      try { parsed = JSON.parse(cleaned); } catch (e) {
        throw new Error(`AI output was not valid JSON: ${e.message}`);
      }
      const saved = upsertAccountPlanSection(bankKey, 'strategic_objectives', parsed);
      jsonResponse(res, 200, { bank_key: bankKey, strategic_objectives: saved, _source: 'claude-ai' });
    } catch (err) {
      console.error('Strategic objectives failed:', err);
      jsonResponse(res, 500, { error: err.message || 'Objectives generation failed' });
    }
    return true;
  }

  return false;
}
