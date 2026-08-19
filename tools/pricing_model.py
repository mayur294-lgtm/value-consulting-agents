#!/usr/bin/env python3
"""
Pricing Model — usage-based (AUM / seat / volume) commercial pricing engine.

The price side of the table. Where `roi_excel_generator.py` models the CLIENT'S
benefit, this models what BACKBASE charges and how it scales with the client's
growth — band schedules, smoothing, crossover, margin head-to-head, and the
software-vs-3rd-party back-solve needed for a POF / BAFO submission.

Two layers (both surfaced on real deals):
  1. SCALAR scenario model — 5-yr-total × band multipliers. Drives the scenario
     projection tables and crossover analysis on negotiation decks.
  2. POF granular model — per-line per-year fees; uplift applied to SOFTWARE only;
     3rd-party (pass-through) held flat; back-solve a proportional discount on the
     uplift so the grand total hits a target. (Exactly the Phase-A POF maths.)

Usage:
    python pricing_model.py --config model.json --out model.xlsx     # build workbook
    python pricing_model.py --selftest                               # regression test
    python pricing_model.py --config model.json --crossover A,B      # print a crossover

Config schema: see `--print-schema` or knowledge/learnings/pipeline_gaps/SPEC_pricing-model.md
Origin: knowledge/learnings/pipeline_gaps/deal_desk_commercial_track.md
"""

import json
import argparse
from pathlib import Path

# ── Brand (frontline-tokens.json) ────────────────────────────────────
NAVY = "041326"
BLUE = "3367FF"
LIGHT_BLUE = "E5EBFF"
GREEN = "15803D"
LIGHT_GREEN = "D1FAE5"
GREY = "6B7280"
RED = "DC2626"


# ════════════════════════════════════════════════════════════════════
#  SCALAR SCENARIO MODEL
# ════════════════════════════════════════════════════════════════════

def scalar_price(scenario, g):
    """Fee for a scenario at growth value `g`. Dispatches on `basis`:

      - "band_multiplier" (default · WEALTH / AUM):
            baseline × Π(1+rate) for each band crossed, × top-band smoothing.
      - "tiered_per_unit" (RETAIL / BANKING / LENDING):
            flat platform fee + Σ(units in each volume tier × per-unit rate).
      - "conversational" (CONVERSATIONAL BANKING · banking-os.md §10):
            platform fee + LOB fee + per-interaction (g = monthly interactions).

    All return a fee in the scenario's own value unit; keep scenarios within
    one model internally consistent so they can be compared / crossed.
    """
    basis = scenario.get("basis", "band_multiplier")
    if basis == "tiered_per_unit":
        return price_tiered(scenario, g)
    if basis == "conversational":
        return price_conversational(scenario, g)
    return price_band_multiplier(scenario, g)


def price_band_multiplier(scenario, g):
    """WEALTH / AUM. A band [lo, hi, rate] multiplies the fee by (1+rate) once
    `g` crosses `lo`. The open `top_band` {from, step, rate} compounds
    (1+rate)^((g-from)/step) once `g` exceeds `from` (smoothing = lower rate)."""
    price = float(scenario["baseline"])
    for lo, hi, rate in scenario.get("bands", []):
        if g > lo:
            price *= (1.0 + rate)
    tb = scenario.get("top_band")
    if tb and g > tb["from"]:
        steps = (g - tb["from"]) / tb["step"]
        price *= (1.0 + tb["rate"]) ** steps
    return price


def price_tiered(scenario, g):
    """RETAIL / BANKING / LENDING. Flat platform fee plus a per-unit charge that
    steps down by volume tier — the standard customer/account/loan model.

      flat            : fixed platform fee (same value unit as the output)
      tiers           : list of [lo, hi, per_unit]; hi=null means open-ended.
                        Units between lo and min(g,hi) are charged at per_unit.

    Volume discounting (lower per_unit in higher tiers) is the retail analogue
    of the wealth reducing-uplift curve.
    """
    price = float(scenario.get("flat", 0.0))
    for tier in scenario.get("tiers", []):
        lo, hi, per_unit = tier[0], tier[1], tier[2]
        hi = g if hi is None else min(g, hi)
        if g > lo:
            price += (hi - lo) * per_unit
    return price


def price_conversational(scenario, g):
    """CONVERSATIONAL BANKING (banking-os.md §10). Annual Backbase fee =
    platform fee + LOB fee + per-interaction, where `g` is the MONTHLY
    interaction volume. Per-interaction is volume-tiered on monthly volume and
    annualised (×12). LLM compute is a transparent pass-through billed at cost —
    echoed in Assumptions, NOT added to the Backbase fee here.

      platform_fee        : annual platform fee (Entry/Critical/Enterprise tier)
      lob_fee_per_domain  : annual fee per activated LOB / business domain
      domains             : number of activated domains (default 1)
      lob_included        : domains bundled in the platform fee (default 1)
      lob_waived          : true on Enterprise (all domains included → LOB = 0)
      interaction_tiers   : [lo, hi, per_interaction] on MONTHLY volume; hi=null open
      llm_passthrough_annual : optional · echoed only (pass-through, at cost)
    """
    platform = float(scenario.get("platform_fee", 0.0))
    if scenario.get("lob_waived"):
        lob = 0.0
    else:
        billable = max(0, int(scenario.get("domains", 1)) - int(scenario.get("lob_included", 1)))
        lob = billable * float(scenario.get("lob_fee_per_domain", 0.0))
    monthly = 0.0
    for lo, hi, rate in scenario.get("interaction_tiers", []):
        hi = g if hi is None else min(g, hi)
        if g > lo:
            monthly += (hi - lo) * rate
    return platform + lob + monthly * 12.0


def projection(model):
    """Return {milestone: {scenario_name: price}} across all milestones."""
    sm = model["scalar_model"]
    out = {}
    for g in sm["milestones"]:
        out[g] = {s["name"]: scalar_price(s, g) for s in sm["scenarios"]}
    return out


def find_crossover(model, name_a, name_b, lo=None, hi=None, step=None):
    """Smallest growth value where scenario A and B swap which is cheaper.
    Scan range defaults to the model's milestone span, so it works for any
    metric scale (AUM £bn, customer counts, loan volumes, ...).
    Returns (crossover_value, 'A_cheaper_below'|'B_cheaper_below'|None)."""
    sm = model["scalar_model"]
    sa = next(s for s in sm["scenarios"] if s["name"] == name_a)
    sb = next(s for s in sm["scenarios"] if s["name"] == name_b)
    ms = sm["milestones"]
    if lo is None:
        lo = min(min(ms), sa.get("baseline_at", min(ms)), sb.get("baseline_at", min(ms)))
    if hi is None:
        hi = max(ms)
    if step is None:
        step = max((hi - lo) / 2000.0, 1e-9)
    prev = scalar_price(sa, lo) - scalar_price(sb, lo)
    g = lo
    while g <= hi:
        d = scalar_price(sa, g) - scalar_price(sb, g)
        if prev == 0:
            prev = d
        if d == 0 or (d > 0) != (prev > 0):
            direction = "A_cheaper_below" if prev < 0 else "B_cheaper_below"
            return round(g, 1), direction
        prev = d
        g += step
    return None, None


def margin_h2h(model, name_a, name_b):
    """Per-milestone Backbase-revenue delta between two structures.
    Positive = A yields more to Backbase than B at that milestone."""
    sm = model["scalar_model"]
    sa = next(s for s in sm["scenarios"] if s["name"] == name_a)
    sb = next(s for s in sm["scenarios"] if s["name"] == name_b)
    rows = []
    for g in sm["milestones"]:
        pa, pb = scalar_price(sa, g), scalar_price(sb, g)
        rows.append({"g": g, name_a: pa, name_b: pb, "delta_A_minus_B": pa - pb})
    return rows


# ════════════════════════════════════════════════════════════════════
#  POF GRANULAR MODEL  (software vs 3rd-party, back-solve discount)
# ════════════════════════════════════════════════════════════════════

def pof_backsolve(pof):
    """Apply uplift to SOFTWARE only; hold 3rd-party flat; back-solve a
    proportional discount on the uplift so software+uplift+3rd-party = target.

    Returns a dict with per-year breakdown, the solved discount, and totals.
    Reproduces the deal-desk POF maths exactly.
    """
    sw = [float(x) for x in pof["software_by_year"]]
    tp = [float(x) for x in pof["thirdparty_by_year"]]
    rate = float(pof["uplift_rate"])
    target = float(pof["target_total"])

    sw_total = sum(sw)
    tp_total = sum(tp)
    uplift_year = [s * rate for s in sw]          # full uplift per year
    uplift_total = sum(uplift_year)

    needed_uplift = target - sw_total - tp_total  # how much uplift the target leaves room for
    if uplift_total == 0:
        discount = 0.0
    else:
        discount = 1.0 - (needed_uplift / uplift_total)   # proportional reduction on uplift

    revised_uplift_year = [u * (1.0 - discount) for u in uplift_year]
    total_year = [sw[i] + revised_uplift_year[i] + tp[i] for i in range(len(sw))]

    return {
        "software_by_year": sw,
        "thirdparty_by_year": tp,
        "uplift_full_by_year": uplift_year,
        "revised_uplift_by_year": revised_uplift_year,
        "total_by_year": total_year,
        "software_total": sw_total,
        "thirdparty_total": tp_total,
        "uplift_full_total": uplift_total,
        "revised_uplift_total": sum(revised_uplift_year),
        "discount_on_uplift": discount,
        "grand_total": sum(total_year),
        "target_total": target,
        "uplift_rate": rate,
    }


# ════════════════════════════════════════════════════════════════════
#  XLSX OUTPUT
# ════════════════════════════════════════════════════════════════════

def build_xlsx(model, out_path):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    cur = model.get("currency", "£")
    unit = model.get("unit", "bn")
    metric = model.get("metric", "AUM")
    disp = model.get("display", {})
    div = float(disp.get("divisor", 1))   # divide fee values for display (e.g. 1e6 for absolute → M)
    suf = disp.get("suffix", "M")         # fee display suffix
    mpre = model.get("metric_prefix", cur)   # growth-axis label prefix (currency for AUM, "" for counts)
    msuf = model.get("metric_suffix", unit)  # growth-axis label suffix ("bn", " cust", ...)
    glabel = lambda g: f"{mpre}{g:,}{msuf}"  # format a growth-metric value for display
    thin = Side(border_style="thin", color="D1D5DB")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    def hdr(ws, row, headers, start=1):
        for i, h in enumerate(headers):
            c = ws.cell(row=row, column=start + i, value=h)
            c.font = Font(bold=True, color="FFFFFF", size=10)
            c.fill = PatternFill("solid", fgColor=NAVY)
            c.alignment = Alignment(horizontal="center", wrap_text=True)
            c.border = border

    def money_fmt(cell):
        cell.number_format = f'"{cur}"#,##0.00,,"M"' if False else '#,##0.00'

    wb = Workbook()

    # ── Tab 1 · Scenarios projection ──────────────────────────────────
    ws = wb.active
    ws.title = "Scenarios"
    ws["A1"] = f"{model.get('client','Client')} — pricing scenarios across {metric} growth"
    ws["A1"].font = Font(bold=True, size=14, color=NAVY)
    sm = model["scalar_model"]
    names = [s["name"] for s in sm["scenarios"]]
    hdr(ws, 3, [metric] + names)
    proj = projection(model)
    r = 4
    for g in sm["milestones"]:
        ws.cell(row=r, column=1, value=glabel(g)).font = Font(bold=True, color=NAVY, size=10)
        ws.cell(row=r, column=1).border = border
        for i, nm in enumerate(names):
            c = ws.cell(row=r, column=2 + i, value=round(proj[g][nm] / div, 2))
            c.number_format = f'"{cur}"#,##0.00"{suf}"'
            c.alignment = Alignment(horizontal="right")
            c.border = border
        r += 1
    for i, w in enumerate([16] + [18] * len(names)):
        ws.column_dimensions[get_column_letter(1 + i)].width = w

    # ── Tab 2 · Crossovers ────────────────────────────────────────────
    ws2 = wb.create_sheet("Crossovers")
    ws2["A1"] = "Scenario crossovers (where the cheaper option swaps)"
    ws2["A1"].font = Font(bold=True, size=13, color=NAVY)
    hdr(ws2, 3, ["Pair", "Crossover " + metric, "Read"])
    r = 4
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            cv, direction = find_crossover(model, names[i], names[j])
            read = "no crossover in range" if cv is None else \
                f"{names[i] if 'A_cheaper' in (direction or '') else names[j]} cheaper below {glabel(cv)}"
            ws2.cell(row=r, column=1, value=f"{names[i]}  vs  {names[j]}").border = border
            ws2.cell(row=r, column=2, value=(glabel(cv) if cv else "—")).border = border
            ws2.cell(row=r, column=3, value=read).border = border
            r += 1
    for i, w in enumerate([34, 18, 46]):
        ws2.column_dimensions[get_column_letter(1 + i)].width = w

    # ── Tab 3 · Margin H2H (first two scenarios, if >=2) ───────────────
    if len(names) >= 2:
        a, b = names[-2], names[-1]  # default: compare the last two (usually the live options)
        ws3 = wb.create_sheet("Margin H2H")
        ws3["A1"] = f"Backbase revenue head-to-head — {a}  vs  {b}"
        ws3["A1"].font = Font(bold=True, size=13, color=NAVY)
        ws3["A2"] = "Positive delta = the first option yields more to Backbase at that point."
        ws3["A2"].font = Font(italic=True, size=10, color=GREY)
        hdr(ws3, 4, [metric, a, b, f"{a} − {b}", "Better for Backbase"])
        r = 5
        for row in margin_h2h(model, a, b):
            ws3.cell(row=r, column=1, value=glabel(row['g'])).font = Font(bold=True, color=NAVY)
            for col, key in [(2, a), (3, b), (4, "delta_A_minus_B")]:
                c = ws3.cell(row=r, column=col, value=round(row[key] / div, 2))
                c.number_format = f'"{cur}"#,##0.00"{suf}"'
                c.alignment = Alignment(horizontal="right")
                c.border = border
            better = a if row["delta_A_minus_B"] > 0 else (b if row["delta_A_minus_B"] < 0 else "tie")
            cc = ws3.cell(row=r, column=5, value=better)
            cc.font = Font(bold=True, color=BLUE if better == a else (GREEN if better == b else GREY))
            cc.border = border
            ws3.cell(row=r, column=1).border = border
            r += 1
        for i, w in enumerate([14, 18, 18, 16, 22]):
            ws3.column_dimensions[get_column_letter(1 + i)].width = w

    # ── Tab 4 · POF split (if present) ────────────────────────────────
    if "pof" in model:
        res = pof_backsolve(model["pof"])
        ws4 = wb.create_sheet("POF Split")
        ws4["A1"] = "Price-of-Failure split — uplift on software only, 3rd-party held flat"
        ws4["A1"].font = Font(bold=True, size=13, color=NAVY)
        ws4["A2"] = (f"Target total {cur}{res['target_total']:,.0f}  ·  uplift rate {res['uplift_rate']*100:.0f}%"
                     f"  ·  solved discount on uplift {res['discount_on_uplift']*100:.4f}%")
        ws4["A2"].font = Font(italic=True, size=10, color=GREY)
        nyr = len(res["software_by_year"])
        hdr(ws4, 4, ["Line"] + [f"Yr {i+1}" for i in range(nyr)] + ["5-Yr Total"])
        tp_label = model["pof"].get("thirdparty_label", "3rd-party (pass-through)")
        rows = [
            ("Software base fee", res["software_by_year"], res["software_total"], NAVY),
            (f"Uplift @ {res['uplift_rate']*100:.0f}% (full)", res["uplift_full_by_year"], res["uplift_full_total"], GREY),
            ("Uplift after discount", res["revised_uplift_by_year"], res["revised_uplift_total"], GREEN),
            (tp_label + " (flat)", res["thirdparty_by_year"], res["thirdparty_total"], BLUE),
            ("TOTAL", res["total_by_year"], res["grand_total"], NAVY),
        ]
        r = 5
        for label, series, tot, color in rows:
            cl = ws4.cell(row=r, column=1, value=label)
            cl.font = Font(bold=(label == "TOTAL"), color=color, size=10)
            cl.border = border
            for i, v in enumerate(series):
                c = ws4.cell(row=r, column=2 + i, value=round(v, 2))
                c.number_format = '#,##0'
                c.alignment = Alignment(horizontal="right")
                c.border = border
            ct = ws4.cell(row=r, column=2 + nyr, value=round(tot, 2))
            ct.number_format = '#,##0'
            ct.font = Font(bold=True, color=color)
            ct.alignment = Alignment(horizontal="right")
            ct.border = border
            if label == "TOTAL":
                for col in range(1, 3 + nyr):
                    ws4.cell(row=r, column=col).fill = PatternFill("solid", fgColor=LIGHT_GREEN)
            r += 1
        ws4.column_dimensions["A"].width = 30
        for i in range(nyr + 1):
            ws4.column_dimensions[get_column_letter(2 + i)].width = 14

    # ── Tab 5 · Assumptions ───────────────────────────────────────────
    wsa = wb.create_sheet("Assumptions")
    wsa["A1"] = "Assumptions & inputs (echo of the config — every number traces here)"
    wsa["A1"].font = Font(bold=True, size=13, color=NAVY)
    r = 3
    for s in sm["scenarios"]:
        basis = s.get("basis", "band_multiplier")
        wsa.cell(row=r, column=1, value=s["name"]).font = Font(bold=True, color=NAVY)
        if basis == "tiered_per_unit":
            wsa.cell(row=r, column=2, value=f"[tiered_per_unit] flat fee {cur}{s.get('flat',0):,.0f}")
            r += 1
            for tier in s.get("tiers", []):
                lo, hi, pu = tier[0], tier[1], tier[2]
                hi_lbl = "∞" if hi is None else f"{hi:,}"
                wsa.cell(row=r, column=2, value=f"{lo:,}–{hi_lbl} {metric}: {cur}{pu}/unit")
                r += 1
        elif basis == "conversational":
            wsa.cell(row=r, column=2, value=f"[conversational] platform fee {cur}{s.get('platform_fee',0):,.0f}/yr")
            r += 1
            if s.get("lob_waived"):
                wsa.cell(row=r, column=2, value="LOB: all domains included (Enterprise — waived)")
                r += 1
            else:
                wsa.cell(row=r, column=2, value=f"LOB: {s.get('domains',1)} domains · {s.get('lob_included',1)} included · {cur}{s.get('lob_fee_per_domain',0):,.0f}/domain/yr")
                r += 1
            for lo, hi, rate in s.get("interaction_tiers", []):
                hi_lbl = "∞" if hi is None else f"{hi:,}"
                wsa.cell(row=r, column=2, value=f"{lo:,}–{hi_lbl}/mo: {cur}{rate}/interaction")
                r += 1
            if s.get("llm_passthrough_annual"):
                wsa.cell(row=r, column=2, value=f"+ LLM compute pass-through ~{cur}{s['llm_passthrough_annual']:,.0f}/yr (at cost, billed separately)")
                r += 1
        else:
            wsa.cell(row=r, column=2, value=f"[band_multiplier] baseline {cur}{s['baseline']}{suf} at {cur}{s.get('baseline_at','?')}{unit}")
            r += 1
            for lo, hi, rate in s.get("bands", []):
                wsa.cell(row=r, column=2, value=f"{cur}{lo}–{hi}{unit}: +{rate*100:.0f}%")
                r += 1
            tb = s.get("top_band")
            if tb:
                wsa.cell(row=r, column=2, value=f"{cur}{tb['from']}{unit}+ per {cur}{tb['step']}{unit}: +{tb['rate']*100:.0f}%")
                r += 1
        r += 1
    wsa.column_dimensions["A"].width = 22
    wsa.column_dimensions["B"].width = 48

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_path)
    return out_path


# ════════════════════════════════════════════════════════════════════
#  SELF-TEST  (synthetic wealth/AUM regression fixture — real-deal parity runs
#  locally, never committed)
# ════════════════════════════════════════════════════════════════════

# WEALTH / AUM fixture. Every value is a synthetic round number authored for this
# test — no client figures. Shape matches a live wealth structure (4 scenarios,
# 3 stepped bands + an open smoothing band, a 5-year POF split) so the same code
# paths are exercised: band crossings, top-band smoothing, POF back-solve with a
# non-zero discount.
WEALTH_FIXTURE = {
    "client": "Synthetic Wealth Regression", "currency": "£", "unit": "bn", "metric": "AUM",
    "scalar_model": {
        "milestones": [150, 200, 250, 300, 400, 500, 600, 700, 800, 1000],
        "scenarios": [
            {"name": "Baseline", "baseline": 10.00, "baseline_at": 100,
             "bands": [[100, 200, 0.10], [200, 300, 0.08], [300, 400, 0.06]],
             "top_band": {"from": 400, "step": 100, "rate": 0.05}},
            {"name": "Option A", "baseline": 10.00, "baseline_at": 100,
             "bands": [[100, 200, 0.10], [200, 300, 0.08], [300, 400, 0.06]],
             "top_band": {"from": 400, "step": 100, "rate": 0.04}},
            {"name": "Option B", "baseline": 12.00, "baseline_at": 200,
             "bands": [[200, 300, 0.08], [300, 400, 0.06]],
             "top_band": {"from": 400, "step": 100, "rate": 0.03}},
            {"name": "Option C", "baseline": 11.50, "baseline_at": 200,
             "bands": [[200, 300, 0.08], [300, 400, 0.06]],
             "top_band": {"from": 400, "step": 100, "rate": 0.04}},
        ],
    },
    "pof": {
        "uplift_rate": 0.10,
        "target_total": 11_750_000,
        "software_by_year": [1_000_000, 2_000_000, 2_000_000, 2_500_000, 2_500_000],
        "thirdparty_by_year": [200_000, 150_000, 150_000, 250_000, 250_000],
        "thirdparty_label": "Marketplace (3rd-party)",
    },
}

# Expected scalar 5-yr totals — hand-computed from WEALTH_FIXTURE above.
# A band [lo, hi, rate] multiplies once g > lo; the top band compounds
# (1+rate)^((g-from)/step) once g > from.
#
#   Baseline / Option A (baseline 10.00, bands +10% / +8% / +6% from 100/200/300):
#     @150  : 10.00 × 1.10                             = 11.00
#     @250  : 10.00 × 1.10 × 1.08                      = 11.88
#     @400  : 10.00 × 1.10 × 1.08 × 1.06               = 12.5928        → 12.59
#     @500  : 12.5928 × 1.04       (A, 1 step  @4%)    = 13.096512      → 13.10
#             12.5928 × 1.05       (Baseline, 1 step)  = 13.22244       → 13.22
#     @600  : 12.5928 × 1.04^2 = 12.5928 × 1.0816      = 13.62037…      → 13.62
#     @1000 : 12.5928 × 1.04^6 = 12.5928 × 1.26531902  = 15.93391…      → 15.93
#             12.5928 × 1.05^6 = 12.5928 × 1.34009564  = 16.87556…      → 16.88
#
#   Option B (baseline 12.00, bands +8% / +6% from 200/300, top +3%/100):
#     @250  : 12.00 × 1.08                             = 12.96
#     @300  : 12.00 × 1.08   (300 > 300 is false)      = 12.96
#     @400  : 12.96 × 1.06                             = 13.7376        → 13.74
#     @500  : 13.7376 × 1.03                           = 14.149728      → 14.15
#     @600  : 13.7376 × 1.03^2 = 13.7376 × 1.0609      = 14.57422…      → 14.57
#     @1000 : 13.7376 × 1.03^6 = 13.7376 × 1.19405230  = 16.40341…      → 16.40
#
#   Option C (baseline 11.50, bands +8% / +6% from 200/300, top +4%/100):
#     @250  : 11.50 × 1.08                             = 12.42
#     @400  : 12.42 × 1.06                             = 13.1652        → 13.17
#     @500  : 13.1652 × 1.04                           = 13.691808      → 13.69
#     @600  : 13.1652 × 1.04^2 = 13.1652 × 1.0816      = 14.23948…      → 14.24
#     @1000 : 13.1652 × 1.04^6 = 13.1652 × 1.26531902  = 16.65818…      → 16.66
EXPECT_SCALAR = {
    "Option A": {150: 11.00, 250: 11.88, 400: 12.59, 500: 13.10, 600: 13.62, 1000: 15.93},
    "Option B": {250: 12.96, 300: 12.96, 400: 13.74, 500: 14.15, 600: 14.57, 1000: 16.40},
    "Option C": {250: 12.42, 400: 13.17, 500: 13.69, 600: 14.24, 1000: 16.66},
    "Baseline": {500: 13.22, 1000: 16.88},
}

# RETAIL / BANKING / LENDING flavour (illustrative — NOT real numbers from a
# retail fellowship deal).
# Per-customer volume tiering with a flat platform fee. Demonstrates the second
# pricing basis the engine supports; numbers are hand-computed for regression.
RETAIL_FIXTURE = {
    "client": "Illustrative Retail Bank", "currency": "€", "unit": "", "metric": "customers",
    "display": {"divisor": 1_000_000, "suffix": "M"},
    "metric_prefix": "", "metric_suffix": " cust",
    "scalar_model": {
        "milestones": [50000, 100000, 300000, 500000, 600000, 1000000],
        "scenarios": [
            {"name": "Standard", "basis": "tiered_per_unit", "flat": 2_000_000,
             "tiers": [[0, 100000, 40], [100000, 500000, 30], [500000, None, 20]]},
            {"name": "Committed", "basis": "tiered_per_unit", "flat": 3_000_000,
             "tiers": [[0, 100000, 32], [100000, 500000, 24], [500000, None, 16]]},
        ],
    },
}
# Hand-computed expected absolute totals for the Standard tiered scenario:
#   50k : 2,000,000 + 50,000×40                                   = 4,000,000
#   300k: 2,000,000 + 100,000×40 + 200,000×30                    = 12,000,000
#   600k: 2,000,000 + 100,000×40 + 400,000×30 + 100,000×20       = 20,000,000
EXPECT_TIERED = {"Standard": {50000: 4_000_000, 300000: 12_000_000, 600000: 20_000_000}}

# CONVERSATIONAL BANKING flavour (banking-os.md §10 — illustrative reference rates).
# g = MONTHLY interaction volume. Annual fee = platform + LOB + per-interaction×12.
CONVERSATIONAL_FIXTURE = {
    "client": "Illustrative Conversational Banking", "currency": "€", "unit": "",
    "metric": "interactions", "metric_prefix": "", "metric_suffix": "/mo",
    "display": {"divisor": 1_000_000, "suffix": "M"},
    "scalar_model": {
        "milestones": [250_000, 500_000, 1_000_000, 2_000_000, 3_000_000],
        "scenarios": [
            {"name": "Critical · 3 domains", "basis": "conversational",
             "platform_fee": 700_000, "lob_fee_per_domain": 350_000,
             "domains": 3, "lob_included": 1, "lob_waived": False,
             "interaction_tiers": [[0, 500_000, 0.070], [500_000, 2_000_000, 0.063], [2_000_000, None, 0.057]],
             "llm_passthrough_annual": 300_000},
            {"name": "Enterprise · all domains", "basis": "conversational",
             "platform_fee": 1_500_000, "lob_fee_per_domain": 350_000,
             "domains": 4, "lob_included": 4, "lob_waived": True,
             "interaction_tiers": [[0, 500_000, 0.070], [500_000, 2_000_000, 0.063], [2_000_000, None, 0.057]]},
        ],
    },
}
# Hand-computed annual totals (platform + LOB + per-interaction×12):
#   Critical(3dom): platform 700k + LOB (3-1)×350k=700k + interaction×12
#     @1.0M/mo: (500k×.070 + 500k×.063)=66,500/mo ×12 = 798,000 → 700k+700k+798k = 2,198,000
#     @2.0M/mo: (500k×.070 + 1.5M×.063)=129,500/mo ×12 = 1,554,000 → = 2,954,000
#   Enterprise: platform 1.5M + LOB 0 (waived) + interaction×12
#     @1.0M/mo: 1,500,000 + 798,000 = 2,298,000
EXPECT_CONVERSATIONAL = {
    "Critical · 3 domains": {250_000: 1_610_000, 500_000: 1_820_000, 1_000_000: 2_198_000,
                             2_000_000: 2_954_000, 3_000_000: 3_638_000},
    "Enterprise · all domains": {1_000_000: 2_298_000, 2_000_000: 3_054_000},
}


def selftest():
    ok = True
    # 1 · WEALTH / AUM — band_multiplier basis
    print("— WEALTH (band_multiplier) —")
    for scen, points in EXPECT_SCALAR.items():
        s = next(x for x in WEALTH_FIXTURE["scalar_model"]["scenarios"] if x["name"] == scen)
        for g, expected in points.items():
            got = round(scalar_price(s, g), 2)
            mark = "ok" if got == expected else "FAIL"
            if got != expected:
                ok = False
            print(f"  {scen:>8} @ £{g}bn = £{got:.2f}M  (expect £{expected:.2f}M)  [{mark}]")
    # 1b · RETAIL / LENDING — tiered_per_unit basis
    print("— RETAIL (tiered_per_unit) —")
    for scen, points in EXPECT_TIERED.items():
        s = next(x for x in RETAIL_FIXTURE["scalar_model"]["scenarios"] if x["name"] == scen)
        for v, expected in points.items():
            got = round(scalar_price(s, v), 2)
            mark = "ok" if got == expected else "FAIL"
            if got != expected:
                ok = False
            print(f"  {scen:>8} @ {v:,} cust = €{got:,.0f}  (expect €{expected:,.0f})  [{mark}]")
    # 1c · CONVERSATIONAL BANKING — conversational basis
    print("— CONVERSATIONAL (platform + LOB + per-interaction) —")
    for scen, points in EXPECT_CONVERSATIONAL.items():
        s = next(x for x in CONVERSATIONAL_FIXTURE["scalar_model"]["scenarios"] if x["name"] == scen)
        for v, expected in points.items():
            got = round(scalar_price(s, v), 2)
            mark = "ok" if got == expected else "FAIL"
            if got != expected:
                ok = False
            print(f"  {scen[:20]:>20} @ {v:,}/mo = €{got:,.0f}  (expect €{expected:,.0f})  [{mark}]")
    print("— POF back-solve —")
    # 2 · POF back-solve
    res = pof_backsolve(WEALTH_FIXTURE["pof"])
    # Hand-computed from WEALTH_FIXTURE["pof"] (uplift on software only, 3rd-party flat):
    #   software total   = 1,000,000 + 2,000,000 + 2,000,000 + 2,500,000 + 2,500,000 = 10,000,000
    #   3rd-party total  =   200,000 +   150,000 +   150,000 +   250,000 +   250,000 =  1,000,000
    #   full uplift @10% = 10,000,000 × 0.10                                          =  1,000,000
    #   room left by the target = 11,750,000 − 10,000,000 − 1,000,000                 =    750,000
    #   discount on uplift     = 1 − 750,000 / 1,000,000 = 0.25                       =    25.0000%
    #   revised uplift total   = 1,000,000 × (1 − 0.25)                               =    750,000
    #   grand total            = 10,000,000 + 750,000 + 1,000,000                     = 11,750,000
    checks = [
        ("discount on uplift", round(res["discount_on_uplift"] * 100, 4), 25.0),
        ("revised uplift total", round(res["revised_uplift_total"], 0), 750000.0),
        ("grand total", round(res["grand_total"], 0), 11750000.0),
    ]
    for label, got, expected in checks:
        mark = "ok" if got == expected else "FAIL"
        if got != expected:
            ok = False
        print(f"  POF {label:>22} = {got}  (expect {expected})  [{mark}]")
    print("\nSELFTEST:", "PASS ✓" if ok else "FAIL ✗")
    return ok


# ════════════════════════════════════════════════════════════════════
def main():
    ap = argparse.ArgumentParser(description="Usage-based commercial pricing engine")
    ap.add_argument("--config", help="JSON pricing config")
    ap.add_argument("--out", help="output xlsx path")
    ap.add_argument("--crossover", help="two scenario names, comma-separated (e.g. A,B)")
    ap.add_argument("--selftest", action="store_true", help="run regression test")
    ap.add_argument("--print-schema", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        raise SystemExit(0 if selftest() else 1)
    if args.print_schema:
        print(json.dumps(WEALTH_FIXTURE, indent=2))
        return
    if not args.config:
        ap.error("provide --config (or --selftest)")

    model = json.loads(Path(args.config).read_text())
    if args.crossover:
        a, b = args.crossover.split(",")
        cv, d = find_crossover(model, a.strip(), b.strip())
        print(f"Crossover {a}/{b}: {cv}  ({d})")
        return
    out = args.out or "pricing_model.xlsx"
    path = build_xlsx(model, out)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
