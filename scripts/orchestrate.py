#!/usr/bin/env python3
"""
Cortex Pipeline Orchestrator — Value Consulting Assessment Pipeline.

Supports interactive (consultant checkpoints), express, and non-interactive modes.
Non-interactive mode includes performance optimizations:
- Single-phase Block A (eliminates P1 sync barrier)
- Overlapping stages (Roadmap + Excel in parallel)
- 3-way parallel Assembly sharding (Acts 1-2 / 3-5 / 6-7)
- Per-agent timeouts and output validation
- 6-partial HTML generation with template assembly

Usage:
    python scripts/orchestrate.py <engagement_dir>
    python scripts/orchestrate.py --express <engagement_dir>
    python scripts/orchestrate.py --resume-from <step> <engagement_dir>
    python scripts/orchestrate.py --dry-run <engagement_dir>
    python scripts/orchestrate.py --non-interactive <engagement_dir>
"""

import asyncio
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

# Ensure output appears immediately even without PYTHONUNBUFFERED
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
from pathlib import Path
from typing import Optional

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)
# NOTE: SDK v0.1.39 patched directly to handle unknown message types
# (e.g., rate_limit_event). See message_parser.py case _ and client.py yield.
# When SDK updates to handle this natively, the direct patches can be removed.

# ─── Paths ────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
COMMANDS_DIR = REPO_ROOT / ".claude" / "commands"
KNOWLEDGE_DIR = REPO_ROOT / "knowledge"

# ─── Colors for terminal output ───────────────────────────────────────────────

class C:
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    DIM = "\033[2m"
    RESET = "\033[0m"

# ─── Helpers ──────────────────────────────────────────────────────────────────

def log(msg: str, color: str = ""):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{C.DIM}{ts}{C.RESET} {color}{msg}{C.RESET}")


def log_step(step: str, desc: str):
    print(f"\n{C.BOLD}{C.CYAN}{'═' * 60}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  {step}: {desc}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}{'═' * 60}{C.RESET}\n")


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def file_exists(path: Path, min_size: int = 0) -> bool:
    return path.exists() and path.stat().st_size > min_size


def glob_files(pattern: str, directory: Path) -> list[Path]:
    return sorted(directory.glob(pattern))


def parse_agent_md(agent_name: str) -> tuple[str, str]:
    """Read agent .md file, return (system_prompt_body, model)."""
    path = AGENTS_DIR / f"{agent_name}.md"
    text = read_file(path)
    # Strip YAML frontmatter
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2].strip()
            # Extract model from frontmatter
            model_match = re.search(r"^model:\s*(\w+)", frontmatter, re.MULTILINE)
            model = model_match.group(1) if model_match else "sonnet"
            return body, model
    return text, "sonnet"


def assert_file_exists(path: Path, agent_name: str, min_size: int = 0):
    if not file_exists(path, min_size):
        size = path.stat().st_size if path.exists() else 0
        raise RuntimeError(
            f"VALIDATION FAILED: {agent_name} did not produce {path.name} "
            f"(exists={path.exists()}, size={size}, min_required={min_size})"
        )
    log(f"  ✓ {path.name} ({path.stat().st_size:,} bytes)", C.GREEN)


def _sum_costs(results) -> float:
    """Sum costs from agent results, handling exceptions in gather results."""
    total = 0.0
    for r in results:
        if isinstance(r, ResultMessage) and r.total_cost_usd:
            total += r.total_cost_usd
    return total


# ─── Resilient Query Wrapper ──────────────────────────────────────────────────

async def _resilient_query(prompt: str, options: ClaudeAgentOptions, label: str):
    """Wrap SDK query() for resilience (e.g., filtering, retry logic)."""
    async for message in query(prompt=prompt, options=options):
        yield message


# ─── Agent Runner ─────────────────────────────────────────────────────────────

async def run_agent(
    agent_name: str,
    prompt: str,
    cwd: Path,
    model: str = "sonnet",
    max_turns: int = 50,
    label: str = "",
) -> ResultMessage:
    """Run a single agent via the SDK. Returns the ResultMessage."""
    display = label or agent_name
    start = time.time()
    log(f"  ▶ Launching {display}...", C.YELLOW)

    system_prompt, agent_model = parse_agent_md(agent_name)
    use_model = model or agent_model

    # V5: Inject tool constraint into system prompt to prevent Task tool usage
    system_prompt = (
        "IMPORTANT: You MUST NOT use the Task tool to spawn sub-agents. "
        "Do all work directly using Read, Write, Edit, Bash, Glob, Grep. "
        "Using Task wastes turns and risks hitting output limits.\n\n"
        + system_prompt
    )

    # Map model names to Claude model IDs
    model_map = {
        "sonnet": "claude-sonnet-4-6",
        "opus": "claude-opus-4-6",
        "haiku": "claude-haiku-4-5-20251001",
    }
    model_id = model_map.get(use_model, use_model)

    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep",
                        "WebSearch", "WebFetch"],
        permission_mode="bypassPermissions",
        cwd=str(cwd),
        model=model_id,
        max_turns=max_turns,
        # Unset CLAUDECODE to allow nested sessions when running inside Claude Code
        env={"CLAUDECODE": ""},
    )

    result = None
    async for message in _resilient_query(prompt, options, display):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock) and block.text.strip():
                    preview = block.text.strip()[:120].replace("\n", " ")
                    log(f"  [{display}] {preview}", C.DIM)
                elif isinstance(block, ToolUseBlock):
                    tool_preview = str(block.input)[:80] if block.input else ""
                    log(f"  [{display}] >> {block.name}({tool_preview})", C.DIM)
        elif isinstance(message, ResultMessage):
            result = message

    elapsed = time.time() - start
    cost = result.total_cost_usd if result and result.total_cost_usd else 0
    turns = result.num_turns if result else 0
    log(f"  ✓ {display} done — {elapsed:.0f}s, {turns} turns, ${cost:.3f}", C.GREEN)
    return result


# ─── Checkpoint Management ────────────────────────────────────────────────────

def present_checkpoint(
    agent_name: str,
    outputs_dir: Path,
    express: bool = False,
    non_interactive: bool = False,
    cp_suffix: str = "",
) -> str:
    """Read checkpoint file, present to consultant (or auto-approve), write approval."""
    cp_name = f"CHECKPOINT_{agent_name}{cp_suffix}"
    cp_file = outputs_dir / f"{cp_name}.md"

    if not cp_file.exists():
        log(f"  ⚠ No checkpoint file: {cp_file.name}", C.YELLOW)
        return "No checkpoint produced — proceeding."

    content = read_file(cp_file)

    if express or non_interactive:
        mode = "EXPRESS" if express else "NON-INTERACTIVE"
        log(f"  ⚡ {mode}: Auto-approving {cp_name}", C.YELLOW)
        # Print summary so Claude Code can show it to consultant
        summary_lines = content.strip().split("\n")[:20]
        print(f"\n  [CHECKPOINT SUMMARY: {agent_name}{cp_suffix}]")
        for line in summary_lines:
            print(f"  | {line}")
        if len(content.strip().split("\n")) > 20:
            print(f"  | ... ({len(content)} chars total)")
        print()
        approval = f"{mode}: Auto-approved with agent recommendations."
    else:
        print(f"\n{C.BOLD}{'─' * 60}{C.RESET}")
        print(f"{C.BOLD}CHECKPOINT: {agent_name}{cp_suffix}{C.RESET}")
        print(f"{'─' * 60}")
        # Show full checkpoint content
        print(content)
        print(f"{'─' * 60}")
        approval = input(f"\n{C.BOLD}Your feedback (or press Enter to approve): {C.RESET}")
        if not approval.strip():
            approval = "APPROVED — proceed with recommendations."

    approval_file = outputs_dir / f"{cp_name}_APPROVED.md"
    write_file(approval_file, f"# {cp_name} — Approved\n\n{approval}\n")
    return approval


def present_checkpoints_batched(
    agents: list[str],
    outputs_dir: Path,
    express: bool = False,
    non_interactive: bool = False,
) -> dict[str, str]:
    """Present multiple checkpoints at once. Returns dict of agent->approval."""
    approvals = {}

    if express or non_interactive:
        for agent in agents:
            approvals[agent] = present_checkpoint(agent, outputs_dir, express=True, non_interactive=non_interactive)
        return approvals

    print(f"\n{C.BOLD}{C.CYAN}{'═' * 60}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  CHECKPOINTS READY: {len(agents)} agents completed{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}{'═' * 60}{C.RESET}")

    for agent in agents:
        cp_file = outputs_dir / f"CHECKPOINT_{agent}.md"
        if cp_file.exists():
            content = read_file(cp_file)
            print(f"\n{C.BOLD}── {agent} ──{C.RESET}")
            # Show first 800 chars as summary
            print(content[:800])
            if len(content) > 800:
                print(f"{C.DIM}  ... ({len(content)} chars total){C.RESET}")

    print(f"\n{'─' * 60}")
    feedback = input(
        f"{C.BOLD}Type 'approve all' or provide feedback per agent: {C.RESET}"
    )

    if "approve all" in feedback.lower() or not feedback.strip():
        for agent in agents:
            approval_file = outputs_dir / f"CHECKPOINT_{agent}_APPROVED.md"
            write_file(approval_file, f"# CHECKPOINT_{agent} — Approved\n\nAPPROVED — proceed.\n")
            approvals[agent] = "APPROVED"
    else:
        # Individual feedback mode
        for agent in agents:
            agent_feedback = input(f"  Feedback for {agent} (Enter=approve): ")
            if not agent_feedback.strip():
                agent_feedback = "APPROVED — proceed."
            approval_file = outputs_dir / f"CHECKPOINT_{agent}_APPROVED.md"
            write_file(approval_file, f"# CHECKPOINT_{agent} — Approved\n\n{agent_feedback}\n")
            approvals[agent] = agent_feedback

    return approvals


# ─── Pipeline Steps ───────────────────────────────────────────────────────────

def _generate_discovery_checkpoint(outputs_dir: Path, transcripts: list[Path]) -> Path:
    """Generate checkpoint by concatenating interim summaries. No LLM needed."""
    checkpoint_path = outputs_dir / "CHECKPOINT_discovery.md"
    sections = []
    sections.append("# Discovery Checkpoint\n")
    sections.append(f"**Transcripts processed:** {len(transcripts)}\n")

    for i, t in enumerate(transcripts, 1):
        interim = outputs_dir / f"interim_transcript_{i}.md"
        if interim.exists():
            content = interim.read_text()
            # Extract Summary section (first lines until ## Evidence Table)
            lines = content.split('\n')
            summary_lines = []
            for line in lines:
                if line.startswith('## Evidence') or line.startswith('## Pain') or len(summary_lines) > 40:
                    break
                summary_lines.append(line)
            sections.append(f"\n---\n## Transcript {i}: {t.name}\n")
            sections.append('\n'.join(summary_lines))
            sections.append(f"\n*Full interim: interim_transcript_{i}.md ({interim.stat().st_size:,} bytes)*\n")

    sections.append("\n---\n## Consultant Action Required\n")
    sections.append("Review the summaries above. Full interim files are available for detail.\n")
    sections.append("Approve to proceed with finalize phase, or provide feedback.\n")

    checkpoint_path.write_text('\n'.join(sections))
    log(f"  ✓ Checkpoint generated ({checkpoint_path.stat().st_size:,} bytes)", C.GREEN)
    return checkpoint_path


# Lean extraction format instructions shared across single and multi-transcript paths
_LEAN_FORMAT = """
IMPORTANT — Write findings in this LEAN structured format:

## Summary
[3-5 bullet points: the most important findings from this transcript]

## Evidence Table
| ID | Category | Finding | Severity | Line Ref |
(One-line findings only. No full quotes — just reference the line number.)

## Pain Points
| ID | Description | Impact | Confidence |

## Metrics
| Name | Value | Source Line |

## Stakeholder Positions
| Name/Role | Key Stance |

## Data Gaps
[Bullet list of missing data or unanswered questions]

TARGET SIZE: 8-15KB. Do NOT include source quotes, interpretation notes, or verbose descriptions.
Do NOT write multi-line cells. Keep every table row on ONE line.
"""


async def step_discovery(
    engagement_dir: Path,
    outputs_dir: Path,
    express: bool,
    non_interactive: bool = False,
) -> dict:
    """Run Discovery: parallel lean extraction -> Python checkpoint -> finalize from interims."""
    start = time.time()
    cost = 0.0
    inputs_dir = engagement_dir / "inputs"
    transcripts = sorted(inputs_dir.glob("transcript_*.md"))
    intake = inputs_dir / "engagement_intake.md"

    if not transcripts:
        log("  ⚠ No transcripts found in inputs/", C.YELLOW)
        return {"elapsed": 0, "cost": 0}

    log(f"  Found {len(transcripts)} transcript(s)")

    if len(transcripts) == 1:
        # Single transcript: lean extraction -> Python checkpoint
        prompt = f"""PHASE DIRECTIVE: Phase 1 of 2
Engagement directory: {engagement_dir}

Read and process this transcript: {transcripts[0]}
Read the engagement context: {intake}

Extract evidence items, pain points, metrics, and stakeholder intelligence.
Write your findings to: {outputs_dir}/interim_transcript_1.md
{_LEAN_FORMAT}
"""
        result = await run_agent(
            "discovery-transcript-interpreter", prompt,
            cwd=engagement_dir,
            label="Discovery (1 transcript)",
            max_turns=15,
        )
        cost += result.total_cost_usd if result and result.total_cost_usd else 0
    else:
        # Multiple transcripts: extract ALL in parallel with lean format
        log(f"  Launching {len(transcripts)} transcript extractions in parallel...")
        extract_tasks = []
        for i, transcript in enumerate(transcripts, 1):
            prompt = f"""PHASE DIRECTIVE: Phase 1 of 2 — Transcript {i} of {len(transcripts)}
Engagement directory: {engagement_dir}

Read and process ONLY this transcript: {transcript}
Read the engagement context: {intake}

Extract evidence items, pain points, metrics, and stakeholder intelligence.
Write your findings ONLY to: {outputs_dir}/interim_transcript_{i}.md

Do NOT write a checkpoint file. Do NOT read other transcripts or interim files.
Focus only on this one transcript. Write the interim file and stop.
{_LEAN_FORMAT}
"""
            extract_tasks.append(run_agent(
                "discovery-transcript-interpreter", prompt,
                cwd=engagement_dir,
                label=f"Discovery (T{i}/{len(transcripts)})",
                max_turns=15,
            ))

        # Fire all transcript extractions simultaneously
        results = await asyncio.gather(*extract_tasks, return_exceptions=True)
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                log(f"  ✗ Transcript {i} extraction FAILED: {result}", C.RED)
        cost += _sum_costs(results)

    # Generate checkpoint in Python (no LLM) — instant
    _generate_discovery_checkpoint(outputs_dir, transcripts)

    # Checkpoint review — T2 FIX: was express=False, now express=express
    present_checkpoint("discovery", outputs_dir, express=express, non_interactive=non_interactive)

    # Phase 2: Finalize registers — reads interims directly (NOT original transcripts)
    interim_files = sorted(outputs_dir.glob("interim_transcript_*.md"))
    interim_list = chr(10).join(f'- {f}' for f in interim_files)

    prompt = f"""PHASE DIRECTIVE: Phase 2 of 2 — Finalize Registers
Engagement directory: {engagement_dir}

Read the consultant approval: {outputs_dir}/CHECKPOINT_discovery_APPROVED.md

Then read ALL interim files for detailed evidence:
{interim_list}

De-duplicate findings across transcripts (same point from multiple stakeholders = higher confidence).
Incorporate any consultant feedback from the approval file.

Do NOT read the original transcript files — the interims contain all extracted data you need.

Produce these REQUIRED final output files (keep each file concise, under 20KB):
- {outputs_dir}/evidence_register.md — consolidated evidence with IDs, categories, findings, severity
- {outputs_dir}/pain_points.md — de-duplicated pain points ranked by impact
- {outputs_dir}/metrics.md — all quantitative data extracted
- {outputs_dir}/stakeholder_intelligence.md — key stakeholder positions and alignment

You MUST write all four files. Do NOT write journal entries or update other files.
"""
    # T1 FIX: added max_turns=15
    result = await run_agent(
        "discovery-transcript-interpreter", prompt,
        cwd=engagement_dir,
        label="Discovery (finalize)",
        max_turns=15,
    )
    cost += result.total_cost_usd if result and result.total_cost_usd else 0

    # Validate
    assert_file_exists(outputs_dir / "evidence_register.md", "Discovery")
    assert_file_exists(outputs_dir / "pain_points.md", "Discovery")
    assert_file_exists(outputs_dir / "metrics.md", "Discovery")

    return {"elapsed": time.time() - start, "cost": cost}


async def step_parallel_block_a(
    engagement_dir: Path,
    outputs_dir: Path,
    express: bool,
    domain: str,
    non_interactive: bool = False,
) -> dict:
    """Run 5 agents in parallel after Discovery: JB, MC, Cap, ROI, Bench.

    S1: In non-interactive mode, uses single-phase (combined P1+P2) per agent
    to eliminate the P1 synchronization barrier and context reload overhead.
    Interactive mode preserves the existing P1 -> checkpoint -> P2 flow.
    """
    start = time.time()
    cost = 0.0
    inputs_dir = engagement_dir / "inputs"
    intake = inputs_dir / "engagement_intake.md"

    # Shared input context for all agents
    shared_context = f"""Engagement directory: {engagement_dir}
Read these discovery outputs before starting:
- {outputs_dir}/evidence_register.md
- {outputs_dir}/pain_points.md
- {outputs_dir}/metrics.md
- {outputs_dir}/stakeholder_intelligence.md
Engagement intake: {intake}
Domain: {domain}
"""

    if non_interactive:
        # ── S1: SINGLE-PHASE (non-interactive) ──────────────────────────
        # Each agent runs ONE session: analyze -> checkpoint (audit) -> final output
        # No pause, no re-launch, no context reload

        log_step("2", "PARALLEL BLOCK A — Single-Phase (5 agents, non-interactive)")

        jb_prompt = f"""PHASE DIRECTIVE: Single-phase (non-interactive)
{shared_context}

Also read domain journey templates: knowledge/domains/{domain}/journey_maps.md
Also read domain personas: knowledge/domains/{domain}/personas.md

OUTPUT DISCIPLINE:
- Do NOT explore the filesystem beyond the listed input files.
- If a file doesn't exist, skip it and proceed — do NOT retry.
- Write ONLY the required output files listed below.

STEP 1 — Analysis & Checkpoint:
Analyze evidence density across customer journeys. Recommend the top 3-5
journeys for mapping based on evidence volume and value leakage potential.
Write checkpoint to: {outputs_dir}/CHECKPOINT_journey-builder.md (for audit trail)

STEP 2 — Final Output (continue immediately, do NOT stop):
Build detailed journey swimlane maps with value leakage quantification.
Produce future-state Backbase-enabled swimlanes.

REQUIRED OUTPUT FILES:
- {outputs_dir}/journey_maps.json
- {outputs_dir}/journey_maps_summary.md
Do NOT write journal entries or update other files.
"""

        mc_prompt = f"""PHASE DIRECTIVE: Single-phase (non-interactive)
{shared_context}

OUTPUT DISCIPLINE:
- Do NOT explore the filesystem beyond the listed input files.
- If a file doesn't exist, skip it and proceed — do NOT retry.
- Write ONLY the required output files listed below.
- TURN BUDGET: You have ~30 turns total. RESERVE your last 5 turns for writing
  output files. Stop ALL web research by turn 20 and begin writing.
  Producing no output file is a FAILURE — partial research with an output file
  is always better than thorough research with no output.

STEP 1 — Analysis & Checkpoint:
Research market context for this engagement. Cover:
- Module 1: Client financial metrics (search for annual reports)
- Module 2: Competitive landscape
- Module 3: Industry benchmarks and CX trends
Write checkpoint to: {outputs_dir}/CHECKPOINT_market-context.md (for audit trail)

STEP 2 — Final Output (continue immediately, do NOT stop):
Finalize the market context brief with all validated findings.

REQUIRED OUTPUT FILES:
- {outputs_dir}/market_context_validated.md
Do NOT write journal entries or update other files.
"""

        cap_prompt = f"""PHASE DIRECTIVE: Single-phase (non-interactive)
{shared_context}

Also read: knowledge/standards/capability_taxonomy_{domain}.md (if exists)
Fallback: knowledge/standards/capability_taxonomy.md

OUTPUT DISCIPLINE:
- Do NOT explore the filesystem beyond the listed input files.
- If a file doesn't exist, skip it and proceed — do NOT retry.
- Write ONLY the required output files listed below.

STEP 1 — Analysis & Checkpoint:
Build the problem map from discovery evidence. Identify capability gaps
and propose assessment scope.
Write checkpoint to: {outputs_dir}/CHECKPOINT_capability.md (for audit trail)

STEP 2 — Final Output (continue immediately, do NOT stop):
Score maturity (1-5) for each capability. Build the F/M/B heatmap.
Write detailed drill-downs per capability.

REQUIRED OUTPUT FILES:
- {outputs_dir}/capability_assessment.md
Do NOT write journal entries or update other files.
"""

        roi_prompt = f"""PHASE DIRECTIVE: Single-phase (non-interactive)
{shared_context}

Also read: knowledge/domains/{domain}/benchmarks.md
Also read: knowledge/domains/{domain}/roi_levers.md (if exists)

OUTPUT DISCIPLINE:
- Do NOT explore the filesystem beyond the listed input files.
- If a cross-reference file doesn't exist yet, proceed WITHOUT it — do NOT wait or retry.
- Write ONLY the required output files listed below.

STEP 1 — Analysis & Checkpoint:
Scan the evidence register for lifecycle stage distribution.
Map evidence to potential value levers. Propose lever candidates
and initial assumptions.
Write checkpoint to: {outputs_dir}/CHECKPOINT_roi_CP1.md (for audit trail)

STEP 2 — Final Output (continue immediately, do NOT stop):
OPTIONAL cross-references (try ONCE, skip if not found — do NOT retry):
- {outputs_dir}/capability_assessment.md
- {outputs_dir}/market_context_validated.md
- {outputs_dir}/benchmarks_validated.md

Build the full financial model with 3 scenarios (conservative/base/aspirational).
Run sensitivity analysis on top assumptions.

REQUIRED OUTPUT FILES (you MUST produce BOTH):
- {outputs_dir}/roi_report.md
- {outputs_dir}/roi_config.json
Do NOT write journal entries or update other files.
"""

        bench_prompt = f"""PHASE DIRECTIVE: Single-phase (non-interactive)
{shared_context}

Also read: knowledge/domains/{domain}/benchmarks.md

OUTPUT DISCIPLINE:
- Do NOT explore the filesystem beyond the listed input files.
- If a file doesn't exist, skip it and proceed — do NOT retry.
- Write ONLY the required output files listed below.

STEP 1 — Analysis & Checkpoint:
Curate domain and regional benchmarks relevant to this engagement.
Rate confidence (High/Medium/Low) and provide sources.
Write checkpoint to: {outputs_dir}/CHECKPOINT_benchmark.md (for audit trail)

STEP 2 — Final Output (continue immediately, do NOT stop):
Finalize benchmarks with source citations and confidence ratings.

REQUIRED OUTPUT FILES:
- {outputs_dir}/benchmarks_validated.md
Do NOT write journal entries or update other files.
"""

        # Fire all 5 simultaneously — single-phase with agent-specific turn caps
        # V5: Per-agent timeout of 40 min to prevent hung agents blocking the pipeline
        BLOCK_A_TIMEOUT = 40 * 60  # 40 minutes

        async def _timed_agent(name, prompt, label, max_turns):
            """Wrap agent in timeout — returns result or raises TimeoutError."""
            try:
                return await asyncio.wait_for(
                    run_agent(name, prompt, engagement_dir,
                              label=label, max_turns=max_turns),
                    timeout=BLOCK_A_TIMEOUT,
                )
            except asyncio.TimeoutError:
                log(f"  ✗ {label} TIMED OUT after {BLOCK_A_TIMEOUT//60} min", C.RED)
                raise

        results = await asyncio.gather(
            _timed_agent("journey-builder", jb_prompt, "Journey Builder", 30),
            _timed_agent("market-context-researcher", mc_prompt, "Market Context", 30),
            _timed_agent("capability-assessment", cap_prompt, "Capability", 25),
            _timed_agent("roi-business-case-builder", roi_prompt, "ROI", 30),
            _timed_agent("benchmark-librarian", bench_prompt, "Benchmark", 25),
            return_exceptions=True,
        )

        # V5: Validate that each agent produced its required output files
        agent_labels = ["Journey Builder", "Market Context", "Capability", "ROI", "Benchmark"]
        required_files = {
            "Journey Builder": ["journey_maps.json", "journey_maps_summary.md"],
            "Market Context": ["market_context_validated.md"],
            "Capability": ["capability_assessment.md"],
            "ROI": ["roi_report.md", "roi_config.json"],
            "Benchmark": ["benchmarks_validated.md"],
        }
        for label, result in zip(agent_labels, results):
            if isinstance(result, Exception):
                log(f"  ✗ {label} FAILED: {result}", C.RED)
            else:
                # Check required output files exist
                for fname in required_files.get(label, []):
                    fpath = outputs_dir / fname
                    if not fpath.exists() or fpath.stat().st_size < 100:
                        log(f"  ⚠ {label}: missing or empty output {fname}", C.YELLOW)

        cost += _sum_costs(results)

    else:
        # ── INTERACTIVE: Keep existing P1 -> checkpoint -> P2 flow ───────

        # ── Phase 1: Launch all 5 simultaneously ─────────────────────────
        log_step("2A", "PARALLEL BLOCK A — Phase 1 (5 agents simultaneously)")

        jb_prompt = f"""PHASE DIRECTIVE: Phase 1 of 2
{shared_context}

Also read domain journey templates: knowledge/domains/{domain}/journey_maps.md
Also read domain personas: knowledge/domains/{domain}/personas.md

Analyze evidence density across customer journeys. Recommend the top 3-5
journeys for mapping based on evidence volume and value leakage potential.

Write: {outputs_dir}/CHECKPOINT_journey-builder.md
"""

        mc_prompt = f"""PHASE DIRECTIVE: Phase 1 of 2
{shared_context}

Research market context for this engagement. Cover:
- Module 1: Client financial metrics (search for annual reports)
- Module 2: Competitive landscape
- Module 3: Industry benchmarks and CX trends

Write: {outputs_dir}/CHECKPOINT_market-context.md
"""

        cap_prompt = f"""PHASE DIRECTIVE: Phase 1 of 2
{shared_context}

Also read: knowledge/standards/capability_taxonomy_{domain}.md (if exists)
Fallback: knowledge/standards/capability_taxonomy.md

Build the problem map from discovery evidence. Identify capability gaps
and propose assessment scope.

Write: {outputs_dir}/CHECKPOINT_capability.md
"""

        roi_prompt = f"""PHASE DIRECTIVE: Phase 1 of 2
{shared_context}

Also read: knowledge/domains/{domain}/benchmarks.md
Also read: knowledge/domains/{domain}/roi_levers.md (if exists)

Scan the evidence register for lifecycle stage distribution.
Map evidence to potential value levers. Propose lever candidates
and initial assumptions.

Write: {outputs_dir}/CHECKPOINT_roi_CP1.md
"""

        bench_prompt = f"""PHASE DIRECTIVE: Phase 1 of 2
{shared_context}

Also read: knowledge/domains/{domain}/benchmarks.md

Curate domain and regional benchmarks relevant to this engagement.
Rate confidence (High/Medium/Low) and provide sources.

Write: {outputs_dir}/CHECKPOINT_benchmark.md
"""

        # Fire all 5 simultaneously
        results = await asyncio.gather(
            run_agent("journey-builder", jb_prompt, engagement_dir, label="Journey Builder P1"),
            run_agent("market-context-researcher", mc_prompt, engagement_dir, label="Market Context P1"),
            run_agent("capability-assessment", cap_prompt, engagement_dir, label="Capability P1"),
            run_agent("roi-business-case-builder", roi_prompt, engagement_dir, label="ROI P1"),
            run_agent("benchmark-librarian", bench_prompt, engagement_dir, label="Benchmark P1"),
            return_exceptions=True,
        )

        agent_names = ["journey-builder", "market-context", "capability", "roi_CP1", "benchmark"]
        for name, result in zip(agent_names, results):
            if isinstance(result, Exception):
                log(f"  ✗ {name} Phase 1 FAILED: {result}", C.RED)
        cost += _sum_costs(results)

        # ── Checkpoints (batched) ────────────────────────────────────────
        checkpoint_agents = ["journey-builder", "market-context", "capability", "roi_CP1", "benchmark"]
        available = [a for a in checkpoint_agents if (outputs_dir / f"CHECKPOINT_{a}.md").exists()]
        present_checkpoints_batched(available, outputs_dir, express=express, non_interactive=non_interactive)

        # ── Phase 2: Launch all 5 again ──────────────────────────────────
        log_step("2B", "PARALLEL BLOCK A — Phase 2 (5 agents simultaneously)")

        jb2_prompt = f"""PHASE DIRECTIVE: Phase 2 of 2
{shared_context}

Read approved checkpoint: {outputs_dir}/CHECKPOINT_journey-builder_APPROVED.md
Read draft checkpoint: {outputs_dir}/CHECKPOINT_journey-builder.md

Build detailed journey swimlane maps with value leakage quantification.
Produce future-state Backbase-enabled swimlanes.

REQUIRED OUTPUT FILES:
- {outputs_dir}/journey_maps.json
- {outputs_dir}/journey_maps_summary.md
"""

        mc2_prompt = f"""PHASE DIRECTIVE: Phase 2 of 2
{shared_context}

Read approved checkpoint: {outputs_dir}/CHECKPOINT_market-context_APPROVED.md
Read draft checkpoint: {outputs_dir}/CHECKPOINT_market-context.md

Finalize the market context brief with all validated findings.

REQUIRED OUTPUT FILES:
- {outputs_dir}/market_context_validated.md
"""

        cap2_prompt = f"""PHASE DIRECTIVE: Phase 2 of 2
{shared_context}

Read approved checkpoint: {outputs_dir}/CHECKPOINT_capability_APPROVED.md
Read draft checkpoint: {outputs_dir}/CHECKPOINT_capability.md

Score maturity (1-5) for each capability. Build the F/M/B heatmap.
Write detailed drill-downs per capability.

REQUIRED OUTPUT FILES:
- {outputs_dir}/capability_assessment.md
"""

        roi2_prompt = f"""PHASE DIRECTIVE: Phase 2 of 2
{shared_context}

Read approved checkpoint: {outputs_dir}/CHECKPOINT_roi_CP1_APPROVED.md
Read draft checkpoint: {outputs_dir}/CHECKPOINT_roi_CP1.md
Read capability assessment: {outputs_dir}/capability_assessment.md (if available)
Read market context: {outputs_dir}/market_context_validated.md (if available)
Read benchmarks: {outputs_dir}/benchmarks_validated.md (if available)

Build the full financial model with 3 scenarios (conservative/base/aspirational).
Run sensitivity analysis on top assumptions.

REQUIRED OUTPUT FILES (you MUST produce BOTH):
- {outputs_dir}/roi_report.md
- {outputs_dir}/roi_config.json
"""

        bench2_prompt = f"""PHASE DIRECTIVE: Phase 2 of 2
{shared_context}

Read approved checkpoint: {outputs_dir}/CHECKPOINT_benchmark_APPROVED.md
Read draft checkpoint: {outputs_dir}/CHECKPOINT_benchmark.md

Finalize benchmarks with source citations and confidence ratings.

REQUIRED OUTPUT FILES:
- {outputs_dir}/benchmarks_validated.md
"""

        results = await asyncio.gather(
            run_agent("journey-builder", jb2_prompt, engagement_dir, label="Journey Builder P2"),
            run_agent("market-context-researcher", mc2_prompt, engagement_dir, label="Market Context P2"),
            run_agent("capability-assessment", cap2_prompt, engagement_dir, label="Capability P2"),
            run_agent("roi-business-case-builder", roi2_prompt, engagement_dir, label="ROI P2"),
            run_agent("benchmark-librarian", bench2_prompt, engagement_dir, label="Benchmark P2"),
            return_exceptions=True,
        )

        for name, result in zip(["JB", "MC", "Cap", "ROI", "Bench"], results):
            if isinstance(result, Exception):
                log(f"  ✗ {name} Phase 2 FAILED: {result}", C.RED)
        cost += _sum_costs(results)

    # ── Validate required outputs (both modes) ───────────────────────────
    assert_file_exists(outputs_dir / "capability_assessment.md", "Capability")
    assert_file_exists(outputs_dir / "roi_report.md", "ROI")
    assert_file_exists(outputs_dir / "roi_config.json", "ROI")

    for f, name in [
        ("journey_maps.json", "Journey Builder"),
        ("market_context_validated.md", "Market Context"),
        ("benchmarks_validated.md", "Benchmark"),
    ]:
        if file_exists(outputs_dir / f):
            log(f"  ✓ {f} ({(outputs_dir / f).stat().st_size:,} bytes)", C.GREEN)
        else:
            log(f"  ⚠ {f} not produced by {name} (non-blocking)", C.YELLOW)

    return {"elapsed": time.time() - start, "cost": cost}


async def step_roadmap(
    engagement_dir: Path,
    outputs_dir: Path,
    express: bool,
    non_interactive: bool = False,
) -> dict:
    """Run Roadmap agent (depends on ROI + Capability).

    S4: Single-pass in both express AND non-interactive mode.
    """
    start = time.time()
    cost = 0.0

    # S4 FIX: Single-pass in express OR non-interactive mode
    if express or non_interactive:
        prompt = f"""Complete the full roadmap in a single pass.
Engagement directory: {engagement_dir}

Read:
- {outputs_dir}/capability_assessment.md
- {outputs_dir}/roi_report.md
- {outputs_dir}/evidence_register.md

Sequence initiatives by value, feasibility, and dependencies.
Create initiative cards with decision gates.

REQUIRED OUTPUT FILES:
- {outputs_dir}/roadmap.md
"""
        result = await run_agent("roadmap-prioritization", prompt, engagement_dir,
                                 label="Roadmap (single-pass)", max_turns=20)
        cost += result.total_cost_usd if result and result.total_cost_usd else 0
    else:
        # Phase 1
        prompt = f"""PHASE DIRECTIVE: Phase 1 of 2
Engagement directory: {engagement_dir}

Read:
- {outputs_dir}/capability_assessment.md
- {outputs_dir}/roi_report.md

Propose phasing and sequencing logic.

Write: {outputs_dir}/CHECKPOINT_roadmap.md
"""
        result = await run_agent("roadmap-prioritization", prompt, engagement_dir, label="Roadmap P1")
        cost += result.total_cost_usd if result and result.total_cost_usd else 0

        # T2 FIX: was express=False, now express=express
        present_checkpoint("roadmap", outputs_dir, express=express, non_interactive=non_interactive)

        # Phase 2
        prompt = f"""PHASE DIRECTIVE: Phase 2 of 2
Engagement directory: {engagement_dir}

Read approved checkpoint: {outputs_dir}/CHECKPOINT_roadmap_APPROVED.md
Read draft: {outputs_dir}/CHECKPOINT_roadmap.md

REQUIRED OUTPUT FILES:
- {outputs_dir}/roadmap.md
"""
        result = await run_agent("roadmap-prioritization", prompt, engagement_dir, label="Roadmap P2")
        cost += result.total_cost_usd if result and result.total_cost_usd else 0

    assert_file_exists(outputs_dir / "roadmap.md", "Roadmap")
    return {"elapsed": time.time() - start, "cost": cost}


async def step_assembly(
    engagement_dir: Path,
    outputs_dir: Path,
    express: bool,
    non_interactive: bool = False,
) -> dict:
    """Run Narrative Assembler.

    S3: In non-interactive mode, uses parallel sharding:
      P1 (plan) -> P2a (Acts 1-3) + P2b (Acts 4-7) parallel -> Python merge -> exec summary

    Interactive mode: preserves existing 3-phase flow with CP2 consultant review.
    """
    start = time.time()
    cost = 0.0
    inputs_dir = engagement_dir / "inputs"

    all_outputs = "\n".join(
        f"- {outputs_dir}/{f}"
        for f in [
            "evidence_register.md", "pain_points.md", "metrics.md",
            "stakeholder_intelligence.md", "capability_assessment.md",
            "roi_report.md", "roadmap.md",
            "journey_maps_summary.md", "market_context_validated.md",
            "benchmarks_validated.md",
        ]
        if (outputs_dir / f).exists()
    )

    # Resume guard: if both assembly outputs exist, skip entirely
    if file_exists(outputs_dir / "assessment_report.md") and file_exists(outputs_dir / "executive_summary.md"):
        log("  ⚡ Both assembly outputs exist — skipping assembly", C.YELLOW)
        return {"elapsed": 0, "cost": 0}

    if non_interactive:
        # ── S3: PARALLEL ASSEMBLY SHARDING (non-interactive) ─────────────

        # Phase 1: Quick structure plan (V5: capped to concise briefing)
        p1_prompt = f"""PHASE DIRECTIVE: Phase 1 — Assembly Plan (CONCISE structure plan only)
Engagement directory: {engagement_dir}

Read ALL upstream outputs:
{all_outputs}

Also read: {inputs_dir}/engagement_intake.md

OUTPUT CONSTRAINT: Write a CONCISE 2-3 page briefing (max 3,000 words).
Do NOT reproduce upstream content. Do NOT write full analysis.
This is a consistency anchor for the parallel shard writers.

Required sections (brief bullets only):
1. Transformation Arc — the EXACT phrase all shard writers will use (1 sentence)
2. Personas — names, segments, key attributes (bulleted list, ~5 lines)
3. Key Numbers — 5-year value, investment, payback (exact figures, ~5 lines)
4. Per-Act Blueprint — 2-3 sentences per act describing scope
5. Lighthouse Initiative — name and scope for Act 3 (3-4 lines)
6. Narrative Bridges — one-liner per transition (Act N → Act N+1)

Write: {outputs_dir}/CHECKPOINT_assembly_CP1.md
Do NOT write journal entries or update other files.
"""
        result = await run_agent("narrative-assembler", p1_prompt, engagement_dir,
                                 label="Assembly P1 (plan)", max_turns=5)
        cost += result.total_cost_usd if result and result.total_cost_usd else 0

        present_checkpoint("assembly_CP1", outputs_dir, express=express, non_interactive=non_interactive)

        # Phase 2: V5 3-way parallel shard writing (balanced workload)
        # Shard A: Acts 1-2 (Strategic Narrative)
        shard_a_files = "\n".join(
            f"- {outputs_dir}/{f}"
            for f in [
                "evidence_register.md", "pain_points.md", "metrics.md",
                "stakeholder_intelligence.md", "market_context_validated.md",
            ]
            if (outputs_dir / f).exists()
        )

        # Shard B: Acts 3-5 (Lighthouse + Journey + Capability)
        shard_b_files = "\n".join(
            f"- {outputs_dir}/{f}"
            for f in [
                "evidence_register.md", "pain_points.md",
                "capability_assessment.md", "journey_maps_summary.md",
                "market_context_validated.md", "benchmarks_validated.md",
            ]
            if (outputs_dir / f).exists()
        )

        # Shard C: Acts 6-7 + Appendix (Roadmap + ROI)
        shard_c_files = "\n".join(
            f"- {outputs_dir}/{f}"
            for f in [
                "roadmap.md", "roi_report.md", "roi_config.json",
                "capability_assessment.md", "benchmarks_validated.md",
                "evidence_register.md",
            ]
            if (outputs_dir / f).exists()
        )

        prompt_a = f"""PHASE DIRECTIVE: Phase 2A — Strategic Narrative (Acts 1, 2)
Engagement directory: {engagement_dir}

Read the approved assembly plan: {outputs_dir}/CHECKPOINT_assembly_CP1_APPROVED.md
Read the draft plan: {outputs_dir}/CHECKPOINT_assembly_CP1.md

Read upstream files:
{shard_a_files}
Also read: {inputs_dir}/engagement_intake.md

Write Acts 1-2 of the assessment report with FULL detail:
- Act 1: Strategic Alignment — Why transformation is needed
- Act 2: The Vision — What the transformation looks like

Use the EXACT transformation arc phrase, persona names, and key numbers from the CP1 plan.
End Act 2 with a narrative bridge paragraph that transitions to Act 3.

Write: {outputs_dir}/assembly_shard_A.md
Do NOT write journal entries or update other files.
"""

        prompt_b = f"""PHASE DIRECTIVE: Phase 2B — Lighthouse + Assessment (Acts 3, 4, 5)
Engagement directory: {engagement_dir}

Read the approved assembly plan: {outputs_dir}/CHECKPOINT_assembly_CP1_APPROVED.md
Read the draft plan: {outputs_dir}/CHECKPOINT_assembly_CP1.md

Read upstream files:
{shard_b_files}
Also read: {inputs_dir}/engagement_intake.md

Write Acts 3-5 of the assessment report with FULL detail:
- Act 3: The Lighthouse — How we prove the transformation (quick-win initiative)
- Act 4: Deep-Dive Assessment — Where the current system breaks (lifecycle gaps)
- Act 5: Capability Assessment — What capabilities the transformation requires

Use the EXACT transformation arc phrase, persona names, and key numbers from the CP1 plan.
Include narrative bridges between acts.
End Act 5 with a narrative bridge paragraph that transitions to Act 6.

Write: {outputs_dir}/assembly_shard_B.md
Do NOT write journal entries or update other files.
"""

        prompt_c = f"""PHASE DIRECTIVE: Phase 2C — Roadmap + Benefits (Acts 6, 7) + Appendix
Engagement directory: {engagement_dir}

Read the approved assembly plan: {outputs_dir}/CHECKPOINT_assembly_CP1_APPROVED.md
Read the draft plan: {outputs_dir}/CHECKPOINT_assembly_CP1.md

Read upstream files:
{shard_c_files}
Also read: {inputs_dir}/engagement_intake.md

Write Acts 6-7 of the assessment report with FULL detail:
- Act 6: Delivery Roadmap — How we build the transformation (phases)
- Act 7: Benefits Case — Why the transformation pays for itself

Also write the Appendix section (methodology, data sources, evidence index).

Use the EXACT transformation arc phrase, persona names, and key numbers from the CP1 plan.
Include narrative bridges between acts.

Write: {outputs_dir}/assembly_shard_C.md
Do NOT write journal entries or update other files.
"""

        results = await asyncio.gather(
            run_agent("narrative-assembler", prompt_a, engagement_dir,
                      label="Assembly P2A (Acts 1-2)", max_turns=25),
            run_agent("narrative-assembler", prompt_b, engagement_dir,
                      label="Assembly P2B (Acts 3-5)", max_turns=25),
            run_agent("narrative-assembler", prompt_c, engagement_dir,
                      label="Assembly P2C (Acts 6-7)", max_turns=25),
            return_exceptions=True,
        )

        for label, result in zip(["P2A", "P2B", "P2C"], results):
            if isinstance(result, Exception):
                log(f"  ✗ Assembly {label} FAILED: {result}", C.RED)
        cost += _sum_costs(results)

        # Python merge (instant — no LLM needed)
        shard_a_path = outputs_dir / "assembly_shard_A.md"
        shard_b_path = outputs_dir / "assembly_shard_B.md"
        shard_c_path = outputs_dir / "assembly_shard_C.md"

        shard_paths = [shard_a_path, shard_b_path, shard_c_path]
        existing_shards = [p for p in shard_paths if p.exists()]
        if len(existing_shards) == 3:
            parts = [p.read_text(encoding="utf-8") for p in existing_shards]
            merged = parts[0].rstrip() + "\n\n" + parts[1].strip() + "\n\n" + parts[2].lstrip()
            merged_path = outputs_dir / "assessment_report.md"
            merged_path.write_text(merged, encoding="utf-8")
            log(f"  ✓ Merged 3 shards → assessment_report.md ({merged_path.stat().st_size:,} bytes)", C.GREEN)
        else:
            missing = [p.name for p in shard_paths if not p.exists()]
            log(f"  ✗ Cannot merge — missing shards: {', '.join(missing)}", C.RED)

        # Executive summary (quick agent pass)
        exec_prompt = f"""Write a concise executive summary for the assessment report.

Read: {outputs_dir}/assessment_report.md
Also read: {outputs_dir}/CHECKPOINT_assembly_CP1.md (for key numbers and arc)

Synthesize:
- The transformation arc
- Key findings (3-5 bullets)
- Strategic recommendation
- Financial headline (investment, payback, 5-year value)

Write: {outputs_dir}/executive_summary.md (2-3 pages max)
Do NOT write journal entries or update other files.
"""
        result = await run_agent("narrative-assembler", exec_prompt, engagement_dir,
                                 label="Executive Summary", max_turns=15)
        cost += result.total_cost_usd if result and result.total_cost_usd else 0

    else:
        # ── INTERACTIVE: Keep existing 3-phase flow with CP2 review ──────

        # Phase 1: Assembly plan
        prompt = f"""PHASE DIRECTIVE: Phase 1 of 3
Engagement directory: {engagement_dir}

Read ALL upstream outputs:
{all_outputs}

Also read: {inputs_dir}/engagement_intake.md

Build the 7-act narrative structure and assembly plan.

Write: {outputs_dir}/CHECKPOINT_assembly_CP1.md
"""
        result = await run_agent("narrative-assembler", prompt, engagement_dir, label="Assembly P1")
        cost += result.total_cost_usd if result and result.total_cost_usd else 0
        present_checkpoint("assembly_CP1", outputs_dir, express=express, non_interactive=non_interactive)

        # Phase 2: Draft report
        prompt = f"""PHASE DIRECTIVE: Phase 2 of 3
Engagement directory: {engagement_dir}

Read approved plan: {outputs_dir}/CHECKPOINT_assembly_CP1_APPROVED.md
Read all upstream outputs:
{all_outputs}

Draft the full 7-act report sections.

Write: {outputs_dir}/CHECKPOINT_assembly_CP2.md
"""
        result = await run_agent("narrative-assembler", prompt, engagement_dir, label="Assembly P2")
        cost += result.total_cost_usd if result and result.total_cost_usd else 0

        # Assembly CP2 ALWAYS pauses for interactive — this is the final report review
        present_checkpoint("assembly_CP2", outputs_dir, express=False, non_interactive=non_interactive)

        # Phase 3: Finalize
        prompt = f"""PHASE DIRECTIVE: Phase 3 of 3
Engagement directory: {engagement_dir}

Read approved draft: {outputs_dir}/CHECKPOINT_assembly_CP2_APPROVED.md

Incorporate consultant feedback. Finalize the report.

REQUIRED OUTPUT FILES (you MUST produce BOTH):
- {outputs_dir}/assessment_report.md
- {outputs_dir}/executive_summary.md
"""
        result = await run_agent("narrative-assembler", prompt, engagement_dir, label="Assembly P3")
        cost += result.total_cost_usd if result and result.total_cost_usd else 0

    assert_file_exists(outputs_dir / "assessment_report.md", "Assembly")
    assert_file_exists(outputs_dir / "executive_summary.md", "Assembly")
    return {"elapsed": time.time() - start, "cost": cost}


# ─── T3: Inline design rules for HTML generation ─────────────────────────────

_DESIGN_RULES_INLINE = """
CRITICAL DESIGN RULES — follow these exactly (full details in design-system.md):
- LIGHT base theme: Body background #F8FAFC, cards #FFFFFF
- Brand colors: #3366FF (blue), #091C35 (dark navy), #7B2FFF (purple), #26BC71 (green), #FF7262 (red), #FFAC09 (amber), #69FEFF (cyan)
- Dark colors (#091C35) ONLY for: sidebar navigation, hero banner, dark-feature accent sections
- WCAG on dark backgrounds: Blue text -> #60A5FA (not #3366FF), Green text -> #34D399 (not #26BC71)
- Sub-labels on dark backgrounds: minimum rgba(255,255,255,0.55) opacity
- Card accents: use TOP accent gradients, NEVER border-left ribbons
- DO NOT generate a dark-themed dashboard. The base theme is LIGHT (#F8FAFC).
- TYPOGRAPHY: Use <strong> or font-weight:700 SPARINGLY — only for metric values, card
  titles, and key emphasis. Body text and descriptions must use normal weight (400).
  Over-bolding everything makes the dashboard feel heavy and reduces visual hierarchy.
"""


def _prepare_html_source_pack(outputs_dir: Path) -> Path:
    """Concatenate upstream files into ONE source pack for HTML agent. Pure Python — no LLM."""
    pack_path = outputs_dir / "html_source_pack.md"
    sections = [
        ("Executive Summary", "executive_summary.md", 0),        # 10KB — full
        ("Assessment Report", "assessment_report.md", 800),      # 228KB → first 800 lines
        ("Capability Assessment", "capability_assessment.md", 500),  # 85KB → first 500 lines
        ("ROI Report", "roi_report.md", 400),                    # 44KB → first 400 lines
        ("ROI Config JSON", "roi_config.json", 0),               # 51KB — full (scenario data)
        ("Roadmap", "roadmap.md", 400),                          # 80KB → first 400 lines
        ("Journey Maps", "journey_maps_summary.md", 400),        # 46KB → first 400 lines
    ]
    parts = []
    for title, filename, max_lines in sections:
        filepath = outputs_dir / filename
        if not filepath.exists():
            continue
        text = filepath.read_text(encoding="utf-8", errors="replace")
        if max_lines > 0:
            lines = text.splitlines()
            if len(lines) > max_lines:
                text = "\n".join(lines[:max_lines]) + f"\n\n[... truncated at {max_lines} lines ...]"
        parts.append(f"\n{'='*60}\n## SOURCE: {title} ({filename})\n{'='*60}\n\n{text}")
    pack_path.write_text("\n".join(parts), encoding="utf-8")
    log(f"  📦 Source pack: {pack_path.name} ({pack_path.stat().st_size:,} bytes)", C.DIM)
    return pack_path


def _assemble_html_dashboard(template_path: Path, partials_dir: Path, output_path: Path) -> bool:
    """Read template + partials, replace {{PLACEHOLDER}} markers. Pure Python — no LLM."""
    template = template_path.read_text(encoding="utf-8")
    replacements = {}

    for partial_file in sorted(partials_dir.glob("[Pp][Aa][Rr][Tt][Ii][Aa][Ll]_*.html")):
        content = partial_file.read_text(encoding="utf-8")
        # Parse <!-- PLACEHOLDER_NAME --> ... content ... <!-- NEXT --> format
        markers = re.findall(r'<!--\s*([A-Z][A-Z0-9_]+)\s*-->', content)
        for i, marker in enumerate(markers):
            # Content from this marker to next marker or EOF
            if i + 1 < len(markers):
                next_marker = markers[i + 1]
                pattern = (
                    r'<!--\s*' + re.escape(marker) + r'\s*-->\s*\n?'
                    r'(.*?)'
                    r'(?=<!--\s*' + re.escape(next_marker) + r'\s*-->)'
                )
            else:
                pattern = r'<!--\s*' + re.escape(marker) + r'\s*-->\s*\n?(.*)'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                value = match.group(1).strip()
                if value:
                    replacements[marker] = value

    replaced = 0
    # Triple-brace first (JS objects): {{{KEY}}} → {value} (preserves outer braces for JS)
    for key, value in replacements.items():
        triple = "{{{" + key + "}}}"
        if triple in template:
            template = template.replace(triple, "{" + value + "}")
            replaced += 1
    # Double-brace: {{KEY}} → value
    for key, value in replacements.items():
        placeholder = "{{" + key + "}}"
        if placeholder in template:
            template = template.replace(placeholder, value)
            replaced += 1

    remaining = re.findall(r'\{\{([A-Z][A-Z0-9_]+)\}\}', template)
    if remaining:
        log(f"  ⚠ {len(remaining)} unfilled placeholders: {', '.join(remaining[:8])}", C.YELLOW)

    output_path.write_text(template, encoding="utf-8")
    size = output_path.stat().st_size
    log(f"  ✓ Assembled: {output_path.name} ({size:,} bytes, {replaced} placeholders filled)", C.GREEN)
    return size > 100_000  # sanity: should be >100KB


async def step_generate_html(
    engagement_dir: Path,
    outputs_dir: Path,
) -> dict:
    """Generate HTML dashboard. V5: Python pre-pack + assembly, 6 macro-partials."""
    start = time.time()
    cost = 0.0

    if not file_exists(outputs_dir / "assessment_report.md"):
        log("  ⚠ Skipping HTML — assessment_report.md not found", C.YELLOW)
        return {"elapsed": 0, "cost": 0}

    # ── Step 1: Python pre-packs all upstream data into one file ──
    source_pack = _prepare_html_source_pack(outputs_dir)
    partials_dir = outputs_dir / "partials"
    partials_dir.mkdir(exist_ok=True)

    template_path = REPO_ROOT / "templates/presentations/assessment-dashboard-template.html"

    html_prompt = f"""You are generating HTML content for an interactive assessment dashboard.
Python will handle assembly — you only write 6 partial files.

TOOL CONSTRAINT: Do NOT use the Task tool. Do NOT read the template file.
Do NOT assemble the final HTML. Python handles template + assembly.

STEP 1 — Read the source data (ONE file with all upstream data):
Read: {source_pack}
(Read it in chunks if needed: lines 1-500, 501-1000, etc.)

{_DESIGN_RULES_INLINE}

STEP 2 — Write 6 partial files to: {partials_dir}/

Each partial uses comment markers to delimit placeholder values:
<!-- PLACEHOLDER_NAME -->
HTML content here
<!-- NEXT_PLACEHOLDER_NAME -->
HTML content here

IMPORTANT FORMAT RULES:
- Each marker is on its own line: <!-- NAME -->
- Content follows on the next line(s)
- Next marker starts the next placeholder
- Use ONLY the placeholder names listed below — exact spelling matters

═══════════════════════════════════════════════════════════
PARTIAL_A.html — Hero + Executive Summary
═══════════════════════════════════════════════════════════

<!-- CLIENT_NAME -->
Short client name (e.g., NFIS)
<!-- REPORT_SUBTITLE -->
e.g., Digital Investor Platform Assessment
<!-- ASSESSMENT_DATE -->
e.g., February 2026
<!-- HERO_H1 -->
Multi-line hero heading with <span> tags and gradient text. Example:
<span>From Trusted</span><span>Banker to</span><span style="background:linear-gradient(135deg,#3366FF,#7B2FFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Trusted Investor</span>
<!-- HERO_SUBTITLE -->
1-2 sentence hero subtitle about the engagement
<!-- HERO_TAGS -->
<span class="hero-tag">Tag1</span><span class="hero-tag">Tag2</span>...
<!-- HERO_ALERT -->
<span style="font-weight:700;">⚠ Cost of Inaction: $XXX/month</span> — breakdown text
<!-- HERO_IMAGE_URL -->
https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=900&auto=format&fit=crop&q=80
<!-- HERO_FLOATS -->
3 floating glass cards:
<div class="hero-float" style="top:80px;right:24px;"><div class="hero-float-val" style="color:#DC2626;">50%</div><div class="hero-float-lbl">Label</div></div>
(repeat for 3 cards)
<!-- HERO_STATS -->
5 stat items:
<div class="hero-stat"><div class="hero-stat-val" style="color:#3366FF;">14.27M</div><div class="hero-stat-lbl">Label</div></div>
(repeat for 5 stats)
<!-- EXEC_SUMMARY_DESC -->
1-2 sentence executive summary
<!-- EXEC_TRANSFORMATION_STORY -->
Transformation arc card with gradient overline:
<div style="position:relative;overflow:hidden;"><div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#3366FF,#7B2FFF);"></div><div style="padding:4px 0 20px;"><div style="font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:3px;background:linear-gradient(90deg,#3366FF,#7B2FFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:12px;">TRANSFORMATION ARC</div><h3 style="font-size:1.5rem;font-weight:900;">Arc Title</h3><p style="font-size:0.92rem;color:var(--muted);line-height:1.8;">Arc description</p></div></div>
<!-- EXEC_BENTO_ITEMS -->
6 bento stat cards. Use class "bento-item bento-stat" (light) or "bento-item bento-dark bento-stat" (dark).
For 2x-width: add "bento-2x1". For accent: add "bento-accent".
<div class="bento-item bento-dark bento-2x1 bento-stat"><div class="bento-stat-val" style="color:#DC2626;">50%</div><div class="bento-stat-lbl">Label</div></div>
<!-- EXEC_PILLARS -->
Dark feature section with 3 transformation pillars:
<div class="dark-feature-overline">THE THREE PILLARS</div><h3>Pillar1. <span>Pillar2.</span> Pillar3.</h3><div class="dark-feature-sub">Description</div><div class="dark-feature-grid"><div class="dark-feature-card"><h4>🎯 Title</h4><p>Description</p></div>(repeat 3)</div>
<!-- EXEC_METRIC_CARDS -->
4 metric cards:
<div class="metric-card"><div class="metric-val" style="color:#DC2626;">-$1.5M</div><div class="metric-lbl">5-Year NPV</div></div>
(repeat for NPV, payback, investment, confidence)
<!-- EXEC_DECISION_BOX -->
Decision request card with scenario comparison grid (conservative/base/aspirational boxes)

═══════════════════════════════════════════════════════════
PARTIAL_B.html — Acts 1, 2, 3
═══════════════════════════════════════════════════════════

For each act: TITLE, DESC, TRANSFORMATION_THREAD, then act-specific content.
TRANSFORMATION_THREAD format (same card style as EXEC_TRANSFORMATION_STORY but shorter):
<div style="position:relative;overflow:hidden;"><div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#3366FF,#7B2FFF);"></div><div style="padding:4px 0 0;"><div style="font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:3px;background:linear-gradient(90deg,#3366FF,#7B2FFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:10px;">TRANSFORMATION ARC — ACT THEME</div><h3 style="font-size:1.1rem;font-weight:900;margin-bottom:10px;">Thread Title</h3><p style="font-size:0.88rem;color:var(--muted);line-height:1.75;">2-3 sentences connecting this act to the transformation arc.</p></div></div>

<!-- ACT1_TITLE -->
Act 1 title
<!-- ACT1_DESC -->
Act 1 description (1-2 sentences)
<!-- ACT1_TRANSFORMATION_THREAD -->
(transformation thread card HTML as described above — theme: "Why transformation is needed")
<!-- ACT1_DARK_FEATURE -->
Dark feature section: overline + h3 + sub + grid of dark-feature-cards
<!-- ACT1_INSIGHT_CARDS -->
2-4 insight cards (class="card")
<!-- ACT1_ADDITIONAL_CONTENT -->
Any extra content (evidence quotes, data tables, etc.)
<!-- ACT2_TITLE -->
Act 2 title
<!-- ACT2_DESC -->
Act 2 description
<!-- ACT2_TRANSFORMATION_THREAD -->
(theme: "What the transformation looks like")
<!-- ACT2_PILLAR_CARDS -->
3 pillar cards (class="pillar-card" or "card")
<!-- ACT2_ADDITIONAL_CONTENT -->
Extra content
<!-- ACT3_TITLE -->
Act 3 title
<!-- ACT3_DESC -->
Act 3 description
<!-- ACT3_TRANSFORMATION_THREAD -->
(theme: "How we prove the transformation")
<!-- ACT3_LIGHTHOUSE_DETAIL -->
Lighthouse initiative detail (phase 1 description, scope, timeline)
<!-- ACT3_MILESTONE_CARDS -->
3 milestone cards
<!-- ACT3_ADDITIONAL_CONTENT -->
Extra content

═══════════════════════════════════════════════════════════
PARTIAL_C.html — Acts 4 and 5
═══════════════════════════════════════════════════════════

<!-- ACT4_TITLE -->
Act 4 title
<!-- ACT4_DESC -->
Act 4 description
<!-- ACT4_TRANSFORMATION_THREAD -->
(theme: "Where current system breaks")
<!-- ACT4_PERSONAS -->
Persona cards: <div class="persona-card"><h4>Name</h4><div style="font-size:0.75rem;color:var(--muted);">Segment</div><div class="persona-detail">Pain points, needs, etc.</div></div>
<!-- ACT4_JX_HEADLINES -->
Journey experience map headline cards per stage:
<div class="jx-headline"><span class="jx-stage-num">1</span><strong>Stage Name</strong><span class="jx-emoji">📱</span></div>
<!-- ACT4_JX_SVG -->
SVG emotion curve (width 100%, viewBox, path with emotion line):
<svg width="100%" viewBox="0 0 800 200" style="overflow:visible;">...<path d="M0,100 C..." stroke="#3366FF" fill="none" stroke-width="3"/>...<circle class="jx-marker" data-stage="1" cx="80" cy="120" r="8" fill="#3366FF" onclick="showStage(1)"/>...</svg>
<!-- ACT4_JX_PANELS -->
Expandable detail panels per stage:
<div class="jx-panel" id="jxp-1"><h4>Stage 1 Title</h4><div class="pain-grid"><div class="pain-item">Pain point</div>...</div><div class="opp-grid"><div class="opp-item">Opportunity</div>...</div></div>
<!-- ACT4_ADDITIONAL_CONTENT -->
Extra content
<!-- ACT5_TITLE -->
Act 5 title
<!-- ACT5_DESC -->
Act 5 description
<!-- ACT5_TRANSFORMATION_THREAD -->
(theme: "What capabilities the transformation requires")
<!-- ACT5_HERO_STATS -->
MANDATORY. Hero stats row matching 02e gold standard. 2-column grid:
Left: Big average maturity number (e.g. "0.56") with gradient text color using L0/L1 CSS vars, "Average Maturity / 4.0" sublabel.
Right: Distribution bar (.dist-bar + .dist-seg CSS classes) showing count/percent per maturity level + .dist-legend with dot + label.
Use this HTML structure:
<div style="display:grid;grid-template-columns:200px 1fr;gap:24px;align-items:center;margin-bottom:36px;">
  <div style="text-align:center;"><div style="font-size:3.2rem;font-weight:900;letter-spacing:-2px;background:linear-gradient(135deg,var(--L0),var(--L1));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1;">X.XX</div><div style="font-size:0.72rem;color:var(--muted);font-weight:600;">Average Maturity / 4.0</div></div>
  <div><div class="dist-bar" style="margin-bottom:8px;"><div class="dist-seg" style="width:NN%;background:var(--L0);">N (NN%)</div>...</div><div class="dist-legend">...</div></div>
</div>
Compute averages from capability data. Only show levels that have capabilities.
<!-- ACT5_DARK_FEATURE -->
MANDATORY. Dark feature banner showing the cross-cutting structural barrier. Use .dark-feature CSS class.
Structure: overline + large h3 title (2-line with <br><span>) + subtitle paragraph + 3-column comparison:
Left: "What Exists" — 4 bullet items showing current infrastructure (blue tones, rgba(51,102,255,...))
Center: Broken connection (X icon with dashed line)
Right: "What's Missing" — 4 bullet items showing gaps (red tones, rgba(255,114,98,...), with line-through text)
Bottom: Quote from evidence in italic with attribution.
Model the NFIS 02e "Two Organizations, Zero Shared Intelligence" pattern but adapted to this client's structural barrier.
<!-- ACT5_PIPELINE_LABEL -->
Short uppercase label for the lifecycle pipeline, e.g. "Member Banking Lifecycle" or "Customer Investment Lifecycle"
<!-- ACT5_DOMAIN_LEGEND -->
Domain legend pills — one colored pill badge per capability domain. Use this HTML pattern:
<span style="display:inline-block;padding:4px 12px;border-radius:8px;font-size:0.68rem;font-weight:700;background:#EFF6FF;color:#1D4ED8;">Customer Lifecycle</span>
(one per domain, using distinct background/text color pairs)
<!-- ACT5_CAP_COUNT -->
Total number of capabilities (integer only, e.g. "16" or "20")
<!-- ACT5_HEATMAP_DATA -->
CRITICAL FORMAT: JS object literals separated by commas, NO outer brackets.
The template wraps this in [...]. Each object MUST have these fields:
  id (string), name (string), domain (string), score (0-4 integer),
  front (0-4 integer — front office score), middle (0-4 integer — middle office score),
  back (0-4 integer — back office score).
Optional: desc (assessment detail text), impact (value impact string, e.g. "$892K (5yr)").
The detail panel shows F/M/B breakdown + assessment detail + value impact when clicked.
Example: {{id:"C1.1",name:"Account Origination",domain:"Onboarding",score:1,front:1,middle:1,back:0,desc:"Account opening workflow lacks digital capabilities",impact:"$892K (5yr)"}},{{id:"C1.2",name:"Funding Automation",domain:"Onboarding",score:0,front:0,middle:0,back:0,desc:"Manual ACH only",impact:"$1.4M (5yr)"}}
<!-- ACT5_LIFECYCLE_STAGES -->
CRITICAL FORMAT: JS object literals separated by commas, NO outer brackets.
The template wraps this in [...]. Each stage object MUST have:
  id (string), title (string), icon (emoji string), color (hex string from brand palette),
  tagline (string — short problem statement), stat (string), statLabel (string),
  statDetail (string — 2-3 sentence explanation),
  l1s (array of L1 problem objects).
Each L1 object MUST have: label (string), desc (string), l2s (array of L2 objects).
Each L2 object MUST have: label (string), desc (string), caps (array of capability ID strings matching ACT5_HEATMAP_DATA ids).
Create 4-6 lifecycle stages that group capabilities by customer journey phase.
Map ALL capabilities to exactly one lifecycle stage. Every capability ID must appear in exactly one L2.caps array.
Stage colors: use brand palette (#3366FF, #EA580C, #059669, #DC2626, #7B2FFF, #FFAC09).
The template uses var LIFECYCLE_STAGES = [{{ACT5_LIFECYCLE_STAGES}}]; — so output complete JS objects with their own braces.

═══════════════════════════════════════════════════════════
PARTIAL_D.html — Acts 6 and 7
═══════════════════════════════════════════════════════════

<!-- ACT6_TITLE -->
Act 6 title
<!-- ACT6_DESC -->
Act 6 description
<!-- ACT6_TRANSFORMATION_THREAD -->
(theme: "How we build the transformation")
<!-- ACT6_TIMELINE -->
VISUAL timeline with phase dots and expandable cards. Use these EXACT CSS classes:
<div class="timeline-phase"><div class="phase-dot" style="border-color:#DC2626;"></div><div class="phase-card open"><h4 style="color:#DC2626;">Phase 1: NOW</h4><div class="phase-time">Months 0-9 | 2026 H1-H2</div><div class="phase-cost">~$3.0M Investment</div><div class="phase-items"><ul><li>Initiative 1</li><li>Initiative 2</li></ul></div></div></div>
Repeat for 3 phases. Use colors: Phase 1=#DC2626 (red), Phase 2=#EA580C (orange), Phase 3=#059669 (green).
Make Phase 1 card "open" (expanded), others collapsed (user clicks to expand).
Each phase lists: initiatives as bullet points, timeline range, investment estimate.
<!-- ACT6_PHASE_CARDS -->
3 phase summary cards (optional — only if timeline doesn't cover all detail)
<!-- ACT6_ADDITIONAL_CONTENT -->
Two sections here:
1. DECISIONS CARD: A single FULL-WIDTH .card with border-top:3px solid #3366FF. Inside: heading "THREE DECISIONS REQUIRED BEFORE MONTH 1" + 3-column grid of decision boxes (background:#EFF6FF, border-radius:12px, padding:20px). Do NOT wrap in card-grid card-grid-3.
2. KEY VALUE MILESTONES: A .card with 4-column grid of milestone boxes (Month X → what happens). Use phase-matching colors for backgrounds.
<!-- ACT7_TITLE -->
Act 7 title
<!-- ACT7_DESC -->
Act 7 description
<!-- ACT7_TRANSFORMATION_THREAD -->
(theme: "Why transformation pays for itself")
<!-- ACT7_ROI_CARDS -->
CRITICAL: 4 dynamic ROI cards with specific IDs that setScenario() updates.
Use these EXACT CSS classes (roi-card, NOT metric-card):
<div class="roi-card"><div class="roi-card-val" id="roi-npv">-$1.5M</div><div class="roi-card-lbl">5-Year NPV</div></div><div class="roi-card"><div class="roi-card-val" id="roi-return">-12%</div><div class="roi-card-lbl">5-Year ROI</div></div><div class="roi-card"><div class="roi-card-val" id="roi-payback">~6.5 yrs</div><div class="roi-card-lbl">Payback Period</div></div><div class="roi-card"><div class="roi-card-val" id="roi-benefits">$7.7M</div><div class="roi-card-lbl">5yr Gross Benefits</div></div>
Set initial values to the BASE scenario numbers from roi_config.json → scenarios.base. The parent roi-grid div is already in the template.
<!-- ACT7_BASE_DESC -->
Plain text description of the base scenario (1-2 sentences). NOT HTML. Use roi_config.json → scenarios.base.desc.
<!-- ACT7_SCENARIO_DATA -->
CRITICAL FORMAT: A JS object (NO var keyword, NO semicolon — the template wraps it).
Must have exactly 3 keys: conservative, base, aspirational.
Each value MUST have: npv (string), roi (string), payback (string), benefits (string), desc (string).
SOURCE: Copy values DIRECTLY from roi_config.json → "scenarios" object. Do NOT re-derive from markdown tables.
Example:
conservative:{{npv:"-$4.8M",roi:"-55%",payback:">10 yrs",benefits:"$3.1M",desc:"Conservative: low improvement rates across all levers"}},base:{{npv:"-$1.5M",roi:"-12%",payback:"~6.5 yrs",benefits:"$7.7M",desc:"Base: moderate improvements with peer-benchmarked assumptions"}},aspirational:{{npv:"+$3.2M",roi:"+36%",payback:"~4.2 yrs",benefits:"$14.5M",desc:"Aspirational: high conversion rates with full cross-app integration"}}
<!-- ACT7_FINANCIAL_TABLE -->
Wrap the table in: <div class="card reveal" style="margin-bottom:40px;"><h3 style="margin-bottom:20px;">5-Year Financial Model &mdash; Base Scenario</h3><div style="overflow-x:auto;">
...TABLE HERE...
</div></div>
HTML table with 5-year projection (Year 1-5 + 5yr Total columns, benefit lines/cost lines/net row).
<!-- ACT7_VALUE_LEVERS -->
Start with: <h3 style="margin-bottom:20px;">Value Levers &mdash; Base Scenario (5-Year)</h3>
EXPANDABLE value lever cards. Users click to see benchmarks and calculation.
Use the .lever-card CSS classes from the template. Create 5-6 lever cards.
SOURCE: Use roi_config.json → "lever_summary" array for lever names, values, MECE text, benchmarks, and capability IDs. Do NOT invent MECE content — it is authored by the ROI agent.
CRITICAL: Keep expanded content CONCISE. Each MECE box must be 1-2 SHORT sentences (max 25 words). No verbose paragraphs.
Each lever card follows this structure:
<div class="lever-card" data-trace-id="BEN-1">
  <div class="lever-header" onclick="this.parentElement.classList.toggle('open')">
    <span class="lever-num">01</span>
    <span class="lever-name">Lever Name</span>
    <span class="lever-value" style="color:#3366FF;">$X.XM</span>
    <span class="lever-arrow">&#9660;</span>
  </div>
  <div class="lever-body"><div class="lever-content">
    <div class="lever-mece">
      <div class="lever-mece-box" style="background:#FEF2F2;"><h5 style="color:#DC2626;">Current State</h5>Short phrase: what happens today</div>
      <div class="lever-mece-box" style="background:#FFFBEB;"><h5 style="color:#D97706;">Change Driver</h5>Short phrase: what Backbase enables</div>
      <div class="lever-mece-box" style="background:#F0FDF4;"><h5 style="color:#059669;">Target State</h5>Short phrase: KPI improvement with %</div>
    </div>
    <div class="lever-benchmark"><strong>Benchmark:</strong> One-line industry benchmark with source</div>
    <div class="lever-capabilities"><span class="lever-cap-tag">CAP-ID</span></div>
  </div></div>
</div>
Lever-value colors: #3366FF, #EA580C, #7B2FFF, #059669, #DC2626, #FFAC09.

═══════════════════════════════════════════════════════════
PARTIAL_E.html — Journey Maps
═══════════════════════════════════════════════════════════

<!-- JOURNEY_DESC -->
Journey maps description (1-2 sentences)
<!-- JOURNEY_SWIMLANES -->
Journey swimlanes with current/future toggle per journey:
<div class="journey-block" id="journey-1"><div class="swimlane-header"><h4>Journey Name</h4><div><button class="swimlane-toggle-btn active-current" onclick="toggleJourney('1','current',this)">Current</button><button class="swimlane-toggle-btn" onclick="toggleJourney('1','future',this)">Future</button></div></div><div class="swimlane-panel active" data-state="current"><div class="swimlane-row"><div class="swim-stage">Stage</div><div class="swim-actions">Actions</div><div class="swim-pain">Pain</div><div class="swim-channel">Channel</div></div></div><div class="swimlane-panel" data-state="future"><div class="swimlane-row"><div class="swim-stage">Stage</div><div class="swim-actions">Future actions</div><div class="swim-gain">Gains</div><div class="swim-channel">Channel</div></div></div></div>
Create 3-4 journey blocks for key personas.

═══════════════════════════════════════════════════════════
PARTIAL_F.html — Use Cases
═══════════════════════════════════════════════════════════

<!-- USECASES_TITLE -->
Use cases section title
<!-- USECASES_DESC -->
Use cases description
<!-- USECASES_CARDS -->
Clickable use case cards:
<div class="uc-card"><div class="uc-card-header"><span class="uc-icon">💡</span><h4>Use Case Title</h4></div><div class="uc-card-body"><p>Description</p><div class="uc-stat-row"><div class="uc-stat-card"><div class="uc-stat-val">$1.3M</div><div class="uc-stat-lbl">Annual Value</div></div></div></div></div>
<!-- USECASES_PHONE_PROTOTYPES -->
OPTIONAL — only include prototypes if the engagement has detailed use case flow data.
If not available, write: <!-- no prototypes -->
If included (2-3 max), wrap them in a heading and grid:
<h3 style="margin:48px 0 24px;">Prototype Previews</h3>
<div class="proto-grid">
<div class="proto-wrap"><div class="proto-phone"><div class="proto-notch"></div><div class="proto-screen"><div style="padding:16px;"><h5 style="font-size:0.85rem;margin-bottom:12px;">Screen Title</h5><div style="background:#F1F5F9;border-radius:8px;padding:12px;margin-bottom:8px;font-size:0.75rem;">Content block</div></div></div></div><div class="proto-caption"><span style="font-weight:600;">Screen Name</span><p style="font-weight:400;">What this screen shows</p></div></div>
</div>

═══════════════════════════════════════════════════════════

Write ALL 6 files (PARTIAL_A through PARTIAL_F). STOP IMMEDIATELY after writing the 6th file.
Do NOT write any other files. Do NOT assemble the final HTML.
Do NOT read the template. Do NOT explore the filesystem.
Do NOT validate. Do NOT run any bash scripts.
Python handles the template, assembly, and validation — your ONLY job is the 6 partials.
After writing PARTIAL_F.html, output "DONE — 6 partials written" and stop.
"""

    result = await run_agent(
        "narrative-assembler", html_prompt, engagement_dir,
        label="HTML Dashboard", max_turns=25,
    )
    cost += result.total_cost_usd if result and result.total_cost_usd else 0

    # ── Step 3: Python assembles template + partials → final HTML ──
    partials_exist = list(partials_dir.glob("[Pp][Aa][Rr][Tt][Ii][Aa][Ll]_*.html"))
    if partials_exist:
        log(f"  📎 Found {len(partials_exist)} partials, assembling...", C.DIM)
        ok = _assemble_html_dashboard(template_path, partials_dir, outputs_dir / "assessment_dashboard.html")
        if not ok:
            log("  ⚠ Assembly produced undersized file — agent may not have written all partials", C.YELLOW)
    else:
        # Fallback: check if agent wrote the full HTML directly
        log("  ⚠ No partials found — checking for direct HTML output", C.YELLOW)

    html_files = glob_files("*.html", outputs_dir)
    if html_files:
        for h in html_files:
            log(f"  ✓ {h.name} ({h.stat().st_size:,} bytes)", C.GREEN)
    else:
        log("  ✗ No HTML dashboard produced", C.RED)

    return {"elapsed": time.time() - start, "cost": cost}


async def step_generate_excel(
    engagement_dir: Path,
    outputs_dir: Path,
) -> dict:
    """Generate ROI Excel model. Extracted for S2 overlapping."""
    start = time.time()
    cost = 0.0

    if not file_exists(outputs_dir / "roi_config.json"):
        log("  ⚠ Skipping Excel — roi_config.json not found", C.YELLOW)
        return {"elapsed": 0, "cost": 0}

    excel_prompt = f"""You are generating a ROI Excel model.

Read and follow: {COMMANDS_DIR / 'generate-roi-excel.md'}

Read the ROI config: {outputs_dir}/roi_config.json
Read the ROI report: {outputs_dir}/roi_report.md

Generate the Excel model using the roi_excel_generator tool or by writing
the Excel file directly.

Write the output to: {outputs_dir}/
"""

    result = await run_agent(
        "roi-business-case-builder", excel_prompt, engagement_dir,
        label="ROI Excel", max_turns=30,
    )
    cost += result.total_cost_usd if result and result.total_cost_usd else 0

    xlsx_files = glob_files("*.xlsx", outputs_dir)
    if xlsx_files:
        for x in xlsx_files:
            log(f"  ✓ {x.name} ({x.stat().st_size:,} bytes)", C.GREEN)

    return {"elapsed": time.time() - start, "cost": cost}


async def step_validate(engagement_dir: Path, outputs_dir: Path) -> bool:
    """Run the validation gate script."""
    script = REPO_ROOT / "scripts" / "validate_engagement_outputs.sh"
    if not script.exists():
        log("  ⚠ validate_engagement_outputs.sh not found — skipping", C.YELLOW)
        return True

    result = subprocess.run(
        ["bash", str(script), str(engagement_dir), "assessment"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        log("  ✓ Validation gate PASSED", C.GREEN)
        return True
    else:
        log(f"  ✗ Validation gate FAILED:\n{result.stdout}\n{result.stderr}", C.RED)
        return False


# ─── T4: Pipeline Summary ────────────────────────────────────────────────────

def _print_pipeline_summary(timings: dict, pipeline_start: float):
    """Print timing + cost summary table at pipeline end."""
    total_time = time.time() - pipeline_start
    total_cost = sum(t.get("cost", 0) for t in timings.values())

    print(f"\n{C.BOLD}{C.GREEN}{'═' * 60}{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}  PIPELINE COMPLETE{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}{'═' * 60}{C.RESET}")
    print(f"\n  {'Stage':<25s} {'Time':>8s}  {'Cost':>8s}")
    print(f"  {'─' * 45}")
    for stage, data in timings.items():
        elapsed = data.get("elapsed", 0)
        cost = data.get("cost", 0)
        print(f"  {stage:<25s} {elapsed/60:>5.1f} min  ${cost:>7.2f}")
    print(f"  {'─' * 45}")
    print(f"  {'TOTAL':<25s} {total_time/60:>5.1f} min  ${total_cost:>7.2f}")

    return total_time, total_cost


# ─── Main Pipeline ────────────────────────────────────────────────────────────

async def run_pipeline(
    engagement_dir: Path,
    express: bool = False,
    non_interactive: bool = False,
    resume_from: Optional[str] = None,
    dry_run: bool = False,
):
    outputs_dir = engagement_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    pipeline_start = time.time()
    timings: dict[str, dict] = {}

    # ── Detect domain from intake ─────────────────────────────────────────
    intake_file = engagement_dir / "inputs" / "engagement_intake.md"
    domain = "retail"  # default
    if intake_file.exists():
        intake_text = read_file(intake_file)
        # Look for explicit "**Domain:** <value>" field first
        domain_match = re.search(r"\*\*Domain:\*\*\s*(\w+)", intake_text)
        if domain_match and domain_match.group(1).lower() in [
            "retail", "sme", "commercial", "corporate", "wealth", "investing"
        ]:
            domain = domain_match.group(1).lower()
        else:
            # Fallback: scan for domain keywords in the text
            for d in ["investing", "wealth", "commercial", "sme", "retail"]:
                if d.lower() in intake_text.lower():
                    domain = d
                    break

    # ── Pipeline header ───────────────────────────────────────────────────
    print(f"\n{C.BOLD}{'═' * 60}{C.RESET}")
    print(f"{C.BOLD}  CORTEX PIPELINE ORCHESTRATOR{C.RESET}")
    print(f"{C.BOLD}{'═' * 60}{C.RESET}")
    print(f"  Engagement: {engagement_dir}")
    print(f"  Domain:     {domain}")
    mode = "EXPRESS" if express else ("NON-INTERACTIVE" if non_interactive else "STANDARD")
    print(f"  Mode:       {mode}")
    if resume_from:
        print(f"  Resuming:   from {resume_from}")
    if dry_run:
        print(f"  DRY RUN:    showing plan only")
    print(f"{'═' * 60}\n")

    if dry_run:
        print("Steps that would execute:")
        if non_interactive:
            print("  1. Discovery (parallel extraction + finalize, max_turns=15)")
            print("  2. Block A: Single-phase (5 agents, 40-min timeout each)")
            print("  3. Roadmap (single-pass) + Excel (overlapping)")
            print("  4. Assembly (P1 plan -> 3-way parallel shards -> merge)")
            print("  5. HTML Dashboard (6 partials + Python assembly, max_turns=25)")
            print("  6. Validation gate")
        else:
            print("  1. Discovery (parallel extraction + finalize)")
            print("  2. Block A: P1 (5 agents) -> checkpoint -> P2 (5 agents)")
            print("  3. Roadmap (2-phase with checkpoint)")
            print("  4. Assembly (3-phase with CP2 review)")
            print("  5. HTML + Excel generation (parallel)")
            print("  6. Validation gate")
        return

    steps = ["discovery", "parallel_a", "roadmap", "assembly", "generate", "validate"]
    if resume_from and resume_from in steps:
        steps = steps[steps.index(resume_from):]

    # ── Step 1: Discovery ─────────────────────────────────────────────────
    if "discovery" in steps:
        log_step("1", "DISCOVERY")
        timings["discovery"] = await step_discovery(engagement_dir, outputs_dir, express, non_interactive)

    # ── Step 2: Parallel Block A ──────────────────────────────────────────
    if "parallel_a" in steps:
        # log_step is called inside step_parallel_block_a based on mode
        timings["parallel_a"] = await step_parallel_block_a(
            engagement_dir, outputs_dir, express, domain, non_interactive
        )

    # ── S2: Overlapping stages (non-interactive) ─────────────────────────
    if non_interactive:
        # In non-interactive mode: Roadmap + Excel start in parallel after Block A,
        # then Assembly starts after Roadmap completes

        if "roadmap" in steps or "assembly" in steps or "generate" in steps:
            log_step("3", "ROADMAP + EXCEL (overlapping)")

            # Start Roadmap and Excel in parallel
            roadmap_and_excel = []
            if "roadmap" in steps:
                roadmap_and_excel.append(("roadmap", step_roadmap(
                    engagement_dir, outputs_dir, express, non_interactive)))
            if "generate" in steps and file_exists(outputs_dir / "roi_config.json"):
                roadmap_and_excel.append(("excel", step_generate_excel(
                    engagement_dir, outputs_dir)))

            if roadmap_and_excel:
                tasks = [t[1] for t in roadmap_and_excel]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for (name, _), result in zip(roadmap_and_excel, results):
                    if isinstance(result, Exception):
                        log(f"  ✗ {name} FAILED: {result}", C.RED)
                        timings[name] = {"elapsed": 0, "cost": 0}
                    else:
                        timings[name] = result

        # Assembly (needs roadmap.md from above)
        if "assembly" in steps:
            log_step("4", "ASSEMBLY (parallel shards)")
            timings["assembly"] = await step_assembly(
                engagement_dir, outputs_dir, express, non_interactive)

        # HTML (needs assessment_report.md from assembly)
        if "generate" in steps:
            log_step("5", "HTML DASHBOARD")
            timings["html"] = await step_generate_html(engagement_dir, outputs_dir)

    else:
        # ── Standard/Interactive flow (sequential) ───────────────────────

        if "roadmap" in steps:
            log_step("3", "ROADMAP")
            timings["roadmap"] = await step_roadmap(
                engagement_dir, outputs_dir, express, non_interactive)

        if "assembly" in steps:
            log_step("4", "ASSEMBLY")
            timings["assembly"] = await step_assembly(
                engagement_dir, outputs_dir, express, non_interactive)

        if "generate" in steps:
            log_step("5", "GENERATE HTML + EXCEL (parallel)")
            # Run HTML and Excel in parallel (original behavior)
            gen_tasks = []
            gen_names = []
            if file_exists(outputs_dir / "assessment_report.md"):
                gen_tasks.append(step_generate_html(engagement_dir, outputs_dir))
                gen_names.append("html")
            if file_exists(outputs_dir / "roi_config.json"):
                gen_tasks.append(step_generate_excel(engagement_dir, outputs_dir))
                gen_names.append("excel")
            if gen_tasks:
                results = await asyncio.gather(*gen_tasks, return_exceptions=True)
                for name, result in zip(gen_names, results):
                    if isinstance(result, Exception):
                        log(f"  ✗ {name} FAILED: {result}", C.RED)
                        timings[name] = {"elapsed": 0, "cost": 0}
                    else:
                        timings[name] = result

    # ── Step 6: Validation Gate ───────────────────────────────────────────
    if "validate" in steps:
        log_step("6", "VALIDATION GATE")
        passed = await step_validate(engagement_dir, outputs_dir)
        if not passed:
            log("  Pipeline completed with validation warnings.", C.YELLOW)

    # ── T4: Summary with timing + costs ──────────────────────────────────
    total_time, total_cost = _print_pipeline_summary(timings, pipeline_start)

    print(f"\n  Output files:")
    for f in sorted(outputs_dir.iterdir()):
        if not f.name.startswith("CHECKPOINT") and not f.name.startswith("interim"):
            print(f"    {f.name:40s} {f.stat().st_size:>8,} bytes")

    # Write timing to journal
    journal = engagement_dir / "ENGAGEMENT_JOURNAL.md"
    if journal.exists():
        timing_entry = f"""
---

### {datetime.now().strftime('%Y-%m-%d %H:%M')} — Pipeline Orchestrator V4 (Python)

**Mode:** {'Express' if express else ('Non-Interactive' if non_interactive else 'Standard')}
**Total Duration:** {total_time:.0f}s ({total_time/60:.1f} min)
**Total Cost:** ${total_cost:.2f}

| Step | Duration | Cost |
|------|----------|------|
"""
        for step_name, data in timings.items():
            elapsed = data.get("elapsed", 0)
            step_cost = data.get("cost", 0)
            timing_entry += f"| {step_name} | {elapsed:.0f}s ({elapsed/60:.1f} min) | ${step_cost:.2f} |\n"

        with open(journal, "a") as f:
            f.write(timing_entry)

    print()


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Cortex Pipeline Orchestrator V4 — optimized agent workflow engine"
    )
    parser.add_argument("engagement_dir", type=Path, help="Path to engagement directory")
    parser.add_argument("--express", action="store_true",
                        help="Auto-approve intermediate checkpoints (keeps Discovery + Assembly CP2)")
    parser.add_argument("--resume-from", choices=[
        "discovery", "parallel_a", "roadmap", "assembly", "generate", "validate"
    ], help="Resume from a specific pipeline step")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show pipeline plan without executing")
    parser.add_argument("--non-interactive", action="store_true",
                        help="Auto-approve ALL checkpoints with summaries (for Claude Code /run-pipeline)")
    args = parser.parse_args()

    engagement_dir = args.engagement_dir.resolve()
    if not engagement_dir.exists():
        print(f"Error: {engagement_dir} does not exist", file=sys.stderr)
        sys.exit(1)
    if not (engagement_dir / "inputs").exists():
        print(f"Error: {engagement_dir}/inputs/ does not exist", file=sys.stderr)
        sys.exit(1)

    asyncio.run(run_pipeline(
        engagement_dir,
        express=args.express,
        non_interactive=args.non_interactive,
        resume_from=args.resume_from,
        dry_run=args.dry_run,
    ))


if __name__ == "__main__":
    main()
