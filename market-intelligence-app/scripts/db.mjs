/**
 * SQLite Database — connection, schema, and helpers
 * Uses better-sqlite3 (synchronous API, WAL mode)
 * DB file: data/market-intelligence.db
 */
import Database from 'better-sqlite3';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DB_PATH = join(__dirname, '..', 'data', 'market-intelligence.db');

let _db = null;

export function getDb() {
  if (!_db) {
    _db = new Database(DB_PATH);
    _db.pragma('journal_mode = WAL');
    _db.pragma('foreign_keys = ON');
    initSchema(_db);
  }
  return _db;
}

export function closeDb() {
  if (_db) { _db.close(); _db = null; }
}

function initSchema(db) {
  db.exec(`
    CREATE TABLE IF NOT EXISTS markets (
      key TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      countries TEXT NOT NULL,
      emoji TEXT,
      has_data INTEGER DEFAULT 0,
      data TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS countries (
      name TEXT PRIMARY KEY,
      market_key TEXT REFERENCES markets(key),
      data TEXT NOT NULL,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS banks (
      key TEXT PRIMARY KEY,
      bank_name TEXT NOT NULL,
      country TEXT NOT NULL,
      tagline TEXT,
      data TEXT NOT NULL,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_banks_country ON banks(country);

    CREATE TABLE IF NOT EXISTS qualification (
      bank_key TEXT PRIMARY KEY REFERENCES banks(key) ON DELETE CASCADE,
      data TEXT NOT NULL,
      updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS cx (
      bank_key TEXT PRIMARY KEY REFERENCES banks(key) ON DELETE CASCADE,
      app_rating_ios REAL,
      app_rating_android REAL,
      digital_maturity TEXT,
      data TEXT NOT NULL,
      updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS competition (
      bank_key TEXT PRIMARY KEY REFERENCES banks(key) ON DELETE CASCADE,
      core_banking TEXT,
      digital_platform TEXT,
      data TEXT NOT NULL,
      updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS value_selling (
      bank_key TEXT PRIMARY KEY REFERENCES banks(key) ON DELETE CASCADE,
      data TEXT NOT NULL,
      updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS relationships (
      bank_key TEXT PRIMARY KEY REFERENCES banks(key) ON DELETE CASCADE,
      data TEXT NOT NULL,
      updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS sources (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      ref_key TEXT NOT NULL,
      label TEXT NOT NULL,
      url TEXT,
      category TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_sources_ref ON sources(ref_key);

    CREATE TABLE IF NOT EXISTS meeting_packs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      bank_key TEXT REFERENCES banks(key),
      kdm_name TEXT,
      meeting_type TEXT,
      result TEXT NOT NULL,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS ai_analyses (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      bank_key TEXT REFERENCES banks(key),
      analysis_type TEXT,
      result TEXT NOT NULL,
      created_at TEXT DEFAULT (datetime('now')),
      UNIQUE(bank_key, analysis_type)
    );

    CREATE TABLE IF NOT EXISTS ingestion_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      run_id TEXT NOT NULL,
      bank_key TEXT,
      source TEXT NOT NULL,
      action TEXT NOT NULL,
      table_name TEXT,
      details TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_ingestion_run ON ingestion_log(run_id);
    CREATE INDEX IF NOT EXISTS idx_ingestion_bank ON ingestion_log(bank_key);
    CREATE INDEX IF NOT EXISTS idx_ingestion_source ON ingestion_log(source);

    CREATE TABLE IF NOT EXISTS landing_zone_matrix (
      bank_key TEXT PRIMARY KEY REFERENCES banks(key) ON DELETE CASCADE,
      matrix TEXT NOT NULL,
      plays TEXT,
      unconsidered TEXT,
      challenges TEXT,
      top_zones TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS discovery_storylines (
      bank_key TEXT PRIMARY KEY REFERENCES banks(key) ON DELETE CASCADE,
      storyline TEXT NOT NULL,
      roi_estimate TEXT,
      next_steps TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now'))
    );

    -- ── Live Signals (AI-classified from external sources) ──
    CREATE TABLE IF NOT EXISTS live_signals (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      bank_key TEXT REFERENCES banks(key) ON DELETE CASCADE,
      source TEXT NOT NULL,
      source_url TEXT,
      title TEXT NOT NULL,
      snippet TEXT,
      published_at TEXT,
      fetched_at TEXT NOT NULL DEFAULT (datetime('now')),
      relevance_score REAL,
      signal_type TEXT,
      implication TEXT,
      priority TEXT DEFAULT 'medium',
      classified_at TEXT,
      content_hash TEXT UNIQUE
    );
    CREATE INDEX IF NOT EXISTS idx_live_signals_bank ON live_signals(bank_key);
    CREATE INDEX IF NOT EXISTS idx_live_signals_score ON live_signals(relevance_score);
    CREATE INDEX IF NOT EXISTS idx_live_signals_date ON live_signals(published_at);

    CREATE TABLE IF NOT EXISTS signal_refresh_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      source TEXT NOT NULL,
      status TEXT DEFAULT 'running',
      articles_fetched INTEGER DEFAULT 0,
      articles_classified INTEGER DEFAULT 0,
      errors INTEGER DEFAULT 0,
      duration_ms INTEGER,
      started_at TEXT DEFAULT (datetime('now')),
      completed_at TEXT
    );

    -- ── Brief Feedback (post-meeting quality tracking) ──
    CREATE TABLE IF NOT EXISTS brief_feedback (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      bank_key TEXT REFERENCES banks(key) ON DELETE CASCADE,
      bank_name TEXT NOT NULL,
      persona TEXT,
      sections_used TEXT NOT NULL,
      accuracy_rating INTEGER NOT NULL CHECK(accuracy_rating BETWEEN 1 AND 5),
      comment TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_brief_feedback_bank ON brief_feedback(bank_key);
    CREATE INDEX IF NOT EXISTS idx_brief_feedback_date ON brief_feedback(created_at);

    -- ── Field Provenance (Layer 1: per-field source lineage + confidence) ──
    CREATE TABLE IF NOT EXISTS field_provenance (
      id TEXT PRIMARY KEY,
      entity_type TEXT NOT NULL,
      entity_key TEXT NOT NULL,
      field_path TEXT NOT NULL,
      value TEXT NOT NULL,
      source_type TEXT NOT NULL,
      source_url TEXT,
      source_date TEXT,
      confidence_tier INTEGER NOT NULL CHECK(confidence_tier BETWEEN 1 AND 3),
      is_stale INTEGER DEFAULT 0,
      captured_at TEXT DEFAULT (datetime('now')),
      UNIQUE(entity_type, entity_key, field_path)
    );
    CREATE INDEX IF NOT EXISTS idx_provenance_entity
      ON field_provenance(entity_type, entity_key);

    -- ── Entity History (Layer 3 schema, populated later — change detection log) ──
    CREATE TABLE IF NOT EXISTS entity_history (
      id TEXT PRIMARY KEY,
      entity_type TEXT NOT NULL,
      entity_key TEXT NOT NULL,
      field_path TEXT NOT NULL,
      old_value TEXT,
      new_value TEXT NOT NULL,
      changed_at TEXT DEFAULT (datetime('now')),
      source TEXT,
      pipeline_run_id TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_history_entity
      ON entity_history(entity_type, entity_key);
    CREATE INDEX IF NOT EXISTS idx_history_date
      ON entity_history(changed_at);

    -- ── Persons (Layer 2: normalized from banks.data.key_decision_makers[]) ──
    CREATE TABLE IF NOT EXISTS persons (
      id TEXT PRIMARY KEY,
      bank_key TEXT NOT NULL,
      canonical_name TEXT NOT NULL,
      role TEXT,
      role_category TEXT,
      aliases TEXT,
      linkedin_url TEXT,
      note TEXT,
      source_url TEXT,
      source_date TEXT,
      confidence_tier INTEGER DEFAULT 2,
      verified_at TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now')),
      UNIQUE(bank_key, canonical_name)
    );
    CREATE INDEX IF NOT EXISTS idx_persons_bank ON persons(bank_key);

    -- ── Pain Points (Layer 2: normalized from banks.data.pain_points[]) ──
    CREATE TABLE IF NOT EXISTS pain_points (
      id TEXT PRIMARY KEY,
      bank_key TEXT NOT NULL,
      canonical_text TEXT NOT NULL,
      category TEXT,
      detail TEXT,
      source_url TEXT,
      source_date TEXT,
      confidence_tier INTEGER DEFAULT 2,
      created_at TEXT DEFAULT (datetime('now')),
      UNIQUE(bank_key, canonical_text)
    );
    CREATE INDEX IF NOT EXISTS idx_pain_points_bank ON pain_points(bank_key);

    -- ── Landing Zones (Layer 2: normalized from 2 curated sources) ──
    CREATE TABLE IF NOT EXISTS landing_zones (
      id TEXT PRIMARY KEY,
      bank_key TEXT NOT NULL,
      zone_name TEXT NOT NULL,
      fit_score INTEGER,
      rationale TEXT,
      entry_strategy TEXT,
      source TEXT NOT NULL,
      details TEXT,
      source_url TEXT,
      confidence_tier INTEGER DEFAULT 2,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now')),
      UNIQUE(bank_key, zone_name, source)
    );
    CREATE INDEX IF NOT EXISTS idx_landing_zones_bank ON landing_zones(bank_key);

    -- ── Meeting History (Layer 4: deal context for brief enrichment) ──
    CREATE TABLE IF NOT EXISTS meeting_history (
      id TEXT PRIMARY KEY,
      bank_key TEXT NOT NULL,
      meeting_date TEXT NOT NULL,
      attendees TEXT,
      key_topics TEXT,
      objections_raised TEXT,
      commitments_made TEXT,
      outcome TEXT,
      notes TEXT,
      source TEXT DEFAULT 'manual',
      created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_meeting_history_bank ON meeting_history(bank_key);
    CREATE INDEX IF NOT EXISTS idx_meeting_history_date ON meeting_history(meeting_date);
  `);

  // Migration: add meeting_type column (idempotent — safe to re-run)
  try {
    db.exec("ALTER TABLE meeting_history ADD COLUMN meeting_type TEXT DEFAULT 'client'");
  } catch (e) {
    // Column already exists — safe to ignore
  }

  // Migration: persons org chart columns (reports_to, lob, seniority_order)
  try { db.exec("ALTER TABLE persons ADD COLUMN reports_to TEXT"); } catch (e) { /* exists */ }
  try { db.exec("ALTER TABLE persons ADD COLUMN lob TEXT"); } catch (e) { /* exists */ }
  try { db.exec("ALTER TABLE persons ADD COLUMN seniority_order INTEGER"); } catch (e) { /* exists */ }

  // Migration: persons legacy flagging + discovery source
  try { db.exec("ALTER TABLE persons ADD COLUMN is_legacy INTEGER DEFAULT 0"); } catch (e) { /* exists */ }
  try { db.exec("ALTER TABLE persons ADD COLUMN discovery_source TEXT"); } catch (e) { /* exists */ }

  // Migration: Strategic Account Plan — MEDDICC + stakeholder fields (consultant-editable overrides)
  const stakeholderColumns = [
    "ALTER TABLE persons ADD COLUMN meddicc_roles TEXT",
    "ALTER TABLE persons ADD COLUMN influence_score INTEGER",
    "ALTER TABLE persons ADD COLUMN engagement_status TEXT",
    "ALTER TABLE persons ADD COLUMN support_status TEXT",
    "ALTER TABLE persons ADD COLUMN relationship_type TEXT",
    "ALTER TABLE persons ADD COLUMN linkedin_intel TEXT",
    "ALTER TABLE persons ADD COLUMN priorities TEXT",
    "ALTER TABLE persons ADD COLUMN kpis_of_interest TEXT",
  ];
  for (const stmt of stakeholderColumns) {
    try { db.prepare(stmt).run(); } catch (e) { /* column exists */ }
  }

  // Migration: pipeline_settings status + disqualify_reason columns
  try { db.exec("ALTER TABLE pipeline_settings ADD COLUMN status TEXT DEFAULT 'prospect'"); } catch (e) { /* exists */ }
  try { db.exec("ALTER TABLE pipeline_settings ADD COLUMN disqualify_reason TEXT"); } catch (e) { /* exists */ }

  // Migration (Stage 1 signals revamp): enrich live_signals with consultant-grade fields.
  //   action_point         — concrete next step for the consultant ("Trigger Discovery play with new CTO")
  //   evidence_quote       — the actual sentence from the article that triggered the signal
  //   mentioned_stakeholders — JSON array of person names mentioned (links signal → persons table)
  try { db.exec("ALTER TABLE live_signals ADD COLUMN action_point TEXT"); } catch (e) { /* exists */ }
  try { db.exec("ALTER TABLE live_signals ADD COLUMN evidence_quote TEXT"); } catch (e) { /* exists */ }
  try { db.exec("ALTER TABLE live_signals ADD COLUMN mentioned_stakeholders TEXT"); } catch (e) { /* exists */ }
  // Pack A: is_strategic_initiative — 1 when the article represents a
  // multi-year transformation, lasting plan, or roadmap whose relevance
  // extends beyond the 2-year recency cap. Lets older "Bank announces 2024-2027
  // transformation" articles stay visible while routine 2024 quarterly
  // earnings articles get filtered out.
  try { db.exec("ALTER TABLE live_signals ADD COLUMN is_strategic_initiative INTEGER DEFAULT 0"); } catch (e) { /* exists */ }
  // Pack B (placeholder for next pack): domain_tags JSON array of LOB tags
  // (Retail / Channels / Wealth & Private / SME / Corporate / AI). Each
  // signal can carry multiple — a digital-RFP article might be ["Retail","AI"].
  try { db.exec("ALTER TABLE live_signals ADD COLUMN domain_tags TEXT"); } catch (e) { /* exists */ }

  // Migration (Stage 2 signals revamp): bridge live_signals → deal_signals.
  // High-relevance live signals get auto-promoted into deal_signals; these
  // columns let the bridge dedup, link back, distinguish demo from real,
  // and show the consultant the same action_point + evidence + stakeholder
  // mentions in the bank profile UI.
  //   action_point           — copied from live_signal at promotion time
  //   evidence_quote         — copied from live_signal at promotion time
  //   mentioned_stakeholders — copied from live_signal at promotion time
  //   live_signal_id         — back-reference for dedup ("did we already promote this article?")
  //   relevance_score        — Backbase relevance copied from live_signal (allows sorting)
  //   is_demo                — flag the original 33 hand-seeded demo rows so the UI can hide
  //                            them once real signals exist for a bank
  try { db.exec("ALTER TABLE deal_signals ADD COLUMN action_point TEXT"); } catch (e) { /* exists */ }
  try { db.exec("ALTER TABLE deal_signals ADD COLUMN evidence_quote TEXT"); } catch (e) { /* exists */ }
  try { db.exec("ALTER TABLE deal_signals ADD COLUMN mentioned_stakeholders TEXT"); } catch (e) { /* exists */ }
  try { db.exec("ALTER TABLE deal_signals ADD COLUMN live_signal_id INTEGER"); } catch (e) { /* exists */ }
  try { db.exec("ALTER TABLE deal_signals ADD COLUMN relevance_score REAL"); } catch (e) { /* exists */ }
  try { db.exec("ALTER TABLE deal_signals ADD COLUMN is_demo INTEGER DEFAULT 0"); } catch (e) { /* exists */ }
  try { db.exec("CREATE UNIQUE INDEX IF NOT EXISTS idx_deal_signals_live_id ON deal_signals(deal_id, live_signal_id) WHERE live_signal_id IS NOT NULL"); } catch (e) { /* exists */ }
  // Pack A + B: mirror new live_signals columns to deal_signals so the bridge
  // (signalRouter) can carry these fields through the promotion.
  try { db.exec("ALTER TABLE deal_signals ADD COLUMN is_strategic_initiative INTEGER DEFAULT 0"); } catch (e) { /* exists */ }
  try { db.exec("ALTER TABLE deal_signals ADD COLUMN domain_tags TEXT"); } catch (e) { /* exists */ }
  // Stage 4B: per-bank freshness tracking via signal_refresh_log.bank_key
  try { db.exec("ALTER TABLE signal_refresh_log ADD COLUMN bank_key TEXT"); } catch (e) { /* exists */ }
  try { db.exec("ALTER TABLE signal_refresh_log ADD COLUMN promoted INTEGER DEFAULT 0"); } catch (e) { /* exists */ }
  try { db.exec("CREATE INDEX IF NOT EXISTS idx_signal_refresh_log_bank ON signal_refresh_log(bank_key, completed_at)"); } catch (e) { /* exists */ }

  // ════════════════════════════════════════════════════════════════════
  //  PULSE SYSTEM (Strategic Repositioning Sprint 1)
  // ════════════════════════════════════════════════════════════════════
  // The pulse is Nova's flagship output: a quarterly account review with
  // every cell source-cited and diff-able against the prior period. This is
  // the demo that wins the redundancy argument vs. Claude-in-a-chat.
  //
  // Three tables:
  //   review_periods  — Q1 / Q2 / Q3 / Q4 buckets with start/end dates
  //   pulses          — one pulse per (bank_key, period_id), payload = JSON
  //   pulse_overrides — per-cell AE corrections (telemetry on synthesizer
  //                     weaknesses, so we know where to harden the prompt)

  db.exec(`
    CREATE TABLE IF NOT EXISTS review_periods (
      id TEXT PRIMARY KEY,
      starts_at TEXT NOT NULL,
      ends_at TEXT NOT NULL,
      status TEXT NOT NULL CHECK(status IN ('active', 'closed')),
      closed_at TEXT
    );

    CREATE TABLE IF NOT EXISTS pulses (
      id TEXT PRIMARY KEY,
      account_id TEXT NOT NULL REFERENCES banks(key) ON DELETE CASCADE,
      period_id TEXT NOT NULL REFERENCES review_periods(id),
      payload_json TEXT NOT NULL,
      generated_at TEXT NOT NULL DEFAULT (datetime('now')),
      generated_by TEXT,
      confirmed_by_ae_at TEXT,
      confirmed_by_ae TEXT,
      exported_at TEXT,
      UNIQUE(account_id, period_id)
    );
    CREATE INDEX IF NOT EXISTS idx_pulses_account ON pulses(account_id);
    CREATE INDEX IF NOT EXISTS idx_pulses_period ON pulses(period_id);

    CREATE TABLE IF NOT EXISTS pulse_overrides (
      id TEXT PRIMARY KEY,
      pulse_id TEXT NOT NULL REFERENCES pulses(id) ON DELETE CASCADE,
      cell_path TEXT NOT NULL,
      original_value TEXT,
      override_value TEXT,
      ae_id TEXT,
      reason TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_pulse_overrides_pulse ON pulse_overrides(pulse_id);
  `);

  // ════════════════════════════════════════════════════════════════════
  //  MEETING INTELLIGENCE LAYER (Strategic Repositioning Sprint 2)
  // ════════════════════════════════════════════════════════════════════
  // Three tables turn free-text meeting transcripts into the structural
  // moat the brief calls out: persistent, longitudinal, attributed
  // internal data that no public chat-LLM workflow can produce.
  //
  //   meeting_facts        — discrete claims extracted from a meeting.
  //                          Each fact is attributed to a speaker (linked
  //                          to persons.id) + topic + verbatim evidence.
  //   stakeholder_positions — derived view: for each (person_id, topic),
  //                          their latest known position with all
  //                          supporting facts. Computed on-write from
  //                          meeting_facts.
  //   pattern_matches      — internal+external pairs the cross-reference
  //                          engine surfaces ("COO said vendor lock-in
  //                          concerns in March + April job posting for
  //                          Vendor Strategy Lead").

  db.exec(`
    CREATE TABLE IF NOT EXISTS meeting_facts (
      id TEXT PRIMARY KEY,
      meeting_id TEXT NOT NULL REFERENCES meeting_history(id) ON DELETE CASCADE,
      bank_key TEXT NOT NULL REFERENCES banks(key) ON DELETE CASCADE,
      speaker_person_id TEXT REFERENCES persons(id),
      speaker_name TEXT,                  -- captured even when no person match
      topic TEXT NOT NULL,                -- canonical topic: budget|vendors|timeline|politics|technical|blockers|other
      position TEXT NOT NULL,             -- the claim — e.g., "concerned about vendor lock-in"
      sentiment TEXT CHECK(sentiment IN ('positive', 'neutral', 'negative', 'mixed')),
      evidence_quote TEXT NOT NULL,       -- verbatim from notes/transcript
      meeting_date TEXT NOT NULL,
      confidence_tier INTEGER DEFAULT 1,  -- meeting facts are tier 1 by default (direct quote)
      extracted_at TEXT DEFAULT (datetime('now')),
      extracted_by TEXT                   -- 'auto' (LLM) | 'ae' (manual)
    );
    CREATE INDEX IF NOT EXISTS idx_meeting_facts_bank ON meeting_facts(bank_key);
    CREATE INDEX IF NOT EXISTS idx_meeting_facts_person ON meeting_facts(speaker_person_id);
    CREATE INDEX IF NOT EXISTS idx_meeting_facts_topic ON meeting_facts(topic);
    CREATE INDEX IF NOT EXISTS idx_meeting_facts_date ON meeting_facts(meeting_date);

    CREATE TABLE IF NOT EXISTS pattern_matches (
      id TEXT PRIMARY KEY,
      bank_key TEXT NOT NULL REFERENCES banks(key) ON DELETE CASCADE,
      internal_fact_id TEXT REFERENCES meeting_facts(id),
      external_signal_id TEXT,            -- deal_signal id
      pattern_type TEXT NOT NULL,         -- 'corroborates' | 'contradicts' | 'evolves'
      summary TEXT NOT NULL,              -- one-line summary of the pattern
      detected_at TEXT DEFAULT (datetime('now')),
      acknowledged_at TEXT,
      acknowledged_by TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_pattern_matches_bank ON pattern_matches(bank_key);
  `);

  // Sprint 2.4 migration — additive columns for the cross-reference engine.
  // These are added separately so reruns on existing DBs don't fail.
  const addColIfMissing = (table, col, ddl) => {
    try { db.exec(`ALTER TABLE ${table} ADD COLUMN ${col} ${ddl}`); } catch { /* exists */ }
  };
  addColIfMissing('pattern_matches', 'content_hash', 'TEXT');                 // idempotency key
  addColIfMissing('pattern_matches', 'confidence', "TEXT DEFAULT 'medium'");  // 'low' | 'medium' | 'high'
  addColIfMissing('pattern_matches', 'time_gap_days', 'INTEGER');             // days between fact and signal
  addColIfMissing('pattern_matches', 'topic', 'TEXT');                        // canonical topic from fact
  addColIfMissing('pattern_matches', 'fact_evidence', 'TEXT');                // verbatim quote snapshot
  addColIfMissing('pattern_matches', 'signal_evidence', 'TEXT');              // signal title snapshot
  try { db.exec(`CREATE UNIQUE INDEX IF NOT EXISTS idx_pattern_matches_hash ON pattern_matches(content_hash) WHERE content_hash IS NOT NULL`); } catch { /* exists */ }

  // Sprint 3.1 — source-grade columns. Grade is independent of confidence_tier:
  //   tier (1/2/3) = how the FACT was derived (Verified / Inferred / Estimated)
  //   grade (A/B/C/D) = the SOURCE's authority
  //     A = primary / bank-originated (press release, regulator, internal doc, AE-logged meeting)
  //     B = tier-1 financial press (Reuters, Bloomberg, FT, WSJ, regional national newspapers)
  //     C = specialized fintech/business press, sector trades, aggregators
  //     D = social media, blogs, unverified third-party, inferred-without-source
  // A high-tier fact from a low-grade source is a yellow flag — both dimensions matter.
  addColIfMissing('deal_signals', 'source_grade', "TEXT CHECK(source_grade IN ('A','B','C','D'))");
  addColIfMissing('deal_signals', 'is_primary_source', 'INTEGER DEFAULT 0');
  addColIfMissing('deal_signals', 'publisher_name', 'TEXT'); // parsed from title tail (" - Reuters" → "Reuters")
  try { db.exec(`CREATE INDEX IF NOT EXISTS idx_deal_signals_grade ON deal_signals(source_grade)`); } catch { /* exists */ }

  // Sprint 5.4 — portfolio saved views (named filters AEs can persist + share)
  db.exec(`
    CREATE TABLE IF NOT EXISTS portfolio_saved_views (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      description TEXT,
      filter_json TEXT NOT NULL,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now'))
    );

    -- ── AE↔VC bridge tables (post-B-series) ──
    -- engagements: tracks VC engagement state per bank. State machine:
    --   none → scoping → discovery → assessment → delivered → closed
    -- One bank can have multiple engagements over time (e.g., assessment + later upgrade).
    CREATE TABLE IF NOT EXISTS engagements (
      id TEXT PRIMARY KEY,
      bank_key TEXT NOT NULL REFERENCES banks(key) ON DELETE CASCADE,
      engagement_type TEXT NOT NULL,  -- 'value_assessment' | 'ignite_inspire' | 'upgrade' | 'roi_only' | 'other'
      state TEXT NOT NULL DEFAULT 'scoping',  -- scoping | discovery | assessment | delivered | closed
      title TEXT,
      kickoff_date TEXT,
      target_close_date TEXT,
      vc_lead TEXT,                   -- VC consultant name (free text)
      ae_lead TEXT,                   -- AE name (free text)
      handoff_snapshot_json TEXT,     -- snapshot of Nova intel at AE→VC handoff
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now')),
      closed_at TEXT,
      outcome TEXT                    -- 'won' | 'lost' | 'no_decision' | null while open
    );
    CREATE INDEX IF NOT EXISTS idx_engagements_bank ON engagements(bank_key);
    CREATE INDEX IF NOT EXISTS idx_engagements_state ON engagements(state);

    -- engagement_artifacts: deliverables produced by VC engagements (ROI, capability,
    -- roadmap, presentation, etc.). When VC publishes a deliverable, deliverableIngest
    -- agent registers it here and emits a Nova signal.
    CREATE TABLE IF NOT EXISTS engagement_artifacts (
      id TEXT PRIMARY KEY,
      engagement_id TEXT NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
      bank_key TEXT NOT NULL,
      artifact_type TEXT NOT NULL,    -- 'roi' | 'capability_assessment' | 'roadmap' | 'presentation' | 'other'
      title TEXT NOT NULL,
      summary TEXT,
      content_url TEXT,               -- file path or URL to artifact
      content_format TEXT,            -- 'html' | 'xlsx' | 'pdf' | 'md' | 'json'
      key_findings_json TEXT,         -- structured findings (e.g., ROI scenarios, capability gaps)
      published_at TEXT DEFAULT (datetime('now')),
      published_by TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_artifacts_engagement ON engagement_artifacts(engagement_id);
    CREATE INDEX IF NOT EXISTS idx_artifacts_bank ON engagement_artifacts(bank_key);

    -- bank_notes: shared comment thread per bank, visible to both AE and VC.
    -- Lightweight collaboration layer — not a full conversation system, just a
    -- way for AE and VC to leave context for each other.
    CREATE TABLE IF NOT EXISTS bank_notes (
      id TEXT PRIMARY KEY,
      bank_key TEXT NOT NULL REFERENCES banks(key) ON DELETE CASCADE,
      author TEXT NOT NULL,           -- name + role e.g. "Oumaima (AE)" or "Mariam (VC)"
      author_role TEXT,               -- 'ae' | 'vc' | 'other' (for filtering)
      body TEXT NOT NULL,
      pinned INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_bank_notes_bank ON bank_notes(bank_key);
    CREATE INDEX IF NOT EXISTS idx_bank_notes_pinned ON bank_notes(pinned);

    -- ── Engagement & Execution Timeline (post-Wave 6) ──
    -- Forward-looking action plan per bank. Generated by deterministic rules
    -- from intelligence inputs (power map, landing zones, account plan,
    -- signals, facts, patterns, drift, intent, opportunity windows,
    -- regulatory pressure). Persisted so AE/VC can track status and
    -- regeneration preserves user customizations.
    CREATE TABLE IF NOT EXISTS engagement_timeline_actions (
      id TEXT PRIMARY KEY,
      bank_key TEXT NOT NULL REFERENCES banks(key) ON DELETE CASCADE,
      generation_run_id TEXT,                -- groups auto-generated actions from one run
      horizon TEXT NOT NULL,                 -- '60d' | '90d'
      category TEXT NOT NULL,                -- 'workshop' | 'stakeholder_outreach' | 'marketing_event' | 'partner_led'
      title TEXT NOT NULL,
      rationale TEXT,
      evidence_json TEXT,                    -- {signals:[], facts:[], persons:[], landing_zones:[], windows:[]}
      status TEXT DEFAULT 'planned',         -- 'planned' | 'in_progress' | 'done' | 'dropped'
      is_auto_generated INTEGER DEFAULT 1,
      owner TEXT,                            -- AE / VC / partner name
      due_date TEXT,
      priority INTEGER DEFAULT 5,            -- 1-10, drives visual order
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now')),
      completed_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_timeline_bank ON engagement_timeline_actions(bank_key);
    CREATE INDEX IF NOT EXISTS idx_timeline_status ON engagement_timeline_actions(status);
    CREATE INDEX IF NOT EXISTS idx_timeline_horizon ON engagement_timeline_actions(horizon);
  `);

  // Seed initial review periods — Q1 + Q2 2026 + Q3 + Q4 2026.
  // Idempotent: INSERT OR IGNORE keys on the period id.
  const seedPeriods = [
    { id: '2026-Q1', starts_at: '2026-01-01', ends_at: '2026-03-31', status: 'closed', closed_at: '2026-04-01' },
    { id: '2026-Q2', starts_at: '2026-04-01', ends_at: '2026-06-30', status: 'active', closed_at: null },
    { id: '2026-Q3', starts_at: '2026-07-01', ends_at: '2026-09-30', status: 'active', closed_at: null },
    { id: '2026-Q4', starts_at: '2026-10-01', ends_at: '2026-12-31', status: 'active', closed_at: null },
  ];
  const periodInsert = db.prepare(
    `INSERT OR IGNORE INTO review_periods (id, starts_at, ends_at, status, closed_at) VALUES (?, ?, ?, ?, ?)`
  );
  for (const p of seedPeriods) periodInsert.run(p.id, p.starts_at, p.ends_at, p.status, p.closed_at);

  // Migration (Stage 2): the original CHECK on signal_category allowed only the
  // first taxonomy: {stakeholder, strategic, competitive, momentum, market, internal}.
  // The Stage 1 classifier emits {stakeholder, strategic, competitive, momentum,
  // market, regulatory} — same 5 + regulatory instead of internal. We need both
  // 'internal' (legacy demo + meeting-derived events) AND 'regulatory' (live news)
  // to be valid. SQLite can't drop a CHECK in place, so recreate the table once.
  // Idempotent: skips if the new constraint is already in place.
  try {
    const schemaInfo = db.prepare("SELECT sql FROM sqlite_master WHERE type='table' AND name='deal_signals'").get();
    const hasRegulatory = schemaInfo?.sql?.includes("'regulatory'");
    if (!hasRegulatory) {
      db.exec('BEGIN');
      db.exec(`
        CREATE TABLE deal_signals_new (
          id TEXT PRIMARY KEY,
          deal_id TEXT NOT NULL,
          signal_category TEXT NOT NULL CHECK(signal_category IN ('stakeholder', 'strategic', 'competitive', 'momentum', 'market', 'internal', 'regulatory')),
          signal_event TEXT NOT NULL,
          title TEXT NOT NULL,
          description TEXT,
          source_url TEXT,
          source_type TEXT CHECK(source_type IN ('linkedin', 'news', 'internal', 'manual', 'meeting')),
          severity TEXT DEFAULT 'info' CHECK(severity IN ('info', 'attention', 'urgent')),
          detected_at TEXT NOT NULL DEFAULT (datetime('now')),
          acknowledged_at TEXT,
          actioned_at TEXT,
          routed_to_plays TEXT DEFAULT '[]',
          triggered_output_ids TEXT DEFAULT '[]',
          action_point TEXT,
          evidence_quote TEXT,
          mentioned_stakeholders TEXT,
          live_signal_id INTEGER,
          relevance_score REAL,
          is_demo INTEGER DEFAULT 0
        )
      `);
      db.exec(`
        INSERT INTO deal_signals_new
        SELECT id, deal_id, signal_category, signal_event, title, description,
               source_url, source_type, severity, detected_at, acknowledged_at,
               actioned_at, routed_to_plays, triggered_output_ids,
               action_point, evidence_quote, mentioned_stakeholders,
               live_signal_id, relevance_score, is_demo
        FROM deal_signals
      `);
      db.exec('DROP TABLE deal_signals');
      db.exec('ALTER TABLE deal_signals_new RENAME TO deal_signals');
      db.exec('CREATE INDEX IF NOT EXISTS idx_deal_signals_deal ON deal_signals(deal_id)');
      db.exec('CREATE INDEX IF NOT EXISTS idx_deal_signals_severity ON deal_signals(severity)');
      db.exec('CREATE INDEX IF NOT EXISTS idx_deal_signals_detected ON deal_signals(detected_at)');
      db.exec("CREATE UNIQUE INDEX IF NOT EXISTS idx_deal_signals_live_id ON deal_signals(deal_id, live_signal_id) WHERE live_signal_id IS NOT NULL");
      db.exec('COMMIT');
      console.log("[db] Relaxed signal_category CHECK to include 'regulatory'");
    }
  } catch (e) {
    db.exec('ROLLBACK');
    console.warn('[db] Failed to relax signal_category constraint:', e.message);
  }

  // Power Maps table (MEDDICC analysis cache)
  db.exec(`
    CREATE TABLE IF NOT EXISTS power_maps (
      id TEXT PRIMARY KEY,
      bank_key TEXT NOT NULL,
      generated_at TEXT DEFAULT (datetime('now')),
      result TEXT NOT NULL,
      persona TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_power_maps_bank ON power_maps(bank_key);

    -- ── Account Plans (cached AI-generated account plan documents) ──
    CREATE TABLE IF NOT EXISTS account_plans (
      id TEXT PRIMARY KEY,
      bank_key TEXT NOT NULL,
      generated_at TEXT DEFAULT (datetime('now')),
      inputs TEXT,
      result TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_account_plans_bank ON account_plans(bank_key);

    -- ── Pipeline Settings (bank status + exclusions) ──
    CREATE TABLE IF NOT EXISTS pipeline_settings (
      bank_key TEXT PRIMARY KEY,
      excluded INTEGER DEFAULT 0,
      status TEXT DEFAULT 'prospect' CHECK(status IN ('prospect', 'discovery', 'qualification', 'proof_of_value', 'negotiation', 'won', 'lost', 'disqualified', 'watching')),
      disqualify_reason TEXT,
      updated_at TEXT DEFAULT (datetime('now'))
    );

    -- ── Deal Outcomes (win/loss tracking for learning loop) ──
    CREATE TABLE IF NOT EXISTS deal_outcomes (
      id TEXT PRIMARY KEY,
      bank_key TEXT NOT NULL,
      outcome TEXT NOT NULL CHECK(outcome IN ('won', 'lost', 'stalled', 'no_decision')),
      arr_value TEXT,
      close_date TEXT,
      win_reasons TEXT,
      loss_reasons TEXT,
      competitor_won TEXT,
      lessons_learned TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_deal_outcomes_bank ON deal_outcomes(bank_key);

    -- ══════════════════════════════════════════════════════════════
    -- Intelligence Layer tables (Sprint 1)
    -- ══════════════════════════════════════════════════════════════

    -- 1. Deal Plays — named intelligence workflows per deal
    CREATE TABLE IF NOT EXISTS deal_plays (
      id TEXT PRIMARY KEY,
      deal_id TEXT NOT NULL,
      play_type TEXT NOT NULL CHECK(play_type IN ('discovery', 'value', 'competitive', 'proposal', 'expansion')),
      status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'paused')),
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now')),
      completed_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_deal_plays_deal ON deal_plays(deal_id);
    CREATE INDEX IF NOT EXISTS idx_deal_plays_status ON deal_plays(status);

    -- 2. Play Outputs — artifacts each play produces
    CREATE TABLE IF NOT EXISTS play_outputs (
      id TEXT PRIMARY KEY,
      play_id TEXT NOT NULL,
      output_type TEXT NOT NULL,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      stakeholder_id TEXT,
      confidence_tier TEXT CHECK(confidence_tier IN ('verified', 'inferred', 'stale')),
      source_ids TEXT DEFAULT '[]',
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now')),
      used_in_meeting_id TEXT,
      feedback TEXT CHECK(feedback IN ('landed', 'missed', 'not_used', 'partially_landed', NULL)),
      FOREIGN KEY (play_id) REFERENCES deal_plays(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_play_outputs_play ON play_outputs(play_id);

    -- 3. Deal Signals — deal-relevant events that trigger play updates
    CREATE TABLE IF NOT EXISTS deal_signals (
      id TEXT PRIMARY KEY,
      deal_id TEXT NOT NULL,
      signal_category TEXT NOT NULL CHECK(signal_category IN ('stakeholder', 'strategic', 'competitive', 'momentum', 'market', 'internal')),
      signal_event TEXT NOT NULL,
      title TEXT NOT NULL,
      description TEXT,
      source_url TEXT,
      source_type TEXT CHECK(source_type IN ('linkedin', 'news', 'internal', 'manual', 'meeting')),
      severity TEXT DEFAULT 'info' CHECK(severity IN ('info', 'attention', 'urgent')),
      detected_at TEXT NOT NULL DEFAULT (datetime('now')),
      acknowledged_at TEXT,
      actioned_at TEXT,
      routed_to_plays TEXT DEFAULT '[]',
      triggered_output_ids TEXT DEFAULT '[]'
    );
    CREATE INDEX IF NOT EXISTS idx_deal_signals_deal ON deal_signals(deal_id);
    CREATE INDEX IF NOT EXISTS idx_deal_signals_severity ON deal_signals(severity);
    CREATE INDEX IF NOT EXISTS idx_deal_signals_detected ON deal_signals(detected_at);

    -- 4. Deal Twin State — computational model of deal health
    CREATE TABLE IF NOT EXISTS deal_twin_state (
      id TEXT PRIMARY KEY,
      deal_id TEXT NOT NULL UNIQUE,
      stakeholder_alignment REAL DEFAULT 50,
      strategic_fit REAL DEFAULT 50,
      competitive_position REAL DEFAULT 50,
      momentum REAL DEFAULT 50,
      value_clarity REAL DEFAULT 50,
      information_completeness REAL DEFAULT 50,
      deal_health_score REAL DEFAULT 50,
      deal_health_trend TEXT DEFAULT 'stable' CHECK(deal_health_trend IN ('improving', 'stable', 'declining')),
      top_risks TEXT DEFAULT '[]',
      recommended_actions TEXT DEFAULT '[]',
      last_calculated_at TEXT NOT NULL DEFAULT (datetime('now')),
      calculation_inputs TEXT DEFAULT '{}'
    );

    -- 5. Deal Twin History — snapshots for trend tracking
    CREATE TABLE IF NOT EXISTS deal_twin_history (
      id TEXT PRIMARY KEY,
      deal_id TEXT NOT NULL,
      snapshot_date TEXT NOT NULL DEFAULT (date('now')),
      deal_health_score REAL,
      stakeholder_alignment REAL,
      strategic_fit REAL,
      competitive_position REAL,
      momentum REAL,
      value_clarity REAL,
      information_completeness REAL
    );
    CREATE INDEX IF NOT EXISTS idx_deal_twin_history_deal ON deal_twin_history(deal_id);

    -- 6. Output Feedback — learning loop from rep usage
    CREATE TABLE IF NOT EXISTS output_feedback (
      id TEXT PRIMARY KEY,
      play_output_id TEXT NOT NULL,
      meeting_id TEXT,
      feedback_type TEXT NOT NULL CHECK(feedback_type IN ('landed', 'missed', 'not_used', 'partially_landed')),
      notes TEXT,
      stakeholder_reaction TEXT CHECK(stakeholder_reaction IN ('positive', 'neutral', 'negative', 'unknown')),
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      FOREIGN KEY (play_output_id) REFERENCES play_outputs(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_output_feedback_output ON output_feedback(play_output_id);

    -- 7. Play Templates — reusable patterns (future Play Builder)
    CREATE TABLE IF NOT EXISTS play_templates (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      description TEXT,
      play_type TEXT NOT NULL,
      bank_segment TEXT,
      deal_pattern TEXT DEFAULT '{}',
      template_config TEXT DEFAULT '{}',
      effectiveness_score REAL DEFAULT 0,
      times_used INTEGER DEFAULT 0,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    -- 8. Template Usage Tracking
    CREATE TABLE IF NOT EXISTS deal_play_template_usage (
      id TEXT PRIMARY KEY,
      deal_id TEXT NOT NULL,
      play_template_id TEXT NOT NULL,
      play_id TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      FOREIGN KEY (play_template_id) REFERENCES play_templates(id),
      FOREIGN KEY (play_id) REFERENCES deal_plays(id) ON DELETE CASCADE
    );
  `);
}

// JSON column sets per table (for auto-parsing)
const JSON_FIELDS = {
  banks: new Set(['data']),
  markets: new Set(['countries', 'data']),
  countries: new Set(['data']),
  qualification: new Set(['data']),
  cx: new Set(['data']),
  competition: new Set(['data']),
  value_selling: new Set(['data']),
  relationships: new Set(['data']),
  meeting_packs: new Set(['result']),
  ai_analyses: new Set(['result']),
  ingestion_log: new Set(['details']),
  landing_zone_matrix: new Set(['matrix', 'plays', 'unconsidered', 'challenges', 'top_zones']),
  discovery_storylines: new Set(['storyline', 'roi_estimate', 'next_steps']),
  brief_feedback: new Set(['sections_used']),
  field_provenance: new Set([]),
  entity_history: new Set([]),
  persons: new Set(['aliases', 'meddicc_roles', 'priorities', 'kpis_of_interest']),
  pain_points: new Set([]),
  landing_zones: new Set(['details']),
  meeting_history: new Set(['attendees', 'key_topics', 'objections_raised', 'commitments_made']),
  power_maps: new Set(['result']),
  account_plans: new Set(['inputs', 'result']),
  deal_outcomes: new Set(['win_reasons', 'loss_reasons']),
  // Intelligence Layer tables
  deal_plays: new Set([]),
  play_outputs: new Set(['source_ids']),
  deal_signals: new Set(['routed_to_plays', 'triggered_output_ids']),
  deal_twin_state: new Set(['top_risks', 'recommended_actions', 'calculation_inputs']),
  deal_twin_history: new Set([]),
  output_feedback: new Set([]),
  play_templates: new Set(['deal_pattern', 'template_config']),
  deal_play_template_usage: new Set([]),
};

/**
 * Parse JSON columns in a row object
 * @param {string} table - table name (for field lookup)
 * @param {object} row - raw row from better-sqlite3
 * @returns {object} row with JSON fields parsed
 */
export function parseRow(table, row) {
  if (!row) return null;
  const fields = JSON_FIELDS[table];
  if (!fields) return row;
  const result = { ...row };
  for (const key of fields) {
    if (typeof result[key] === 'string') {
      try { result[key] = JSON.parse(result[key]); } catch { /* keep as string */ }
    }
  }
  return result;
}

/**
 * Parse all rows from a query
 */
export function parseRows(table, rows) {
  return rows.map(r => parseRow(table, r));
}
