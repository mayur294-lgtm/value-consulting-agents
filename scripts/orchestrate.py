#!/usr/bin/env python3
"""
Cortex Pipeline Orchestrator — Python-driven workflow engine.

Replaces the markdown orchestrator with deterministic code.
LLM agents handle content (analysis, writing, modeling).
This script handles workflow (sequencing, checkpoints, validation, parallelism).

Usage:
    python scripts/orchestrate.py <engagement_dir>
    python scripts/orchestrate.py --express <engagement_dir>
    python scripts/orchestrate.py --resume-from <step> <engagement_dir>
    python scripts/orchestrate.py --dry-run <engagement_dir>
    python scripts/orchestrate.py --non-interactive <engagement_dir>   # for Claude Code /run-pipeline

The existing .claude/agents/*.md files are unchanged — this runs alongside them.
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
) -> float:
    """Run Discovery: parallel lean extraction → Python checkpoint → finalize from interims."""
    start = time.time()
    inputs_dir = engagement_dir / "inputs"
    transcripts = sorted(inputs_dir.glob("transcript_*.md"))
    intake = inputs_dir / "engagement_intake.md"

    if not transcripts:
        log("  ⚠ No transcripts found in inputs/", C.YELLOW)
        return 0

    log(f"  Found {len(transcripts)} transcript(s)")

    if len(transcripts) == 1:
        # Single transcript: lean extraction → Python checkpoint
        prompt = f"""PHASE DIRECTIVE: Phase 1 of 2
Engagement directory: {engagement_dir}

Read and process this transcript: {transcripts[0]}
Read the engagement context: {intake}

Extract evidence items, pain points, metrics, and stakeholder intelligence.
Write your findings to: {outputs_dir}/interim_transcript_1.md
{_LEAN_FORMAT}
"""
        await run_agent(
            "discovery-transcript-interpreter", prompt,
            cwd=engagement_dir,
            label="Discovery (1 transcript)",
            max_turns=15,
        )
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

    # Generate checkpoint in Python (no LLM) — instant
    _generate_discovery_checkpoint(outputs_dir, transcripts)

    # Checkpoint review
    present_checkpoint("discovery", outputs_dir, express=False, non_interactive=non_interactive)

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
    await run_agent(
        "discovery-transcript-interpreter", prompt,
        cwd=engagement_dir,
        label="Discovery (finalize)",
    )

    # Validate
    assert_file_exists(outputs_dir / "evidence_register.md", "Discovery")
    assert_file_exists(outputs_dir / "pain_points.md", "Discovery")
    assert_file_exists(outputs_dir / "metrics.md", "Discovery")

    return time.time() - start


async def step_parallel_block_a(
    engagement_dir: Path,
    outputs_dir: Path,
    express: bool,
    domain: str,
    non_interactive: bool = False,
) -> float:
    """Run 5 agents in parallel after Discovery: JB, MC, Cap, ROI, Bench."""
    start = time.time()
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

    # ── Phase 1: Launch all 5 simultaneously ──────────────────────────────

    log_step("3A", "PARALLEL BLOCK A — Phase 1 (5 agents simultaneously)")

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

    # Report any failures
    agent_names = ["journey-builder", "market-context", "capability", "roi_CP1", "benchmark"]
    for name, result in zip(agent_names, results):
        if isinstance(result, Exception):
            log(f"  ✗ {name} Phase 1 FAILED: {result}", C.RED)

    # ── Checkpoints (batched) ─────────────────────────────────────────────

    checkpoint_agents = ["journey-builder", "market-context", "capability", "roi_CP1", "benchmark"]
    # Only present checkpoints for agents that produced files
    available = [a for a in checkpoint_agents if (outputs_dir / f"CHECKPOINT_{a}.md").exists()]
    present_checkpoints_batched(available, outputs_dir, express=express, non_interactive=non_interactive)

    # ── Phase 2: Launch all 5 again ───────────────────────────────────────

    log_step("3B", "PARALLEL BLOCK A — Phase 2 (5 agents simultaneously)")

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

    # Validate required outputs
    assert_file_exists(outputs_dir / "capability_assessment.md", "Capability")
    assert_file_exists(outputs_dir / "roi_report.md", "ROI")
    assert_file_exists(outputs_dir / "roi_config.json", "ROI")

    # These are important but not blocking
    for f, name in [
        ("journey_maps.json", "Journey Builder"),
        ("market_context_validated.md", "Market Context"),
        ("benchmarks_validated.md", "Benchmark"),
    ]:
        if file_exists(outputs_dir / f):
            log(f"  ✓ {f} ({(outputs_dir / f).stat().st_size:,} bytes)", C.GREEN)
        else:
            log(f"  ⚠ {f} not produced by {name} (non-blocking)", C.YELLOW)

    return time.time() - start


async def step_roadmap(
    engagement_dir: Path,
    outputs_dir: Path,
    express: bool,
    non_interactive: bool = False,
) -> float:
    """Run Roadmap agent (depends on ROI + Capability)."""
    start = time.time()

    # Single-pass in express mode, two-phase otherwise
    if express:
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
        await run_agent("roadmap-prioritization", prompt, engagement_dir, label="Roadmap (single-pass)")
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
        await run_agent("roadmap-prioritization", prompt, engagement_dir, label="Roadmap P1")
        present_checkpoint("roadmap", outputs_dir, express=False, non_interactive=non_interactive)

        # Phase 2
        prompt = f"""PHASE DIRECTIVE: Phase 2 of 2
Engagement directory: {engagement_dir}

Read approved checkpoint: {outputs_dir}/CHECKPOINT_roadmap_APPROVED.md
Read draft: {outputs_dir}/CHECKPOINT_roadmap.md

REQUIRED OUTPUT FILES:
- {outputs_dir}/roadmap.md
"""
        await run_agent("roadmap-prioritization", prompt, engagement_dir, label="Roadmap P2")

    assert_file_exists(outputs_dir / "roadmap.md", "Roadmap")
    return time.time() - start


async def step_assembly(
    engagement_dir: Path,
    outputs_dir: Path,
    express: bool,
    non_interactive: bool = False,
) -> float:
    """Run Narrative Assembler (reads all upstream, 2 checkpoints)."""
    start = time.time()
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

    # Phase 1: Assembly plan
    prompt = f"""PHASE DIRECTIVE: Phase 1 of 3
Engagement directory: {engagement_dir}

Read ALL upstream outputs:
{all_outputs}

Also read: {inputs_dir}/engagement_intake.md

Build the 7-act narrative structure and assembly plan.

Write: {outputs_dir}/CHECKPOINT_assembly_CP1.md
"""
    await run_agent("narrative-assembler", prompt, engagement_dir, label="Assembly P1")
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
    await run_agent("narrative-assembler", prompt, engagement_dir, label="Assembly P2")

    # Assembly CP2 ALWAYS pauses — this is the final report review
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
    await run_agent("narrative-assembler", prompt, engagement_dir, label="Assembly P3")

    assert_file_exists(outputs_dir / "assessment_report.md", "Assembly")
    assert_file_exists(outputs_dir / "executive_summary.md", "Assembly")
    return time.time() - start


async def step_generate_outputs(
    engagement_dir: Path,
    outputs_dir: Path,
) -> float:
    """Generate HTML dashboard and ROI Excel in parallel."""
    start = time.time()

    html_prompt = f"""You are generating an interactive HTML assessment dashboard.

Read and follow: {COMMANDS_DIR / 'generate-assessment-html.md'}
Read the design system: {KNOWLEDGE_DIR / 'design-system.md'}

Engagement directory: {engagement_dir}
Read all output files in: {outputs_dir}/

Generate a single self-contained HTML file.
Write it to: {outputs_dir}/assessment_dashboard.html

The file MUST be >200KB and contain interactive navigation, capability heatmaps,
journey visualizations, and the full 7-act narrative.
"""

    excel_prompt = f"""You are generating a ROI Excel model.

Read and follow: {COMMANDS_DIR / 'generate-roi-excel.md'}

Read the ROI config: {outputs_dir}/roi_config.json
Read the ROI report: {outputs_dir}/roi_report.md

Generate the Excel model using the roi_excel_generator tool or by writing
the Excel file directly.

Write the output to: {outputs_dir}/
"""

    # Check prerequisites
    has_html_inputs = file_exists(outputs_dir / "assessment_report.md")
    has_excel_inputs = file_exists(outputs_dir / "roi_config.json")

    tasks = []
    if has_html_inputs:
        tasks.append(run_agent(
            "narrative-assembler", html_prompt, engagement_dir,
            label="HTML Dashboard", max_turns=80,
        ))
    else:
        log("  ⚠ Skipping HTML — assessment_report.md not found", C.YELLOW)

    if has_excel_inputs:
        tasks.append(run_agent(
            "roi-business-case-builder", excel_prompt, engagement_dir,
            label="ROI Excel", max_turns=30,
        ))
    else:
        log("  ⚠ Skipping Excel — roi_config.json not found", C.YELLOW)

    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

    # Validate
    html_files = glob_files("*.html", outputs_dir)
    if html_files:
        for h in html_files:
            log(f"  ✓ {h.name} ({h.stat().st_size:,} bytes)", C.GREEN)
    else:
        log("  ✗ No HTML dashboard produced", C.RED)

    xlsx_files = glob_files("*.xlsx", outputs_dir)
    if xlsx_files:
        for x in xlsx_files:
            log(f"  ✓ {x.name} ({x.stat().st_size:,} bytes)", C.GREEN)

    return time.time() - start


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
    timings: dict[str, float] = {}

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
        print("  1. Discovery (sequential, per transcript)")
        print("  2. Parallel Block A: JB + MC + Cap + ROI + Bench (×2 phases)")
        print("  3. Roadmap (depends on ROI + Cap)")
        print("  4. Assembly (3 phases, 2 checkpoints)")
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
        log_step("2", "PARALLEL BLOCK A (5 agents simultaneously)")
        timings["parallel_a"] = await step_parallel_block_a(
            engagement_dir, outputs_dir, express, domain, non_interactive
        )

    # ── Step 3: Roadmap ───────────────────────────────────────────────────
    if "roadmap" in steps:
        log_step("3", "ROADMAP")
        timings["roadmap"] = await step_roadmap(engagement_dir, outputs_dir, express, non_interactive)

    # ── Step 4: Assembly ──────────────────────────────────────────────────
    if "assembly" in steps:
        log_step("4", "ASSEMBLY")
        timings["assembly"] = await step_assembly(engagement_dir, outputs_dir, express, non_interactive)

    # ── Step 5: Generate HTML + Excel ─────────────────────────────────────
    if "generate" in steps:
        log_step("5", "GENERATE HTML + EXCEL (parallel)")
        timings["generate"] = await step_generate_outputs(engagement_dir, outputs_dir)

    # ── Step 6: Validation Gate ───────────────────────────────────────────
    if "validate" in steps:
        log_step("6", "VALIDATION GATE")
        passed = await step_validate(engagement_dir, outputs_dir)
        if not passed:
            log("  Pipeline completed with validation warnings.", C.YELLOW)

    # ── Summary ───────────────────────────────────────────────────────────
    total_time = time.time() - pipeline_start
    print(f"\n{C.BOLD}{C.GREEN}{'═' * 60}{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}  PIPELINE COMPLETE{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}{'═' * 60}{C.RESET}")
    print(f"\n  Timing breakdown:")
    for step_name, elapsed in timings.items():
        print(f"    {step_name:20s} {elapsed:6.0f}s  ({elapsed/60:.1f} min)")
    print(f"    {'─' * 35}")
    print(f"    {'TOTAL':20s} {total_time:6.0f}s  ({total_time/60:.1f} min)")
    print(f"\n  Output files:")
    for f in sorted(outputs_dir.iterdir()):
        if not f.name.startswith("CHECKPOINT") and not f.name.startswith("interim"):
            print(f"    {f.name:40s} {f.stat().st_size:>8,} bytes")

    # Write timing to journal
    journal = engagement_dir / "ENGAGEMENT_JOURNAL.md"
    if journal.exists():
        timing_entry = f"""
---

### {datetime.now().strftime('%Y-%m-%d %H:%M')} — Pipeline Orchestrator (Python)

**Mode:** {'Express' if express else 'Standard'}
**Total Duration:** {total_time:.0f}s ({total_time/60:.1f} min)

| Step | Duration |
|------|----------|
"""
        for step_name, elapsed in timings.items():
            timing_entry += f"| {step_name} | {elapsed:.0f}s ({elapsed/60:.1f} min) |\n"

        with open(journal, "a") as f:
            f.write(timing_entry)

    print(f"\n  Total cost: check Claude dashboard for session costs")
    print()


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Cortex Pipeline Orchestrator — deterministic agent workflow engine"
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
