# Pipeline Test Results — NFIS Digital Investor (Feb 20, 2026)

## Test Setup

- **Client:** NFIS (Navy Federal Investment Services)
- **Transcripts:** 4 PDFs converted to markdown (310KB / 5,397 lines total)
- **Orchestrator:** `scripts/orchestrate.py` v1 (Python + claude-agent-sdk)
- **Mode:** `--non-interactive` (auto-approve checkpoints)
- **Model:** claude-sonnet-4-6 (default from agent .md files)

---

## Run 1: Sequential Discovery (Original Code)

| Step | Start | End | Duration | Cost | Turns | Output |
|------|-------|-----|----------|------|-------|--------|
| T1 extraction (112KB, 1793 lines) | 10:10 | 10:19 | **8.7 min** | $1.10 | 9 | 38KB interim |
| T2 extraction (57KB, 970 lines) | 10:19 | 10:26 | **6.8 min** | $0.77 | 7 | 32KB interim |
| T3 extraction (57KB, 1011 lines) | 10:26 | 10:32 | **6.2 min** | $0.72 | 7 | 30KB interim |
| T4 extraction + consolidation (85KB, 1623 lines) | 10:32 | 10:45 | **12.7 min** | $1.88 | 18 | 32KB interim + 57KB checkpoint |
| **Redundant consolidation (STUCK)** | **10:45** | **11:10+** | **27+ min** | **??** | **??** | **Never completed** |
| **Total (killed)** | 10:10 | 11:10 | **62+ min** | **$4.47+** | **41+** | Stuck on consolidation |

### Root Cause: Redundant Consolidation
T4 was told "if this is the last transcript, write the checkpoint." It did — produced a 57KB CHECKPOINT_discovery.md. The orchestrator then ran a SEPARATE consolidation step (`if len(transcripts) > 1`) which was completely redundant. That consolidation agent got stuck trying to write a large file for 27+ minutes before being killed.

---

## Run 2: Parallel Discovery (Fixed Code)

| Step | Start | End | Duration | Cost | Turns | Output |
|------|-------|-----|----------|------|-------|--------|
| T1 extraction (parallel) | 11:20 | 11:30 | 10.0 min | $1.27 | 12 | 36KB interim |
| T2 extraction (parallel) | 11:20 | 11:30 | 9.5 min | $1.00 | 9 | 39KB interim |
| T3 extraction (parallel) | 11:20 | 11:34 | 13.7 min | $1.42 | 10 | 47KB interim |
| T4 extraction (parallel) | 11:20 | 11:34 | 13.7 min | $1.66 | 12 | 49KB interim |
| **All 4 parallel** | **11:20** | **11:34** | **13.7 min** | **$5.35** | **43** | 171KB total interims |
| Consolidation (still slow) | 11:34 | 11:46+ | **12+ min (killed)** | ?? | ?? | Writing checkpoint |

### Improvement: 2.5x faster extraction
Parallel: 13.7 min vs Sequential: 34.5 min = **2.5x speedup** for extraction.

### Still broken: Consolidation
The consolidation step is still extremely slow. Reading 171KB of interim files and writing a ~60KB checkpoint takes 12+ minutes. The agent spends most of its turns generating the large output file.

---

## Problems Identified

### P1: Consolidation is the bottleneck (CRITICAL)
- **What:** Writing a 50-60KB checkpoint from 4 interim files takes 12-27+ minutes
- **Why:** Each API turn can generate ~4-8KB of text. A 60KB checkpoint = 8-15 turns of pure writing. At 30-60s per turn, that's 4-15 min just for output generation.
- **Impact:** Makes the entire discovery phase take 25+ min even with parallel extraction
- **Fix options:**
  a. **Reduce checkpoint size** — Don't consolidate full registers into checkpoint. Instead, write a summary-only checkpoint (top findings, severity rankings, data gaps) at ~5-10KB, keep the 4 interim files as the detailed source.
  b. **Skip consolidation for Phase 2** — Let the Phase 2 finalize agent read the 4 interim files directly instead of a consolidated checkpoint.
  c. **Parallelize the consolidation write** — Split checkpoint into sections written by separate agents.

### P2: Discovery agent chunking overhead (HIGH)
- **What:** Each transcript agent chunks into 400-500 line blocks, reads engagement_intake, checks file sizes with `wc -l`, creates directories, etc.
- **Why:** The discovery agent's system prompt mandates the chunking protocol at 500-line threshold.
- **Impact:** Adds 3-5 turns of overhead per transcript (60-90 seconds)
- **Fix:** Raise chunking threshold. The Read tool handles 2000 lines natively. A 1000-line transcript doesn't need chunking. Set threshold to 1500+ lines.

### P3: Rate limit events crash SDK (FIXED)
- **What:** `claude-agent-sdk` v0.1.39 throws `MessageParseError` on `rate_limit_event` messages
- **Why:** SDK's `parse_message()` doesn't handle this message type
- **Impact:** Pipeline crashes on first rate limit
- **Fix:** Monkey-patched in orchestrate.py. Works but fragile. Should be reported to SDK team.

### P4: Parallel agents are slower per-agent than sequential (MEDIUM)
- **What:** T1 took 8.7 min sequential vs 10.0 min parallel. T2: 6.8 vs 9.5 min.
- **Why:** 4 simultaneous agents compete for API rate limits, causing more rate_limit_events and retries. Each individual agent is ~20-40% slower, but wall-clock time is still 2.5x better.
- **Impact:** The parallel speedup is 2.5x instead of theoretical 4x
- **Fix:** Acceptable trade-off. Could batch to 2-at-a-time for lower-tier API plans.

### P5: Domain detection was wrong (FIXED)
- **What:** Detected "sme" instead of "investing" because keyword scan matched "sme" before "investing"
- **Fix:** Now looks for explicit `**Domain:**` field in intake first, falls back to keyword scan with better priority order.

### P6: Agent writes are too verbose (HIGH)
- **What:** Each transcript agent writes 36-49KB interim files with full register tables, extensive quotes, and interpretation notes
- **Why:** The discovery agent system prompt demands 6 full registers per transcript with exact quotes, cross-references, etc.
- **Impact:** 4 × 45KB = 180KB of interim data that then needs consolidation. Writing 45KB takes 6-8 turns.
- **Fix:** For the interim extraction phase, produce a leaner format (evidence IDs + key findings, no full register tables). Save the full register format for the consolidated checkpoint.

### P7: PYTHONUNBUFFERED required for monitoring (LOW)
- **What:** Without PYTHONUNBUFFERED=1, no output appears until pipeline completes
- **Fix:** Already using it in the command. Should add `sys.stdout.reconfigure(line_buffering=True)` at top of script.

### P8: No progress callback from SDK (MEDIUM)
- **What:** Agent tool calls (Read, Write, Bash) are not visible in our log. We only see TextBlock messages.
- **Why:** The SDK yields AssistantMessage with TextBlock and ToolUseBlock, but our logger only prints TextBlock.
- **Impact:** Pipeline appears silent for minutes while agent reads/writes files
- **Fix:** Also log ToolUseBlock messages (show tool name and first arg).

---

## Timing Projections

### Current (with parallel extraction, consolidation still slow)
| Phase | Estimated |
|-------|-----------|
| Discovery extraction (parallel) | 14 min |
| Discovery consolidation | 12 min |
| Discovery Phase 2 (finalize) | 8 min |
| **Discovery Total** | **34 min** |
| Parallel Block A (5 agents × 2 phases) | 16 min |
| Roadmap | 8 min |
| Assembly (3 phases) | 20 min |
| HTML + Excel | 15 min |
| Validation | 2 min |
| **Pipeline Total** | **~95 min** |

### Target (with all fixes applied)
| Phase | Estimated |
|-------|-----------|
| Discovery extraction (parallel, lean output) | 8 min |
| Discovery consolidation (summary checkpoint) | 3 min |
| Discovery Phase 2 (reads interims directly) | 5 min |
| **Discovery Total** | **16 min** |
| Parallel Block A | 12 min |
| Roadmap | 6 min |
| Assembly (3 phases) | 15 min |
| HTML + Excel (parallel) | 10 min |
| Validation | 2 min |
| **Pipeline Total** | **~45 min** |

### Stretch (with aggressive optimizations)
- Assembly single-pass (no intermediate checkpoints): -8 min
- ROI reads discovery directly (skip Phase 2): -5 min
- **Possible: ~32 min**

---

## Cost Analysis (Run 2)

| Agent | Cost |
|-------|------|
| Discovery T1 (parallel) | $1.27 |
| Discovery T2 (parallel) | $1.00 |
| Discovery T3 (parallel) | $1.42 |
| Discovery T4 (parallel) | $1.66 |
| Discovery consolidation (partial) | ~$0.80 |
| **Discovery subtotal** | **~$6.15** |
| Parallel Block A (5 agents × 2 phases, projected) | ~$8.00 |
| Roadmap + Assembly + HTML/Excel (projected) | ~$6.00 |
| **Estimated total pipeline cost** | **~$20** |

All using Sonnet. Switching discovery to Haiku could reduce cost to ~$3 for that phase.
