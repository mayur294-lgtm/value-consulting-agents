#!/usr/bin/env python3
"""
Proposal Builder — deterministic deal-strategy engine for the VC team.

The brain behind the `/proposal-builder` skill. Given a parsed CPQ deal plus the
intel only a consultant holds (the 5 lever families, switching cost, context), it
computes — DETERMINISTICALLY — the negotiation strategy: anchor, Good/Better/Best
scenarios, the Martini concession ladder, the approval tier at each step, the Deal
Desk trigger check + submission pack, and a LEVER LEDGER (what's used vs what's
still open). Same input → same output, every time. No LLM in the numbers.

The skill (Claude) runs the GATED INTERVIEW that fills the config; this engine does
the math and the rules. Output: a strategy JSON + a human-readable strategy brief
(the trace / explainability artifact). The skill then renders the client proposal
via /proposal-longform using the JSON.

Usage:
    python proposal_builder.py --config deal.json --json out.json --out brief.md
    python proposal_builder.py --config deal.json            # brief to stdout
    python proposal_builder.py --selftest                    # determinism + rules test
    python proposal_builder.py --print-schema                # config schema

Rule sources (codified, authoritative):
    knowledge/domains/negotiation/negotiation-tactics.md  (§1 Martini, §2 ladder,
        §3 lever families, §4 lever types, §6 floor economics, §9 Deal Desk)
    knowledge/domains/pricing/pricing-methodology.md       (basis × LOB)
"""

import json
import argparse
import hashlib
import re
from pathlib import Path

# ════════════════════════════════════════════════════════════════════
#  CODIFIED RULES  (deterministic — traceable to negotiation-tactics.md)
# ════════════════════════════════════════════════════════════════════

# §1 — the Martini: cumulative share of the discount budget given by each stage.
MARTINI = [0.0, 0.60, 0.90, 1.0]            # Anchor → C1 → C2 → BAFO  (shrinking)

# §2 — the 4-stage concession ladder (posture · NBA · what you EXTRACT in return)
STAGES = [
    {"key": "anchor", "name": "Anchor", "posture": "Firm. Zero upfront.",
     "nba": "Present the full-scope value case, state no discount, secure agreement in principle.",
     "extract": "Reference rights · value baseline"},
    {"key": "counter1", "name": "Counter 1", "posture": "Biggest move, cheap-weighted.",
     "nba": "Largest concession now, weighted to cheap levers, paired to a signed term.",
     "extract": "Signed 5-yr term + reference rights"},
    {"key": "counter2", "name": "Counter 2", "posture": "Smaller move, structure + price.",
     "nba": "Visibly smaller move. Trade the volume discount only against prepay + expansion.",
     "extract": "Year-one prepay + written expansion commit"},
    {"key": "bafo", "name": "Best & Final", "posture": "Smallest move, floor + closer.",
     "nba": "Smallest move, dated and final. Price-hold addendum to Deal Desk. State the deadline once.",
     "extract": "Final & dated · price-hold gated to Deal Desk"},
]

# §9 — discount authority by region price list (% list)
TIER_BANDS = {
    100: [("List", 0), ("SVP", 20), ("CRO", 40), ("Deal Desk", 10_000)],
    70:  [("List", 0), ("SVP", 40), ("CRO", 60), ("Deal Desk", 10_000)],
}

# §3 — the 5 lever families: canonical sub-levers (everything is "open" until the VC spends it)
FAMILIES = [
    {"n": 1, "name": "Solution optionality", "margin": "Zero margin cost",
     "rule": "Anchor here. Reframe price → configuration.",
     "levers": ["Good/Better/Best", "Bundle / unbundle", "Phasing", "Scope ramp"]},
    {"n": 2, "name": "Commitment terms", "margin": "Often margin-accretive",
     "rule": "Trade before any price move.",
     "levers": ["3/5/10-yr term", "Volume tier", "Year-one prepay", "Expansion commit"]},
    {"n": 3, "name": "Non-price value", "margin": "Capacity cost",
     "rule": "Price the bench, don't gift it.",
     "levers": ["Sandbox", "Training credits", "Premium support / SLA", "Program architect", "Dedicated CS", "Advisory seat"]},
    {"n": 4, "name": "Timing & cash flow", "margin": "Cost of capital only",
     "rule": "Eases the buyer's budget, barely touches margin.",
     "levers": ["Payment terms", "Stub bill", "Staggered activation", "Billing cadence"]},
    {"n": 5, "name": "Price", "margin": "1:1 margin hit",
     "rule": "Last resort. Sets the renewal reference.",
     "levers": ["Volume discount", "VPA / price hold", "Renewal cap"]},
]

# §2 / §5 — the buffer play is a PRICE HOLD, never a discount: the give-to-get list
# that must be pre-agreed before the price of growth is held.
BUFFER_CONDITIONS = [
    "Timing of commitment",
    "No attrition on current agreements",
    "Inclusions & exclusions agreed",
    "Contract term held",
    "Funding commitment confirmed",
]

# §6 — bands
DEAL_SIZE = [("large", 10_000), ("mid", 3_000), ("small", 0)]      # £k TCV
HEADROOM = [("ample", 18.0), ("moderate", 8.0), ("tight", 0.0)]    # % to floor

# §9 — Deal Desk GM thresholds (healthy floor; below = trigger)
GM_THRESHOLDS = {
    "gm_arr_pct": 83, "managed_hosting_gm_pct": 25, "managed_services_gm_pct": 45,
    "professional_services_gm_pct": 35, "first_year_arr_pct": 60,
}

RULE_SOURCE = "knowledge/domains/negotiation/negotiation-tactics.md (§1–§9)"


# ════════════════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════════════════

def band_of(value, table):
    for name, lo in table:
        if value >= lo:
            return name
    return table[-1][0]


def approval_tier(discount_pct, list_pct):
    bands = TIER_BANDS.get(int(list_pct), TIER_BANDS[100])
    if discount_pct <= 0:
        return "List"
    for name, hi in bands[1:]:
        if discount_pct <= hi:
            return name
    return "Deal Desk"


def svp_cap(list_pct):
    return TIER_BANDS.get(int(list_pct), TIER_BANDS[100])[1][1]


def max_discount_to_floor(gm_pct, floor_gm_pct):
    """§6 — the most you can discount before the floor GM is breached.
    margin after discount D stays >= floor  ⇒  D <= (gm - floor)/(1 - floor)."""
    g, f = gm_pct / 100.0, floor_gm_pct / 100.0
    if f >= 1:
        return 0.0
    return max(0.0, round((g - f) / (1 - f) * 100, 1))


def fmt_m(n, cur="£"):
    return f"{cur}{n/1000:.1f}M"


def require(deal, name):
    """Gate 8 — money inputs are never defaulted. A missing required field is a
    hard stop (non-zero exit), the same refusal as a missing `deal` block."""
    if name not in deal or deal[name] is None:
        raise SystemExit(f"Missing required deal field: {name} — no defaults for money (Gate 8)")
    return deal[name]


# ════════════════════════════════════════════════════════════════════
#  ENGINE
# ════════════════════════════════════════════════════════════════════

def build_strategy(cfg):
    deal = cfg["deal"]
    # Required money inputs — no silent defaults (Gate 8: "there are no defaults
    # for money"). eur_per_unit stays optional: it has a documented default.
    cur = require(deal, "currency")
    list_pct = require(deal, "region_list_pct")
    term = require(deal, "term_years")
    eur_rate = deal.get("eur_per_unit", 1.0 if cur == "€" else 1.17)

    # ── economics ────────────────────────────────────────────────────
    software = deal.get("software_tcv")
    if software is None:
        software = sum(l.get("total", 0) for l in deal.get("lines", []))
    thirdparty = deal.get("thirdparty_tcv", 0)
    total = software + thirdparty
    acv = total / term if term else total
    acv_eur = acv * eur_rate

    econ = cfg.get("economics", {})
    gm = econ.get("gm_arr_pct")
    floor = econ.get("floor_gm_pct")
    headroom = max_discount_to_floor(gm, floor) if (gm is not None and floor is not None) else None

    economics = {
        "software_tcv": software, "thirdparty_tcv": thirdparty, "total_tcv": total,
        "acv": round(acv, 1), "acv_eur": round(acv_eur, 1),
        "gm_arr_pct": gm, "floor_gm_pct": floor,
        "max_discount_to_floor_pct": headroom,
        "headroom_band": band_of(headroom, HEADROOM) if headroom is not None else None,
        "deal_size_band": band_of(total, DEAL_SIZE),
    }

    # ── scenarios (the two-scenario mandate) ─────────────────────────
    scen_cfg = cfg.get("scenarios", {})
    strat = cfg.get("strategy", {})
    anchor_id = strat.get("anchor", "best")
    alt_id = strat.get("alt", "better")
    names = {"good": "Good · Digital Foundation", "better": "Better · Engagement Platform",
             "best": "Best · Full scope"}
    scenarios = []
    for sid in ("good", "better", "best"):
        if sid in scen_cfg:
            role = "anchor (A)" if sid == anchor_id else ("alternative (B)" if sid == alt_id else "decoy")
            scenarios.append({"id": sid, "name": scen_cfg.get(sid + "_name", names[sid]),
                              "tcv": scen_cfg[sid], "role": role})

    # ── concession ladder (deterministic Martini) ────────────────────
    target = float(strat.get("target_bafo_discount_pct", 0))
    capped = headroom is not None and target > headroom
    ladder = []
    for i, stg in enumerate(STAGES):
        cum = round(MARTINI[i] * target, 1)
        prev = round(MARTINI[i - 1] * target, 1) if i else 0.0
        price = software * (1 - cum / 100.0)
        ladder.append({
            "stage": stg["name"], "posture": stg["posture"], "nba": stg["nba"],
            "extract": stg["extract"], "cum_discount_pct": cum,
            "increment_pct": round(cum - prev, 1),
            "price": round(price, 1), "price_fmt": fmt_m(price, cur),
            "tier": approval_tier(cum, list_pct),
        })
    increments = [s["increment_pct"] for s in ladder[1:]]
    shape_ok = all(increments[k] >= increments[k + 1] - 0.05 for k in range(len(increments) - 1))

    # Approval ladder display — the Deal Desk band is "everything above the last
    # named cap", so its lower bound is read off the band table (bands[-2][1] =
    # the CRO cap), never derived from the SVP cap. On the 70% price list the CRO
    # cap is 60, not 2 × the SVP cap.
    bands = TIER_BANDS.get(int(list_pct), TIER_BANDS[100])
    deal_desk_lower = bands[-2][1]
    approval = {
        "bafo_discount_pct": target,
        "tier_at_bafo": approval_tier(target, list_pct),
        "capped_to_floor": capped,
        "svp_cap_pct": svp_cap(list_pct),
        "ladder": [{"who": w, "rng": r} for w, r in
                   [("List", "0%")] + [(n, f"≤ {h}%" if h < 1000 else f"> {deal_desk_lower}%")
                                        for n, h in bands[1:]]],
    }

    # ── Deal Desk gate (§9) ──────────────────────────────────────────
    triggers = []

    def trg(label, fires, detail):
        triggers.append({"label": label, "fires": bool(fires), "detail": detail})

    if gm is not None:
        trg("GM ARR < 83%", gm < GM_THRESHOLDS["gm_arr_pct"], f"~{gm}% (floor 83%)")
    trg("ARR ACV > €2M", acv_eur > 2000, f"ACV {fmt_m(acv, cur)} ≈ €{acv_eur/1000:.1f}M")
    metric = deal.get("exceptional_metric")
    if metric:
        trg(f"Exceptional pricing metric ({metric})", True, f"{metric} applied — always routes to Deal Desk")
    trg("ARR discount above SVP authority", approval_tier(target, list_pct) not in ("List", "SVP"),
        f"BAFO −{target}% → {approval_tier(target, list_pct)} tier")
    # €600K threshold — compare in EUR, like the ACV trigger above, so a deal
    # priced in £ (or any non-EUR unit) is not measured against a euro number.
    total_eur = total * eur_rate
    if deal.get("new_logo") and total_eur < 600:
        trg("New logo < €600K", True, f"{fmt_m(total, cur)} TCV ≈ €{total_eur/1000:.1f}M")
    if term > 5:
        trg("Term > 5 years", True, f"{term}-yr term")
    if deal.get("custom_dev"):
        trg("Custom dev / roadmap request", True, "flagged")
    for key, label in [("managed_hosting_gm_pct", "Managed Hosting GM < 25%"),
                       ("managed_services_gm_pct", "Managed Services GM < 45%"),
                       ("professional_services_gm_pct", "Professional Services GM < 35%"),
                       ("first_year_arr_pct", "1st-year ARR ramp < 60%")]:
        if key in econ:
            trg(label, econ[key] < GM_THRESHOLDS[key], f"~{econ[key]}% (floor {GM_THRESHOLDS[key]}%)")

    required = any(t["fires"] for t in triggers)
    deal_desk = {
        "required": required,
        "triggers": triggers,
        "pack": [
            "Complete commercial model — ARR + Professional Services + Managed Services",
            "Gross Margin by component (subscription · hosting · services · ecosystem)",
            "Digital Solutioning Document summary",
            "RFF — Request for Features (product, pre-aligned)",
            "Deal QA — delivery-risk summary",
        ],
        "decision": ["Approve", "Clarify", "Reject"],
        "cadence": "Thursday review · submit COB Tuesday",
    }

    # ── lever ledger (§3/§4) — used vs OPEN (the explainability core) ─
    lev_cfg = cfg.get("levers", {})
    families, used_n, open_n = [], 0, 0
    for fam in FAMILIES:
        spec = lev_cfg.get(f"{fam['n']}_{fam['name'].lower().split()[0]}", {}) or \
               lev_cfg.get(str(fam["n"]), {})
        used = spec.get("used", [])
        extract = spec.get("extract", [])
        na = spec.get("na", [])
        explicit_open = spec.get("open")
        if explicit_open is not None:
            open_lv = explicit_open
        else:
            taken = set(used) | set(na)
            open_lv = [l for l in fam["levers"] if l not in taken and not any(l in u for u in used)]
        used_n += len(used)
        open_n += len(open_lv)
        families.append({
            "n": fam["n"], "name": fam["name"], "margin": fam["margin"], "rule": fam["rule"],
            "used": used, "extract": extract, "open": open_lv, "na": na,
        })
    lever_ledger = {"families": families, "used_count": used_n, "open_count": open_n}
    # ONE ENTRY PER LEVER — reserve is counted in levers, so the round-over-round
    # diff in INTERNAL_deal_state.json shows exactly which lever got spent. A
    # per-family grouping would hide that (and breaks the deal-state contract).
    open_levers = [f"Family {f['n']} ({f['name']}): {lever}"
                   for f in families for lever in f["open"]]

    # ── leverage posture (§5) ────────────────────────────────────────
    ctx = cfg.get("context", {})
    sw = ctx.get("switching_cost", "medium")
    posture = {"high": "Anchor firm — lock-in is leverage, not a reason to discount.",
               "medium": "Standard anchor — protect price, trade structure.",
               "low": "Lead with non-price value, hold the floor tightly."}.get(sw, "Standard anchor.")
    leverage = {"switching_cost": sw, "posture": posture}

    # ── rationale (why) — traced to rules ────────────────────────────
    a_name = next((s["name"] for s in scenarios if s["id"] == anchor_id), anchor_id)
    b_name = next((s["name"] for s in scenarios if s["id"] == alt_id), alt_id)
    rationale = [
        f"Anchor on {a_name}: Family 1 (solution optionality) is zero-margin-cost — it reframes price as configuration (§3, §7).",
        f"Present two scenarios — {a_name} (anchor) and {b_name} (deliberately lighter) — to frame a configuration choice, not a price ask (§7).",
        f"Concessions follow the Martini ({'→'.join(str(x) for x in MARTINI)} of budget): each move smaller than the last (§1).",
        f"BAFO −{target}% sits in the {approval_tier(target, list_pct)} tier for a {list_pct}% price list (§9).",
    ]
    if headroom is not None:
        rationale.append(f"Floor headroom is {headroom}% to a {floor}% GM floor ({economics['headroom_band']}); the {target}% BAFO "
                         + ("EXCEEDS the floor — re-scope before committing." if capped else "stays within the floor (§6)."))
    if required:
        fired = [t["label"] for t in triggers if t["fires"]]
        rationale.append(f"Routes to Deal Desk on: {', '.join(fired)} (§9) — the tool assembles the pack, it doesn't bypass the review.")

    # ── exit-ARR / downsell guard ────────────────────────────────────
    # A ramped deal reports the AVERAGE annual fee as ARR, but the bank exits the
    # term paying the FINAL-YEAR fee. On churn/downsell the exposure is the exit
    # run-rate, not the reported average. Conservative bias: flag on
    # strictly-greater.
    # LIKE-FOR-LIKE BASIS: ramp_schedule carries SOFTWARE annual fees, so the
    # reported figure here is software_tcv / term — NOT the blended ACV
    # ((software + third-party) / term) reported in economics. Blending the bases
    # lets third-party revenue inflate the average and suppress the flag.
    ramp = deal.get("ramp_schedule") or {}
    exit_arr_block = None
    if ramp:
        final_year = max(ramp, key=lambda y: int(y))
        exit_arr_v = ramp[final_year]
        reported_arr_v = round(software / term, 1) if term else float(software)
        exit_arr_block = {
            "reported_arr": reported_arr_v,
            "exit_arr": exit_arr_v,
            "downsell_exposure": exit_arr_v,
            "flag": bool(exit_arr_v > reported_arr_v),
        }

    # ── buffer play (Family 5 · price hold, NOT a discount) ──────────
    # Pre-agree the price of future growth at today's unit economics. The
    # "travel story" prices what that growth would have cost at the anchor's
    # per-unit price — it is a hold, never a discount.
    bo = strat.get("buffer_offer") or {}
    buffer_block = None
    if bo:
        commit_units = bo.get("commit_units", 0) or 0
        buffer_units = bo.get("buffer_units", 0) or 0
        buffer_price = bo.get("buffer_price", 0) or 0
        unit_price = (software / commit_units) if commit_units > 0 else 0.0
        ramp_price = round(buffer_units * unit_price, 1)
        buffer_block = {
            "ramp_price": ramp_price,
            "buffer_price": buffer_price,
            "saving_vs_ramp": round(ramp_price - buffer_price, 1),
            "conditions": list(BUFFER_CONDITIONS),
            # inputs echoed so the brief can state the offer without re-reading cfg
            "commit_units": commit_units,
            "buffer_units": buffer_units,
        }

    if exit_arr_block and exit_arr_block["flag"]:
        rationale.append(
            f"Reported ARR {fmt_m(exit_arr_block['reported_arr'], cur)} understates the exit run-rate "
            f"{fmt_m(exit_arr_block['exit_arr'], cur)} — size downsell/churn exposure off the exit ARR, not the average (§6).")
    if buffer_block:
        rationale.append(
            "The buffer is a PRICE HOLD on future growth, not a discount — it is gated on the give-to-get "
            "conditions and does not reset the renewal reference (§4, §5).")

    cfg_hash = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:8]

    out = {
        "deal": {k: deal.get(k) for k in ("client", "lob", "basis", "region_list_pct", "term_years", "currency")},
        "economics": economics,
        "scenarios": scenarios,
        "anchor": {"id": anchor_id, "name": a_name},
        "alternative": {"id": alt_id, "name": b_name,
                        "why": strat.get("why_alt", ""), "walkaway": strat.get("walkaway", "")},
        "concession_ladder": ladder,
        "shape": {"name": "Martini", "valid": shape_ok},
        "approval": approval,
        "deal_desk": deal_desk,
        "lever_ledger": lever_ledger,
        "open_levers": open_levers,
        "leverage": leverage,
        "rationale": rationale,
        "provenance": {"generated_by": "proposal_builder.py", "rule_source": RULE_SOURCE,
                       "inputs_hash": cfg_hash},
    }

    # ── optional pass-through metadata + new blocks ──────────────────
    # Emitted ONLY when supplied, so a config without the new fields yields
    # byte-identical output to the pre-change engine.
    if "deal_type" in deal:
        out["deal_type"] = deal["deal_type"]          # new_logo | renewal | expansion (no math)
    if "round" in deal or "deal_type" in deal:
        out["round"] = deal.get("round", 1)           # default 1 for a typed deal
    if deal.get("pricing_source"):
        out["pricing_source"] = deal["pricing_source"]
    if exit_arr_block:
        out["exit_arr"] = exit_arr_block
    if buffer_block:
        out["buffer"] = buffer_block

    return out


# ════════════════════════════════════════════════════════════════════
#  BRIEF (the trace / explainability artifact)
# ════════════════════════════════════════════════════════════════════

def render_brief(s):
    cur = s["deal"].get("currency", "£")
    e = s["economics"]
    L = []
    L.append(f"# Deal strategy brief — {s['deal'].get('client','(deal)')}")
    L.append(f"_{s['deal'].get('lob','')} · {s['deal'].get('basis','')} basis · "
             f"{s['deal'].get('region_list_pct')}% price list · trace `{s['provenance']['inputs_hash']}`_\n")

    L.append("## The deal")
    L.append(f"- 5-yr TCV **{fmt_m(e['total_tcv'],cur)}** (software {fmt_m(e['software_tcv'],cur)} + "
             f"3rd-party {fmt_m(e['thirdparty_tcv'],cur)}) · ACV {fmt_m(e['acv'],cur)} ≈ €{e['acv_eur']/1000:.1f}M")
    L.append(f"- Deal size: **{e['deal_size_band']}** · "
             + (f"GM ~{e['gm_arr_pct']}% · floor headroom **{e['max_discount_to_floor_pct']}%** ({e['headroom_band']})"
                if e['max_discount_to_floor_pct'] is not None else "GM/floor not supplied"))
    if s.get("deal_type"):
        L.append(f"- Deal type: **{s['deal_type']}** · negotiation round {s.get('round', 1)}")
    if s.get("pricing_source"):
        ps = s["pricing_source"]
        L.append(f"- Pricing basis: {ps.get('source','(source not stated)')}, {ps.get('date','(date not stated)')}")

    # exit-ARR / downsell guard — sits high, before any scenario framing
    if s.get("exit_arr"):
        x = s["exit_arr"]
        if x["flag"]:
            L.append(f"\n> **⚠ EXIT-ARR:** reported ARR {fmt_m(x['reported_arr'],cur)} but final-year run-rate "
                     f"{fmt_m(x['exit_arr'],cur)} — downsell exposure on churn is {fmt_m(x['downsell_exposure'],cur)}.")
        else:
            L.append(f"\n- Exit ARR {fmt_m(x['exit_arr'],cur)} vs reported ARR {fmt_m(x['reported_arr'],cur)} — "
                     "no downsell exposure flagged.")

    L.append("\n## Scenarios (present two)")
    for sc in s["scenarios"]:
        L.append(f"- **{sc['name']}** — {fmt_m(sc['tcv'],cur)} · _{sc['role']}_")
    if s["alternative"]["why"]:
        L.append(f"- Why the alternative is lighter: {s['alternative']['why']}")
    if s["alternative"]["walkaway"]:
        L.append(f"- **Walk-away (internal):** {s['alternative']['walkaway']}")

    L.append("\n## Concession ladder — the Martini "
             + ("✓" if s["shape"]["valid"] else "⚠ shape drifting"))
    L.append("| Stage | Posture | Cum. | Move | Price | Tier | Extract in return |")
    L.append("|---|---|---|---|---|---|---|")
    for r in s["concession_ladder"]:
        L.append(f"| {r['stage']} | {r['posture']} | −{r['cum_discount_pct']}% | "
                 f"−{r['increment_pct']}% | {r['price_fmt']} | {r['tier']} | {r['extract']} |")

    L.append(f"\n## Approval — BAFO −{s['approval']['bafo_discount_pct']}% → "
             f"**{s['approval']['tier_at_bafo']}**"
             + (" · ⚠ EXCEEDS floor" if s['approval']['capped_to_floor'] else ""))

    if s.get("buffer"):
        b = s["buffer"]
        L.append("\n## Buffer — a price hold, not a discount")
        L.append(f"- **Buffer (price hold):** {b['buffer_units']} units @ {fmt_m(b['buffer_price'],cur)} — "
                 "pre-agree the price of growth.")
        L.append(f"- _Travel story:_ at anchor unit economics this growth would have cost "
                 f"{fmt_m(b['ramp_price'],cur)} (saving {fmt_m(b['saving_vs_ramp'],cur)}).")
        L.append("- **Conditions:** " + " · ".join(b["conditions"]))

    dd = s["deal_desk"]
    L.append(f"\n## Deal Desk — {'**REQUIRED**' if dd['required'] else 'not required'}")
    for t in dd["triggers"]:
        L.append(f"- {'🔴' if t['fires'] else '⚪'} {t['label']} — {t['detail']}")
    if dd["required"]:
        L.append("- **Pack:** " + " · ".join(dd["pack"]))
        L.append(f"- Decision: {' / '.join(dd['decision'])} · {dd['cadence']}")

    L.append("\n## Lever ledger — used vs still open")
    ll = s["lever_ledger"]
    L.append(f"_Spend 1→4 before price (5). {ll['used_count']} levers used · {ll['open_count']} still open._\n")
    L.append("| # | Family | Margin | Used (extract) | Still open |")
    L.append("|---|---|---|---|---|")
    for f in ll["families"]:
        used = "; ".join(f["used"]) + (f"  →  _{', '.join(f['extract'])}_" if f["extract"] else "") if f["used"] else "—"
        L.append(f"| {f['n']} | {f['name']} | {f['margin']} | {used} | {', '.join(f['open']) or '—'} |")

    L.append(f"\n## Leverage\n- Switching cost **{s['leverage']['switching_cost']}** → {s['leverage']['posture']}")

    L.append("\n## Why these calls (traced)")
    for r in s["rationale"]:
        L.append(f"- {r}")

    L.append(f"\n## Still on the table (open levers)")
    for o in s["open_levers"]:
        L.append(f"- {o}")

    L.append(f"\n---\n_Generated by `{s['provenance']['generated_by']}` · rules: {s['provenance']['rule_source']} · "
             f"deterministic (trace `{s['provenance']['inputs_hash']}`)_")
    return "\n".join(L)


# ════════════════════════════════════════════════════════════════════
#  SELFTEST  (the canonical Northgate wealth deal (fictional))
# ════════════════════════════════════════════════════════════════════

SAMPLE = {
    "deal": {
        "client": "Northgate Private Bank", "lob": "Wealth & Private Banking", "basis": "AUM",
        "region_list_pct": 100, "term_years": 5, "currency": "£", "eur_per_unit": 1.17,
        "exceptional_metric": "AUM",
        "software_tcv": 13205, "thirdparty_tcv": 1795,
        "lines": [
            {"name": "Digital Banking — Wealth & PB (Signature) · Base Fee", "total": 4081},
            {"name": "Digital Banking — Wealth & PB (Signature) · AUM Fee", "total": 2577},
            {"name": "RM Workspace (Signature) · Base + AUM Fee", "total": 2674},
            {"name": "Digital Onboarding — Private Banking", "total": 1981},
            {"name": "CLO Wealth Management (Premium) · Base + User", "total": 1892},
        ],
    },
    "economics": {"gm_arr_pct": 84, "floor_gm_pct": 70},
    "scenarios": {"good": 6300, "better": 12200, "best": 13900},
    "strategy": {"anchor": "best", "alt": "better", "target_bafo_discount_pct": 13,
                 "why_alt": "Same platform, lighter scope — no dedicated CS or price hold.",
                 "walkaway": "Below £11.0M software, we walk."},
    "levers": {
        "1": {"used": ["Good/Better/Best anchored on Best"], "extract": ["reference rights"]},
        "2": {"used": ["5-yr term"], "extract": ["signed reference"], "open": ["Year-one prepay", "Expansion commit"]},
        "3": {"open": ["Sandbox", "Training credits", "Dedicated CS"]},
        "4": {"open": ["Net 60 payment terms", "Stub bill"]},
        "5": {"used": ["Volume discount to BAFO"], "na": ["VPA / price hold", "Renewal cap"]},
    },
    "context": {"switching_cost": "high", "champion": "validated", "competition": "Avaloq", "budget": "confirmed"},
}


# A second, deliberately SYNTHETIC fixture (fictional client, invented numbers) that
# exercises the ramped/exit-ARR + buffer path and the pass-through metadata.
# Hand arithmetic, written before the engine was run:
#   total_tcv    = 6000 + 0                     = 6000
#   acv          = 6000 / 5                     = 1200.0   (blended, = software here)
#   reported_arr = software 6000 / 5            = 1200.0   (SOFTWARE basis — the ramp's basis)
#   ramp sum     = 400+900+1400+1650+1650       = 6000     (consistent with software_tcv)
#   exit_arr     = fee at highest year key "5"  = 1650
#   flag         = 1650 > 1200                  = True
#   headroom     = (85-70)/(100-70)             = 50.0%
#   ladder       = 0/0.6/0.9/1.0 × 10           = 0 / 6.0 / 9.0 / 10.0
#   unit price   = 6000 / 300 commit units      = 20.0
#   ramp_price   = 100 buffer units × 20.0      = 2000.0
#   saving       = 2000.0 − 1500                = 500.0
RAMPED_SAMPLE = {
    "deal": {
        "client": "Northwind Mutual (fictional)", "lob": "Retail", "basis": "unit",
        "region_list_pct": 100, "term_years": 5, "currency": "€", "eur_per_unit": 1.0,
        "deal_type": "renewal", "round": 2,
        "pricing_source": {"source": "Synthetic price list (fixture)", "date": "2026-01-01"},
        "software_tcv": 6000, "thirdparty_tcv": 0,
        "ramp_schedule": {"1": 400, "2": 900, "3": 1400, "4": 1650, "5": 1650},
    },
    "economics": {"gm_arr_pct": 85, "floor_gm_pct": 70},
    "strategy": {"anchor": "best", "alt": "better", "target_bafo_discount_pct": 10,
                 "buffer_offer": {"commit_units": 300, "buffer_units": 100, "buffer_price": 1500}},
    "context": {"switching_cost": "medium"},
}


# A minimal SYNTHETIC new-logo fixture that sits either side of the €600K Deal Desk
# threshold in a NON-euro currency — the boundary the trigger has to convert for.
# Hand arithmetic, written before the engine was run:
#   total_tcv    = 550 + 0                      = 550   (£k)
#   in EUR       = 550 × 1.17                   = 643.5 ≥ 600  → trigger does NOT fire
#   at 500 £k    = 500 × 1.17                   = 585.0 <  600  → trigger fires
NEW_LOGO_SAMPLE = {
    "deal": {
        "client": "Fictional new-logo bank", "lob": "Retail", "basis": "unit",
        "region_list_pct": 100, "term_years": 5, "currency": "£", "eur_per_unit": 1.17,
        "new_logo": True, "software_tcv": 550, "thirdparty_tcv": 0,
    },
    "economics": {},
    "strategy": {"anchor": "best", "alt": "better", "target_bafo_discount_pct": 0},
    "context": {"switching_cost": "medium"},
}


def selftest():
    s1 = build_strategy(SAMPLE)
    s2 = build_strategy(json.loads(json.dumps(SAMPLE)))
    j1, j2 = json.dumps(s1, sort_keys=True), json.dumps(s2, sort_keys=True)
    assert j1 == j2, "NON-DETERMINISTIC: identical input produced different output"

    e = s1["economics"]
    assert e["total_tcv"] == 15000, e["total_tcv"]
    assert e["acv"] == 3000.0, e["acv"]
    assert e["deal_size_band"] == "large", e["deal_size_band"]
    # (84-70)/(100-70)=46.7
    assert e["max_discount_to_floor_pct"] == 46.7, e["max_discount_to_floor_pct"]
    assert e["headroom_band"] == "ample"
    # ladder: Martini 0/0.6/0.9/1.0 × 13 = 0/7.8/11.7/13
    cum = [r["cum_discount_pct"] for r in s1["concession_ladder"]]
    assert cum == [0.0, 7.8, 11.7, 13.0], cum
    incs = [r["increment_pct"] for r in s1["concession_ladder"]]
    assert incs[1] >= incs[2] >= incs[3], incs            # shrinking = Martini
    assert s1["shape"]["valid"] is True
    assert s1["approval"]["tier_at_bafo"] == "SVP", s1["approval"]["tier_at_bafo"]  # 13% ≤ 20
    # deal desk: AUM metric + ACV>€2M fire; GM healthy
    assert s1["deal_desk"]["required"] is True
    fired = {t["label"] for t in s1["deal_desk"]["triggers"] if t["fires"]}
    assert "Exceptional pricing metric (AUM)" in fired
    assert "ARR ACV > €2M" in fired
    assert "GM ARR < 83%" not in fired
    # approval ladder DISPLAY — the Deal Desk lower bound is the CRO cap read off
    # the band table, not a multiple of the SVP cap (100 list: 20/40 → "> 40%").
    assert [r["rng"] for r in s1["approval"]["ladder"]] == ["0%", "≤ 20%", "≤ 40%", "> 40%"], \
        s1["approval"]["ladder"]
    # …and on the 70% price list the caps are 40/60, so Deal Desk starts above 60%.
    s70 = build_strategy({**SAMPLE, "deal": {**SAMPLE["deal"], "region_list_pct": 70}})
    assert [r["rng"] for r in s70["approval"]["ladder"]] == ["0%", "≤ 40%", "≤ 60%", "> 60%"], \
        s70["approval"]["ladder"]

    # lever ledger has open levers (explainability)
    assert s1["lever_ledger"]["open_count"] > 0
    # open_levers is ONE ENTRY PER LEVER — "Family N (Name): Lever", never a
    # comma-joined per-family grouping (the deal-state round diff counts levers).
    assert len(s1["open_levers"]) == s1["lever_ledger"]["open_count"], s1["open_levers"]
    assert len(s1["open_levers"]) == sum(len(f["open"]) for f in s1["lever_ledger"]["families"])
    for entry in s1["open_levers"]:
        m = re.match(r"^Family \d+ \([^)]+\): (.+)$", entry)
        assert m, f"malformed open lever entry: {entry!r}"
        assert "," not in m.group(1), f"grouped, not one lever per entry: {entry!r}"

    # determinism trace stable
    assert s1["provenance"]["inputs_hash"] == s2["provenance"]["inputs_hash"]

    # ── BACKWARD COMPAT: a config without the new fields adds no new keys ──
    for k in ("exit_arr", "buffer", "deal_type", "round", "pricing_source"):
        assert k not in s1, f"backward-compat broken: {k} emitted for a config that never asked for it"
    render_brief(s1)                                       # brief still renders

    # ── ramped / buffer fixture (new blocks) ─────────────────────────
    r1 = build_strategy(RAMPED_SAMPLE)
    r2 = build_strategy(json.loads(json.dumps(RAMPED_SAMPLE)))
    assert json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True), \
        "NON-DETERMINISTIC: identical ramped input produced different output"

    # pass-through metadata (engine does no math with these)
    assert r1["deal_type"] == "renewal", r1["deal_type"]
    assert r1["round"] == 2, r1["round"]
    assert r1["pricing_source"]["date"] == "2026-01-01", r1["pricing_source"]

    # exit-ARR guard — hand math above: 6000/5 = 1200.0 reported vs 1650 exit
    re_ = r1["economics"]
    assert re_["total_tcv"] == 6000, re_["total_tcv"]
    assert re_["acv"] == 1200.0, re_["acv"]
    x = r1["exit_arr"]
    assert x["reported_arr"] == 1200.0, x["reported_arr"]
    assert x["exit_arr"] == 1650, x["exit_arr"]            # final-year fee, highest year key
    assert x["downsell_exposure"] == 1650, x["downsell_exposure"]
    assert x["flag"] is True, x["flag"]                    # 1650 > 1200 → exposure understated

    # buffer play — hand math above: 6000/300 = 20.0/unit; 100 × 20.0 = 2000.0; −1500 = 500.0
    b = r1["buffer"]
    assert b["ramp_price"] == 2000.0, b["ramp_price"]
    assert b["buffer_price"] == 1500, b["buffer_price"]
    assert b["saving_vs_ramp"] == 500.0, b["saving_vs_ramp"]
    assert b["conditions"] == BUFFER_CONDITIONS, b["conditions"]

    # the buffer is a PRICE HOLD — the word "discount" never describes it
    rb = render_brief(r1)
    assert "⚠ EXIT-ARR:" in rb, "exit-ARR warning missing from brief"
    assert "price hold, not a discount" in rb
    assert "Pricing basis: Synthetic price list (fixture), 2026-01-01" in rb
    assert re_["max_discount_to_floor_pct"] == 50.0, re_["max_discount_to_floor_pct"]

    # ── exit-ARR is a LIKE-FOR-LIKE (software) comparison ─────────────
    # Same fixture + €3.0M of third-party revenue. Hand math, written first:
    #   total_tcv    = 6000 + 3000              = 9000
    #   economics.acv= 9000 / 5                 = 1800.0   (blended — unchanged)
    #   reported_arr = software 6000 / 5        = 1200.0   (software basis)
    #   flag         = 1650 > 1200              = True
    # On the blended basis this would read 1650 > 1800 = False — third-party
    # revenue suppressing a real downsell exposure.
    mixed = json.loads(json.dumps(RAMPED_SAMPLE))
    mixed["deal"]["thirdparty_tcv"] = 3000
    m1 = build_strategy(mixed)
    assert m1["economics"]["total_tcv"] == 9000, m1["economics"]["total_tcv"]
    assert m1["economics"]["acv"] == 1800.0, m1["economics"]["acv"]      # blended ACV unchanged
    assert m1["exit_arr"]["reported_arr"] == 1200.0, m1["exit_arr"]["reported_arr"]
    assert m1["exit_arr"]["flag"] is True, m1["exit_arr"]                # not suppressed

    # ── new-logo trigger converts to EUR before the €600K test ────────
    # Hand math above: £550k × 1.17 = €643.5k ≥ 600 → no trigger;
    #                  £500k × 1.17 = €585.0k <  600 → trigger.
    above = build_strategy(NEW_LOGO_SAMPLE)
    assert not any(t["label"] == "New logo < €600K" for t in above["deal_desk"]["triggers"]), \
        "£550k (≈€643.5k) fired the €600K trigger — currency not converted"
    assert above["deal_desk"]["required"] is False, above["deal_desk"]["triggers"]
    below_cfg = json.loads(json.dumps(NEW_LOGO_SAMPLE))
    below_cfg["deal"]["software_tcv"] = 500
    below = build_strategy(below_cfg)
    nl = [t for t in below["deal_desk"]["triggers"] if t["label"] == "New logo < €600K"]
    assert nl and nl[0]["fires"] is True, below["deal_desk"]["triggers"]
    assert "€0.6M" in nl[0]["detail"], nl[0]["detail"]                   # EUR figure shown
    assert below["deal_desk"]["required"] is True

    # ── money inputs are never defaulted (Gate 8 hard stop) ───────────
    for field in ("currency", "region_list_pct", "term_years"):
        stripped = json.loads(json.dumps(SAMPLE))
        stripped["deal"].pop(field)
        try:
            build_strategy(stripped)
        except SystemExit as exc:
            assert field in str(exc), str(exc)
        else:
            raise AssertionError(f"missing '{field}' was silently defaulted instead of refused")

    print("✓ selftest passed — deterministic, rules verified")
    print(f"  TCV {fmt_m(e['total_tcv'])} · ACV {fmt_m(e['acv'])} · headroom {e['max_discount_to_floor_pct']}% "
          f"· BAFO tier {s1['approval']['tier_at_bafo']} · Deal Desk {'required' if s1['deal_desk']['required'] else 'no'} "
          f"· {s1['lever_ledger']['open_count']} levers open · trace {s1['provenance']['inputs_hash']}")
    print(f"  ramped fixture: reported ARR {fmt_m(x['reported_arr'],'€')} vs exit ARR {fmt_m(x['exit_arr'],'€')} "
          f"(flag {x['flag']}) · buffer hold {fmt_m(b['buffer_price'],'€')} vs ramp {fmt_m(b['ramp_price'],'€')} "
          f"(saving {fmt_m(b['saving_vs_ramp'],'€')}) · backward-compat OK")
    return s1


SCHEMA = """
Config schema (JSON):
{
  "deal": {
    "client", "lob", "basis" (AUM|unit|conversational),
    "region_list_pct" (100|70)  REQUIRED,   # no default — hard stop if absent
    "term_years"                REQUIRED,   # no default — hard stop if absent
    "currency"                  REQUIRED,   # no default — hard stop if absent
    "eur_per_unit"?,                        # optional; defaults 1.0 for € else 1.17
    "exceptional_metric" (e.g. "AUM" | null),
    "new_logo" (bool), "custom_dev" (bool),
    "software_tcv", "thirdparty_tcv",         # £k; software_tcv falls back to sum(lines.total)
    "lines": [ {"name", "total", "years":[...]} ],

    # ── all optional; omit them and the output is byte-identical to before ──
    "deal_type"?: "new_logo" | "renewal" | "expansion",   # pass-through, no math
    "round"?: int (default 1 when deal_type is given),    # negotiation round, pass-through
    "pricing_source"?: {"source", "date"},                # provenance line in the brief
    "ramp_schedule"?: {"<year>": fee}                     # SOFTWARE annual fee per contract
                                                          # year (£k; str|int keys), i.e. the
                                                          # same basis as software_tcv —
                                                          # third-party is NOT in here
                                                          # → triggers the exit_arr block
  },
  "economics": { "gm_arr_pct", "floor_gm_pct",   # → floor headroom
                 "managed_hosting_gm_pct"?, "managed_services_gm_pct"?,
                 "professional_services_gm_pct"?, "first_year_arr_pct"? },
  "scenarios": { "good", "better", "best", "<id>_name"? },     # £k TCV
  "strategy": { "anchor", "alt", "target_bafo_discount_pct", "why_alt", "walkaway",
                "buffer_offer"?: {"commit_units", "buffer_units", "buffer_price"}
                                       # optional → triggers the buffer (price-hold) block },
  "levers": { "1".."5": { "used":[], "extract":[], "open":[], "na":[] } },
  "context": { "switching_cost" (high|medium|low), "champion", "competition", "budget" }
}

Optional output blocks (emitted only when their config field is supplied):
  "deal_type" / "round" / "pricing_source"   pass-through metadata
  "exit_arr": { "reported_arr",              # = software_tcv / term — SOFTWARE basis, the
                                             #   like-for-like comparator for the ramp (NOT the
                                             #   blended economics.acv, which includes 3rd-party)
                "exit_arr",                  # = final-year fee in ramp_schedule
                "downsell_exposure",         # = exit_arr — what churn actually costs
                "flag" }                     # true when exit_arr > reported_arr
  "buffer":   { "ramp_price",                # = buffer_units × (software_tcv / commit_units)
                "buffer_price", "saving_vs_ramp", "conditions"[],
                "commit_units", "buffer_units" }
                # a PRICE HOLD on future growth — never described as a discount

Output: strategy JSON (--json) + markdown strategy brief (--out / stdout).
"""


def main():
    ap = argparse.ArgumentParser(description="Proposal Builder — deterministic deal-strategy engine")
    ap.add_argument("--config")
    ap.add_argument("--json", help="write strategy JSON here")
    ap.add_argument("--out", help="write markdown brief here (else stdout)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--print-schema", action="store_true")
    a = ap.parse_args()

    if a.print_schema:
        print(SCHEMA); return
    if a.selftest:
        selftest(); return
    if not a.config:
        ap.error("provide --config, --selftest, or --print-schema")

    cfg = json.loads(Path(a.config).read_text())
    s = build_strategy(cfg)
    if a.json:
        Path(a.json).write_text(json.dumps(s, indent=2))
    brief = render_brief(s)
    if a.out:
        Path(a.out).write_text(brief)
        print(f"✓ brief → {a.out}" + (f" · json → {a.json}" if a.json else ""))
    else:
        print(brief)


if __name__ == "__main__":
    main()
