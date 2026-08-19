"""proposal-engine component evaluator (objective, code-only — no LLM).

Verifies the CANONICAL deal engine `tools/proposal_builder.py` as the pipeline
actually invokes it: a subprocess run against a committed synthetic config,
scored on the JSON it writes. Nothing here imports the engine's internals, so a
check fails when the CLI contract breaks, not only when a function does.

  engine_runs_clean                     `--config <golden> --json <tmp>` exits 0 and writes
                                        parseable JSON.
  selftest_passes                       the engine's own `--selftest` (determinism + the
                                        codified negotiation rules) is green — the adopted
                                        test suite, run by the gate rather than trusted.
  exit_arr_flag_recomputed              the exit-ARR / downsell guard: reported_arr, exit_arr,
                                        downsell_exposure and `flag` are recomputed HERE from
                                        the config (TCV/term vs the final-year ramp fee) and
                                        compared to the engine's block. A ramped deal reports
                                        the average annual fee as ARR while the bank exits the
                                        term paying the final-year fee; the flag is what stops
                                        churn exposure being sized off the wrong number.
  buffer_arithmetic_correct             the buffer play is a PRICE HOLD: ramp_price =
                                        buffer_units x (software_tcv / commit_units), and
                                        saving_vs_ramp = ramp_price - buffer_price, both
                                        recomputed independently; the give-to-get conditions
                                        must be present (a hold without conditions is a
                                        discount wearing a different name).
  pricing_provenance_passthrough        deal_type / round / pricing_source travel into the
                                        output untouched — every downstream artifact has to be
                                        able to cite where the numbers came from.
  deterministic_output                  two runs of the same config produce byte-identical
                                        JSON (same inputs_hash) — "no LLM in the numbers".
  hard_error_on_missing_pricing_inputs  a config with the pricing block removed must exit
                                        NON-ZERO. Silently defaulting missing deal inputs to
                                        zero would emit a confident strategy built on nothing.

OBSERVED LIMIT OF THE HARD-ERROR RULE (deliberately encoded to what is true, not
to what would be nicer): the engine hard-errors when the `deal` block is ABSENT
(KeyError -> non-zero exit). A config carrying an EMPTY `deal: {}` still exits 0
and produces a zeroed strategy. The negative fixture therefore removes the whole
block, and the empty-block gap is recorded in the ticket report rather than
asserted here as if it already held.

target: path to a deal-config JSON golden (self-contained; the negative fixture
is loaded by name, the same way rubrics.component.roi_excel_generator loads its
paired backward-compat golden — the components altitude wires only one `input:`).
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from rubrics.base import CheckResult, repo_root

_ENGINE = "tools/proposal_builder.py"
_MISSING_PRICING_NEGATIVE = "evals/goldens/negatives/deal_config_missing_pricing.json"


def _bool(name: str, ok: bool, *, detail: str = "", evidence: list[str] | None = None) -> CheckResult:
    return CheckResult(name, 1.0 if ok else 0.0, ok, detail=detail, evidence=evidence or [])


def _run(config_path: str) -> tuple[int, str, str]:
    """Run the engine on a config, returning (rc, stdout_json_text, stderr_tail)."""
    root = repo_root()
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "strategy.json"
        proc = subprocess.run(
            [sys.executable, str(root / _ENGINE), "--config", str(config_path),
             "--json", str(out), "--out", str(Path(td) / "brief.md")],
            cwd=str(root), capture_output=True, text=True,
        )
        text = out.read_text() if out.exists() else ""
    return proc.returncode, text, (proc.stderr or "")[-300:]


def _strategy(target: str) -> tuple[dict | None, str]:
    rc, text, err = _run(target)
    if rc != 0:
        return None, f"engine exited {rc}: {err}"
    if not text:
        return None, "engine exited 0 but wrote no JSON"
    try:
        return json.loads(text), ""
    except json.JSONDecodeError as e:
        return None, f"engine JSON invalid: {e}"


def _config(target: str) -> dict:
    return json.loads(Path(target).read_text())


# ── checks ──────────────────────────────────────────────────────────────────

def _check_runs_clean(target: str, s: dict | None, err: str) -> CheckResult:
    return _bool("engine_runs_clean", s is not None,
                 detail="exit 0, parseable strategy JSON" if s is not None else err)


def _check_selftest(target: str, s: dict | None, err: str) -> CheckResult:
    root = repo_root()
    proc = subprocess.run([sys.executable, str(root / _ENGINE), "--selftest"],
                          cwd=str(root), capture_output=True, text=True)
    ok = proc.returncode == 0
    tail = (proc.stdout or proc.stderr or "").strip().splitlines()
    return _bool("selftest_passes", ok,
                 detail=(tail[0] if tail else "no output") if ok
                 else f"--selftest exited {proc.returncode}",
                 evidence=[] if ok else tail[-4:])


def _check_exit_arr(target: str, s: dict | None, err: str) -> CheckResult:
    if s is None:
        return _bool("exit_arr_flag_recomputed", False, detail=err)
    cfg = _config(target)
    deal = cfg["deal"]
    ramp = deal.get("ramp_schedule") or {}
    if not ramp:
        return _bool("exit_arr_flag_recomputed", False,
                     detail="golden config carries no ramp_schedule — the guard is not exercised")
    block = s.get("exit_arr")
    if not block:
        return _bool("exit_arr_flag_recomputed", False,
                     detail="ramped config produced no exit_arr block")
    software = deal.get("software_tcv") or sum(l.get("total", 0) for l in deal.get("lines", []))
    total = software + deal.get("thirdparty_tcv", 0)
    term = deal.get("term_years", 5)
    expect_reported = round(total / term, 1) if term else float(total)
    expect_exit = ramp[max(ramp, key=lambda y: int(y))]
    expect_flag = expect_exit > expect_reported
    diffs = []
    if block.get("reported_arr") != expect_reported:
        diffs.append(f"reported_arr {block.get('reported_arr')} != {expect_reported}")
    if block.get("exit_arr") != expect_exit:
        diffs.append(f"exit_arr {block.get('exit_arr')} != {expect_exit}")
    if block.get("downsell_exposure") != expect_exit:
        diffs.append(f"downsell_exposure {block.get('downsell_exposure')} != {expect_exit}")
    if bool(block.get("flag")) != expect_flag:
        diffs.append(f"flag {block.get('flag')} != {expect_flag}")
    return _bool("exit_arr_flag_recomputed", not diffs,
                 detail=(f"reported {expect_reported} vs exit {expect_exit} → flag {expect_flag}"
                         if not diffs else f"{len(diffs)} mismatch(es)"),
                 evidence=diffs)


def _check_buffer(target: str, s: dict | None, err: str) -> CheckResult:
    if s is None:
        return _bool("buffer_arithmetic_correct", False, detail=err)
    cfg = _config(target)
    bo = (cfg.get("strategy") or {}).get("buffer_offer") or {}
    if not bo:
        return _bool("buffer_arithmetic_correct", False,
                     detail="golden config carries no buffer_offer — the price hold is not exercised")
    block = s.get("buffer")
    if not block:
        return _bool("buffer_arithmetic_correct", False, detail="buffer_offer given but no buffer block emitted")
    deal = cfg["deal"]
    software = deal.get("software_tcv") or sum(l.get("total", 0) for l in deal.get("lines", []))
    commit, buf = bo.get("commit_units", 0), bo.get("buffer_units", 0)
    price = bo.get("buffer_price", 0)
    expect_ramp = round(buf * (software / commit), 1) if commit else 0.0
    expect_saving = round(expect_ramp - price, 1)
    diffs = []
    if block.get("ramp_price") != expect_ramp:
        diffs.append(f"ramp_price {block.get('ramp_price')} != {expect_ramp}")
    if block.get("buffer_price") != price:
        diffs.append(f"buffer_price {block.get('buffer_price')} != {price}")
    if block.get("saving_vs_ramp") != expect_saving:
        diffs.append(f"saving_vs_ramp {block.get('saving_vs_ramp')} != {expect_saving}")
    if not block.get("conditions"):
        diffs.append("no give-to-get conditions on the price hold")
    return _bool("buffer_arithmetic_correct", not diffs,
                 detail=(f"ramp {expect_ramp} − hold {price} = saving {expect_saving}, "
                         f"{len(block.get('conditions') or [])} condition(s)"
                         if not diffs else f"{len(diffs)} mismatch(es)"),
                 evidence=diffs)


def _check_provenance(target: str, s: dict | None, err: str) -> CheckResult:
    if s is None:
        return _bool("pricing_provenance_passthrough", False, detail=err)
    cfg = _config(target)
    deal = cfg["deal"]
    diffs = []
    for key in ("deal_type", "round"):
        if key in deal and s.get(key) != deal[key]:
            diffs.append(f"{key} {s.get(key)!r} != {deal[key]!r}")
    ps_in, ps_out = deal.get("pricing_source"), s.get("pricing_source")
    if ps_in:
        if not ps_out:
            diffs.append("pricing_source not emitted")
        else:
            for k in ("source", "date"):
                if ps_out.get(k) != ps_in.get(k):
                    diffs.append(f"pricing_source.{k} {ps_out.get(k)!r} != {ps_in.get(k)!r}")
    else:
        diffs.append("golden config carries no pricing_source — provenance is not exercised")
    return _bool("pricing_provenance_passthrough", not diffs,
                 detail=(f"deal_type={s.get('deal_type')} round={s.get('round')} "
                         f"source={(ps_out or {}).get('source')!r} ({(ps_out or {}).get('date')})"
                         if not diffs else f"{len(diffs)} mismatch(es)"),
                 evidence=diffs)


def _check_determinism(target: str, s: dict | None, err: str) -> CheckResult:
    if s is None:
        return _bool("deterministic_output", False, detail=err)
    _, first, _ = _run(target)
    _, second, _ = _run(target)
    ok = bool(first) and first == second
    return _bool("deterministic_output", ok,
                 detail=(f"two runs byte-identical ({len(first)} bytes, trace "
                         f"{s.get('provenance', {}).get('inputs_hash')})" if ok
                         else "two runs of the same config differ"))


def _check_hard_error(target: str, s: dict | None, err: str) -> CheckResult:
    neg = repo_root() / _MISSING_PRICING_NEGATIVE
    if not neg.exists():
        return _bool("hard_error_on_missing_pricing_inputs", False,
                     detail=f"negative fixture missing: {_MISSING_PRICING_NEGATIVE}")
    rc, text, stderr = _run(str(neg))
    ok = rc != 0 and not text
    return _bool("hard_error_on_missing_pricing_inputs", ok,
                 detail=(f"config with the pricing block removed exits {rc} and writes no strategy"
                         if ok else
                         f"exited {rc} and wrote {len(text)} bytes of strategy — missing pricing "
                         f"inputs were defaulted instead of refused"),
                 evidence=[stderr.strip().splitlines()[-1]] if (ok and stderr.strip()) else [])


CHECKS = (_check_runs_clean, _check_selftest, _check_exit_arr, _check_buffer,
          _check_provenance, _check_determinism, _check_hard_error)


def evaluate(target: str) -> list[CheckResult]:
    """target: path to a deal-config JSON golden."""
    p = Path(target)
    if not p.exists():
        return [CheckResult("deal_config_readable", 0.0, False, hard_fail=True,
                            detail=f"fixture not found: {target}")]
    s, err = _strategy(target)
    return [fn(target, s, err) for fn in CHECKS]
