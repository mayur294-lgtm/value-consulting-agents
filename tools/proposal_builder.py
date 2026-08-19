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
via /frontline-long-form using the JSON.

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


# ════════════════════════════════════════════════════════════════════
#  ENGINE
# ════════════════════════════════════════════════════════════════════

def build_strategy(cfg):
    deal = cfg["deal"]
    cur = deal.get("currency", "£")
    list_pct = deal.get("region_list_pct", 100)
    term = deal.get("term_years", 5)
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

    approval = {
        "bafo_discount_pct": target,
        "tier_at_bafo": approval_tier(target, list_pct),
        "capped_to_floor": capped,
        "svp_cap_pct": svp_cap(list_pct),
        "ladder": [{"who": w, "rng": r} for w, r in
                   [("List", "0%")] + [(n, f"≤ {h}%" if h < 1000 else f"> {svp_cap(list_pct)*2}%")
                                        for n, h in TIER_BANDS.get(int(list_pct), TIER_BANDS[100])[1:]]],
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
    if deal.get("new_logo") and total < 600:
        trg("New logo < €600K", True, f"{fmt_m(total, cur)} TCV")
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
    open_levers = [f"Family {f['n']} ({f['name']}): {', '.join(f['open'])}"
                   for f in families if f["open"]]

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

    cfg_hash = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:8]

    return {
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
    # lever ledger has open levers (explainability)
    assert s1["lever_ledger"]["open_count"] > 0
    assert len(s1["open_levers"]) > 0
    # determinism trace stable
    assert s1["provenance"]["inputs_hash"] == s2["provenance"]["inputs_hash"]

    print("✓ selftest passed — deterministic, rules verified")
    print(f"  TCV {fmt_m(e['total_tcv'])} · ACV {fmt_m(e['acv'])} · headroom {e['max_discount_to_floor_pct']}% "
          f"· BAFO tier {s1['approval']['tier_at_bafo']} · Deal Desk {'required' if s1['deal_desk']['required'] else 'no'} "
          f"· {s1['lever_ledger']['open_count']} levers open · trace {s1['provenance']['inputs_hash']}")
    return s1


SCHEMA = """
Config schema (JSON):
{
  "deal": {
    "client", "lob", "basis" (AUM|unit|conversational), "region_list_pct" (100|70),
    "term_years", "currency", "eur_per_unit", "exceptional_metric" (e.g. "AUM" | null),
    "new_logo" (bool), "custom_dev" (bool),
    "software_tcv", "thirdparty_tcv",         # £k; software_tcv falls back to sum(lines.total)
    "lines": [ {"name", "total", "years":[...]} ]
  },
  "economics": { "gm_arr_pct", "floor_gm_pct",   # → floor headroom
                 "managed_hosting_gm_pct"?, "managed_services_gm_pct"?,
                 "professional_services_gm_pct"?, "first_year_arr_pct"? },
  "scenarios": { "good", "better", "best", "<id>_name"? },     # £k TCV
  "strategy": { "anchor", "alt", "target_bafo_discount_pct", "why_alt", "walkaway" },
  "levers": { "1".."5": { "used":[], "extract":[], "open":[], "na":[] } },
  "context": { "switching_cost" (high|medium|low), "champion", "competition", "budget" }
}
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
