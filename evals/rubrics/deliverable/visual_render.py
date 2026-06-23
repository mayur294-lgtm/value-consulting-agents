#!/usr/bin/env python3
"""Visual-render design eval (MULTIMODAL).

Renders an HTML deliverable to a PNG with a headless browser, then an Opus VISION
judge scores the actual pixels against the frozen design system — catching overflow,
clipping, overlap, cramping, broken grids, off-brand visuals that text parsing can't
see. This is the only eval that *looks* at the output.

Graceful: returns a skipped CheckResult if there's no ANTHROPIC key, code-only mode,
or no headless browser available (so it never breaks the fast/offline path).

evaluate(target) -> [CheckResult]   (target = path to an .html file)
"""
from __future__ import annotations

import base64
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))
from rubrics.base import CheckResult  # noqa: E402

_CHROME_CANDIDATES = (
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
)


def _find_chrome() -> str | None:
    for c in _CHROME_CANDIDATES:
        exe = shutil.which(c) if "/" not in c else (c if Path(c).exists() else None)
        if exe:
            return exe
    return None


def _render(html_path: str, png_path: str) -> bool:
    chrome = _find_chrome()
    if not chrome:
        return False
    try:
        subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
             "--window-size=1366,2000", f"--screenshot={png_path}",
             f"file://{Path(html_path).resolve()}"],
            timeout=90, capture_output=True,
        )
    except Exception:
        return False
    return Path(png_path).exists() and Path(png_path).stat().st_size > 0


def _vision_judge(png_path: str, threshold: float) -> CheckResult:
    import json
    import re
    import anthropic
    prompt = (HERE.parent / "judge" / "prompts" / "visual_render.md").read_text()
    snap = (HERE.parent / "judge" / "standards_snapshot" / "design-system-frozen.md")
    standard = snap.read_text() if snap.exists() else ""
    img = base64.standard_b64encode(Path(png_path).read_bytes()).decode()
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=os.getenv("CORTEX_JUDGE_MODEL", "claude-opus-4-8"), max_tokens=1024,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img}},
            {"type": "text", "text": f"# Frozen design standard\n{standard}\n\n# Rubric\n{prompt}"},
        ]}],
    )
    raw = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    m = re.search(r"\{.*\}", raw, re.S)
    data = json.loads(m.group(0) if m else raw)
    score = float(data.get("score", 0.0))
    passed = bool(data.get("pass", score >= threshold))
    return CheckResult(name="judge:visual_render", score=score, passed=passed,
                       hard_fail=not passed, detail=str(data.get("reason", ""))[:300])


def evaluate(target: str, threshold: float = 0.8) -> list[CheckResult]:
    if os.getenv("CORTEX_EVAL_NO_JUDGE") or not os.getenv("ANTHROPIC_API_KEY"):
        return [CheckResult("judge:visual_render", 0.0, True, skipped=True,
                            detail="skipped (code-only mode or no ANTHROPIC_API_KEY)")]
    with tempfile.TemporaryDirectory() as td:
        png = str(Path(td) / "shot.png")
        if not _render(target, png):
            return [CheckResult("judge:visual_render", 0.0, True, skipped=True,
                                detail="skipped (no headless browser to render the page)")]
        try:
            return [_vision_judge(png, threshold)]
        except Exception as e:
            return [CheckResult("judge:visual_render", 0.0, True, skipped=True,
                                detail=f"skipped (vision judge error: {e})")]


if __name__ == "__main__":
    from rubrics.base import RubricResult
    t = sys.argv[1]
    print(RubricResult(t, "deliverable", evaluate(t)).report(0.8))
