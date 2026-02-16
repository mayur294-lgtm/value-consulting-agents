#!/usr/bin/env python3
"""
ROI Calibrator — Stage 1 & 2

Assesses a generated ROI config against knowledge-base benchmarks,
identifies expansion opportunities, and (Stage 2) can auto-apply
approved expansions and regenerate the Excel model.

Usage (Stage 1 — assessment only):
    python roi_calibrator.py --config roi_config.json

Usage (Stage 2 — apply expansions + regenerate):
    python roi_calibrator.py --config roi_config.json --apply --output roi_model.xlsx
"""

import json
import copy
import argparse
import math
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────────────────────────
# BENCHMARK DATA (from knowledge/domains/roi_examples.md)
# ─────────────────────────────────────────────────────────────────────

SEGMENT_BENCHMARKS = {
    "Retail Banking": {
        "roi_range": (60, 150),
        "payback_range": (1.5, 2.5),
        "typical_yoy": 0.08,
        "impl_curve_moderate": [0.30, 0.70, 0.80, 1.00, 1.00],
        "eff_curve_moderate": [0.15, 0.35, 0.60, 0.85, 1.00],
        "standard_levers": [
            "Customer Acquisition / Onboarding",
            "Loan / Product Origination",
            "Customer Servicing",
            "Loyalty & Retention",
            "IT Cost Savings",
        ],
    },
    "Wealth Management": {
        "roi_range": (120, 200),
        "payback_range": (1.5, 2.0),
        "typical_yoy": 0.10,
        "impl_curve_moderate": [0.20, 0.70, 0.80, 1.00, 1.00],
        "eff_curve_moderate": [0.15, 0.35, 0.60, 0.85, 1.00],
        "standard_levers": [
            "Customer Acquisition / Onboarding",
            "RM Productivity / Prospecting",
            "Customer Servicing",
            "Loyalty & Retention",
            "Retail-to-Wealth Conversion",
        ],
    },
    "Commercial Banking": {
        "roi_range": (80, 140),
        "payback_range": (2.0, 3.0),
        "typical_yoy": 0.08,
        "impl_curve_moderate": [0.25, 0.60, 0.80, 1.00, 1.00],
        "eff_curve_moderate": [0.15, 0.35, 0.60, 0.85, 1.00],
        "standard_levers": [
            "Customer Acquisition / Onboarding",
            "Loan / Product Origination",
            "Customer Servicing",
            "Cash Management",
            "IT Cost Savings",
        ],
    },
    "SME Banking": {
        "roi_range": (70, 130),
        "payback_range": (2.0, 2.5),
        "typical_yoy": 0.08,
        "impl_curve_moderate": [0.25, 0.60, 0.80, 1.00, 1.00],
        "eff_curve_moderate": [0.15, 0.35, 0.60, 0.85, 1.00],
        "standard_levers": [
            "Customer Acquisition / Onboarding",
            "Loan / Product Origination",
            "Customer Servicing",
            "Self-Service Migration",
            "IT Cost Savings",
        ],
    },
    "Corporate Banking": {
        "roi_range": (60, 100),
        "payback_range": (2.5, 3.5),
        "typical_yoy": 0.06,
        "impl_curve_moderate": [0.20, 0.55, 0.75, 0.95, 1.00],
        "eff_curve_moderate": [0.10, 0.30, 0.55, 0.80, 1.00],
        "standard_levers": [
            "Customer Acquisition / Onboarding",
            "Cash Management",
            "Trade Finance",
            "Customer Servicing",
            "IT Cost Savings",
        ],
    },
}

# Multi-role multipliers for servicing tasks (RM + RM Assistant + Back Office)
MULTI_ROLE_MULTIPLIERS = {
    "portfolio_report_generation": 1.75,
    "cross_subsidiary_data_consolidation": 1.75,
    "quarterly_performance_review": 1.83,
    "market_updates": 1.0,
    "client_service_requests": 2.06,
    "document_collection": 2.0,
    "meeting_scheduling": 2.0,
    "inter_subsidiary_referral": 1.67,
    "kyc_aml_reviews": 1.75,
    "transaction_processing": 2.19,
    "regulatory_reporting": 1.50,
}


# ─────────────────────────────────────────────────────────────────────
# PROPOSAL DATA CLASSES
# ─────────────────────────────────────────────────────────────────────

class ExpansionProposal:
    """A single expansion proposal with estimated impact."""

    CATEGORIES = [
        "new_journey",
        "curve_calibration",
        "reframe_benefit",
        "multi_role_servicing",
        "missing_lever",
        "investment_calibration",
    ]

    def __init__(
        self,
        lever_name: str,
        category: str,
        estimated_annual_impact: float,
        justification: str,
        confidence: str = "MEDIUM",
        benchmark_source: str = "",
        data_inputs_needed: list = None,
        config_patch: dict = None,
    ):
        self.lever_name = lever_name
        self.category = category
        self.estimated_annual_impact = estimated_annual_impact
        self.justification = justification
        self.confidence = confidence
        self.benchmark_source = benchmark_source
        self.data_inputs_needed = data_inputs_needed or []
        self.config_patch = config_patch or {}

    def to_dict(self):
        return {
            "lever_name": self.lever_name,
            "category": self.category,
            "estimated_annual_impact": self.estimated_annual_impact,
            "justification": self.justification,
            "confidence": self.confidence,
            "benchmark_source": self.benchmark_source,
            "data_inputs_needed": self.data_inputs_needed,
        }


# ─────────────────────────────────────────────────────────────────────
# ROI CALCULATOR (quick Python-side computation)
# ─────────────────────────────────────────────────────────────────────

def compute_roi_metrics(config: dict) -> dict:
    """Compute ROI, NPV, IRR, payback from a config dict."""
    impl = config.get("backbase_loading", {}).get("implementation_curve", [0.3, 0.7, 0.8, 1.0, 1.0])
    eff = config.get("backbase_loading", {}).get("effectiveness_curve", [0.15, 0.35, 0.6, 0.85, 1.0])
    yoy = config.get("backbase_loading", {}).get("yoy_growth", [0.08] * 5)
    discount = config.get("discount_rate", 0.10)

    journeys = config.get("journeys", {})
    total_steady = 0
    for j in journeys.values():
        total_steady += j.get("totals", {}).get("journey_total", 0)

    investment = config.get("investment", {})
    license_d = investment.get("license", {})
    impl_d = investment.get("implementation", {})

    yearly_inflows = []
    yearly_outflows = []
    yearly_net = []
    for yr in range(5):
        inflow = total_steady * impl[yr] * eff[yr] * (1 + yoy[yr])
        lic = license_d.get(f"year_{yr+1}", 0)
        imp = impl_d.get(f"year_{yr+1}", 0)
        outflow = lic + imp
        yearly_inflows.append(inflow)
        yearly_outflows.append(outflow)
        yearly_net.append(inflow - outflow)

    total_benefits = sum(yearly_inflows)
    total_investment = sum(yearly_outflows)
    net_benefit = total_benefits - total_investment
    roi = (net_benefit / total_investment * 100) if total_investment else 0

    # NPV
    npv = sum(cf / (1 + discount) ** (yr + 1) for yr, cf in enumerate(yearly_net))

    # IRR (Newton's method)
    irr = _compute_irr(yearly_net)

    # Payback
    cumulative = 0
    payback = "N/A"
    for yr in range(5):
        prev = cumulative
        cumulative += yearly_net[yr]
        if cumulative >= 0 and prev < 0:
            frac = -prev / yearly_net[yr] if yearly_net[yr] != 0 else 0
            payback = round(yr + frac, 1)
            break
        elif cumulative >= 0 and yr == 0:
            payback = 1.0
            break

    return {
        "total_steady_state": total_steady,
        "total_benefits_5yr": round(total_benefits),
        "total_investment_5yr": round(total_investment),
        "net_benefit": round(net_benefit),
        "roi_percent": round(roi, 1),
        "npv": round(npv),
        "irr": irr,
        "payback_years": payback,
        "yearly_inflows": [round(x) for x in yearly_inflows],
        "yearly_outflows": [round(x) for x in yearly_outflows],
        "yearly_net": [round(x) for x in yearly_net],
    }


def _compute_irr(cashflows, guess=0.1, max_iter=100, tol=1e-6):
    """Newton-Raphson IRR."""
    rate = guess
    for _ in range(max_iter):
        npv = sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))
        dnpv = sum(-t * cf / (1 + rate) ** (t + 1) for t, cf in enumerate(cashflows))
        if abs(dnpv) < 1e-12:
            break
        rate -= npv / dnpv
        if abs(npv) < tol:
            break
    if math.isnan(rate) or math.isinf(rate) or rate < -1:
        return None
    return round(rate * 100, 1)


# ─────────────────────────────────────────────────────────────────────
# STAGE 1: ASSESSMENT & PROPOSAL GENERATION
# ─────────────────────────────────────────────────────────────────────

class ROICalibrator:
    """Assesses ROI config and generates expansion proposals."""

    def __init__(self, config: dict):
        self.config = config
        self.segment = self._detect_segment()
        self.benchmark = SEGMENT_BENCHMARKS.get(self.segment, SEGMENT_BENCHMARKS["Retail Banking"])
        self.metrics = compute_roi_metrics(config)
        self.proposals: list[ExpansionProposal] = []

    def _detect_segment(self) -> str:
        industry = self.config.get("industry", "").lower()
        if "wealth" in industry:
            return "Wealth Management"
        if "commercial" in industry:
            return "Commercial Banking"
        if "sme" in industry:
            return "SME Banking"
        if "corporate" in industry:
            return "Corporate Banking"
        return "Retail Banking"

    def assess(self) -> dict:
        """Run full assessment and return structured report."""
        roi = self.metrics["roi_percent"]
        low, high = self.benchmark["roi_range"]

        assessment = {
            "segment": self.segment,
            "current_roi": roi,
            "expected_range": f"{low}-{high}%",
            "status": "WITHIN_RANGE" if low <= roi <= high else ("BELOW_RANGE" if roi < low else "ABOVE_RANGE"),
            "gap_to_lower_bound": max(0, low - roi),
            "metrics": self.metrics,
        }

        if roi < low:
            self._check_retail_to_segment_conversion()
            self._check_multi_role_servicing()
            self._check_curve_calibration()
            self._check_investment_calibration()
            self._check_cost_avoidance_reframing()
            self._check_missing_standard_levers()

            # Sort by impact descending
            self.proposals.sort(key=lambda p: p.estimated_annual_impact, reverse=True)

        assessment["proposals"] = [p.to_dict() for p in self.proposals]
        assessment["projected_roi_with_all"] = self._projected_roi_all()
        return assessment

    def _projected_roi_all(self) -> float:
        """Estimate ROI if all proposals are applied."""
        extra_steady = sum(p.estimated_annual_impact for p in self.proposals
                          if p.category != "curve_calibration" and p.category != "investment_calibration")
        config_copy = copy.deepcopy(self.config)

        # Apply curve calibration if proposed
        for p in self.proposals:
            if p.category == "curve_calibration" and p.config_patch:
                bl = config_copy.get("backbase_loading", {})
                bl.update(p.config_patch.get("backbase_loading", {}))
                config_copy["backbase_loading"] = bl
            if p.category == "investment_calibration" and p.config_patch:
                config_copy["investment"] = p.config_patch.get("investment", config_copy["investment"])

        # Add extra steady state to a dummy journey
        current_steady = self.metrics["total_steady_state"]
        new_steady = current_steady + extra_steady

        # Recompute with new steady state
        impl = config_copy.get("backbase_loading", {}).get("implementation_curve", [0.3, 0.7, 0.8, 1.0, 1.0])
        eff = config_copy.get("backbase_loading", {}).get("effectiveness_curve", [0.15, 0.35, 0.6, 0.85, 1.0])
        yoy = config_copy.get("backbase_loading", {}).get("yoy_growth", [0.08] * 5)

        inv = config_copy.get("investment", {})
        lic_d = inv.get("license", {})
        imp_d = inv.get("implementation", {})

        total_ben = sum(new_steady * impl[yr] * eff[yr] * (1 + yoy[yr]) for yr in range(5))
        total_inv = sum(lic_d.get(f"year_{yr+1}", 0) + imp_d.get(f"year_{yr+1}", 0) for yr in range(5))
        if total_inv == 0:
            return 0
        return round((total_ben - total_inv) / total_inv * 100, 1)

    # ── Checkers ──────────────────────────────────────────────────

    def _check_retail_to_segment_conversion(self):
        """Check if retail-to-wealth/SME/commercial conversion is missing."""
        bp = self.config.get("bank_profile", {})
        ac = bp.get("additional_context", {})

        # Need a large retail base to convert from
        total_employees = ac.get("total_employees_bankwide", {})
        retail_customers = ac.get("retail_customer_count", {})
        total_deposits = ac.get("total_deposits", {})

        # Check if a conversion journey already exists
        journeys = self.config.get("journeys", {})
        has_conversion = any(
            "conversion" in j.get("journey_name", "").lower() or
            "retail" in j.get("journey_name", "").lower() or
            "upgrade" in j.get("journey_name", "").lower()
            for j in journeys.values()
        )
        if has_conversion:
            return

        # For wealth: check if bank has retail customers to convert
        if self.segment == "Wealth Management":
            # Try to find retail customer count from various sources
            retail_count = None
            rc_entry = ac.get("retail_customer_count", {})
            if isinstance(rc_entry, dict) and rc_entry.get("value"):
                retail_count = rc_entry["value"]

            # Fallback: check basic_information for bank-wide customer count
            bi = bp.get("basic_information", {})
            wealth_customers_entry = bi.get("total_customers", {})
            wealth_customers = wealth_customers_entry.get("value", 0) if isinstance(wealth_customers_entry, dict) else 0

            # Check for eligible unconverted
            eligible_entry = ac.get("wealth_eligible_unconverted", {})
            eligible = eligible_entry.get("value", 0) if isinstance(eligible_entry, dict) else 0

            # Check total deposits as proxy for large retail base
            deposits_entry = ac.get("total_deposits", {})
            deposits = deposits_entry.get("value", 0) if isinstance(deposits_entry, dict) else 0

            # If we have deposits > $1B, bank likely has large retail base
            if (deposits and deposits > 1_000_000_000 and wealth_customers) or retail_count:
                # Estimate retail base from deposits (typical wealth is 5-15% of total customer base)
                estimated_retail = max(wealth_customers * 10, 100_000)

                # Check if we have explicit data — always prefer it
                if retail_count:
                    estimated_retail = retail_count

                # Use bank-specific eligible threshold if available
                eligible_pct = 0.12  # 12% of retail eligible for wealth
                adoption_rate = 0.15  # 15% annual adoption
                eligible_pool = int(estimated_retail * eligible_pct)
                new_clients_yr = int(eligible_pool * adoption_rate)

                # Revenue: new digital converts are minimum-threshold clients
                # They generate ~5-7% of average wealth client revenue (just crossed threshold)
                basic = self.config.get("basic_information", {})
                rev_per_client = basic.get("average_revenue_per_customer", 946)
                new_client_rev_factor = 0.05  # New converts at entry-level, ~5% of avg
                rev_per_new_client = rev_per_client * new_client_rev_factor

                # AUM fees + product revenue for new digital converts
                revenue_annual = new_clients_yr * rev_per_new_client

                # Cost avoidance: RMs not hired (digital clients use higher ratio)
                digital_clients_per_rm = 400  # Digital self-service = higher RM ratio
                rms_avoided = new_clients_yr / digital_clients_per_rm

                # RM annual cost
                staff_costs_bw = ac.get("staff_costs_bankwide", {})
                staff_costs = staff_costs_bw.get("value", 0) if isinstance(staff_costs_bw, dict) else 0
                employees_bw = ac.get("total_employees_bankwide", {})
                employees = employees_bw.get("value", 0) if isinstance(employees_bw, dict) else 0

                if staff_costs and employees:
                    avg_cost_per_fte = staff_costs / employees
                    rm_cost = avg_cost_per_fte * 1.5  # RMs cost ~1.5x average
                else:
                    rm_cost = 14000  # fallback

                cost_avoidance = rms_avoided * rm_cost

                total_annual = revenue_annual + cost_avoidance

                if total_annual > 100_000:
                    self.proposals.append(ExpansionProposal(
                        lever_name="Retail-to-Wealth Digital Conversion Pipeline",
                        category="new_journey",
                        estimated_annual_impact=round(total_annual),
                        justification=(
                            f"Bank has large retail base ({estimated_retail:,} customers) with "
                            f"{eligible_pool:,} eligible for wealth ({eligible_pct*100:.0f}%). "
                            f"At {adoption_rate*100:.0f}% annual adoption = {new_clients_yr:,} new digital wealth "
                            f"clients/yr. Revenue: ${revenue_annual:,.0f}/yr (entry-level clients at "
                            f"${rev_per_new_client:,.0f}/client = {new_client_rev_factor*100:.0f}% of avg). "
                            f"Cost avoidance: ${cost_avoidance:,.0f}/yr ({rms_avoided:.0f} RMs not hired at "
                            f"${rm_cost:,.0f}/yr, {digital_clients_per_rm}:1 digital ratio). "
                            f"Benchmarked from HNB V12 Lever 4."
                        ),
                        confidence="MEDIUM",
                        benchmark_source="HNB V12 Lever 4, Seabank CLO lever",
                        data_inputs_needed=["retail_customer_count", "eligibility_threshold", "rm_annual_cost"],
                        config_patch={
                            "_new_journey_key": "retail_to_wealth_conversion",
                            "_estimated_retail": estimated_retail,
                            "_eligible_pool": eligible_pool,
                            "_adoption_rate": adoption_rate,
                            "_new_clients_yr": new_clients_yr,
                            "_revenue_annual": revenue_annual,
                            "_cost_avoidance": cost_avoidance,
                            "_rms_avoided": rms_avoided,
                            "_rm_cost": rm_cost,
                            "_rev_per_client": rev_per_client,
                            "_rev_per_new_client": rev_per_new_client,
                            "_new_client_rev_factor": new_client_rev_factor,
                            "_digital_clients_per_rm": digital_clients_per_rm,
                        },
                    ))

    def _check_multi_role_servicing(self):
        """Check if servicing uses single role vs multi-role."""
        journeys = self.config.get("journeys", {})
        for j_key, journey in journeys.items():
            sa = journey.get("servicing_analysis", {})
            if not sa:
                continue

            # Check if tasks have only a single FTE rate (single role)
            all_tasks = []
            for channel in sa.values():
                if isinstance(channel, dict) and "tasks" in channel:
                    all_tasks.extend(channel["tasks"])

            if not all_tasks:
                continue

            # If all tasks have same rate, it's single-role
            rates = set(t.get("fte_rate", 0) for t in all_tasks)
            if len(rates) <= 1:
                # Calculate current servicing total
                current_total = journey.get("totals", {}).get("total_cost_saved", 0)
                if current_total == 0:
                    continue

                # Estimate multi-role uplift (average multiplier ~1.8x)
                avg_multiplier = sum(MULTI_ROLE_MULTIPLIERS.values()) / len(MULTI_ROLE_MULTIPLIERS)
                new_total = current_total * avg_multiplier
                uplift = new_total - current_total

                if uplift > 10_000:
                    self.proposals.append(ExpansionProposal(
                        lever_name="Multi-Role Servicing (RM + Assistant + Back Office)",
                        category="multi_role_servicing",
                        estimated_annual_impact=round(uplift),
                        justification=(
                            f"Current servicing uses single blended FTE rate (${rates.pop():.2f}/hr). "
                            f"Real-world tasks involve RM + RM Assistant + Back Office roles. "
                            f"Adding multi-role time (avg {avg_multiplier:.1f}x multiplier) increases "
                            f"servicing benefit from ${current_total:,.0f} to ${new_total:,.0f}."
                        ),
                        confidence="MEDIUM",
                        benchmark_source="HNB V12 Lever 5 (multi-role servicing)",
                        data_inputs_needed=["rm_assistant_count", "back_office_staff_count"],
                        config_patch={
                            "_servicing_journey_key": j_key,
                            "_multipliers": MULTI_ROLE_MULTIPLIERS,
                        },
                    ))
                break  # Only one servicing journey

    def _check_curve_calibration(self):
        """Check if loading curves and YoY are below benchmark."""
        bl = self.config.get("backbase_loading", {})
        current_yoy = bl.get("yoy_growth", [0.08] * 5)
        bench_yoy = self.benchmark.get("typical_yoy", 0.08)

        avg_current_yoy = sum(current_yoy) / len(current_yoy)

        if avg_current_yoy < bench_yoy - 0.02:
            # Estimate impact of YoY change
            current_metrics = self.metrics
            # Rough estimate: each 1pp YoY compounds over 5 years
            yoy_diff = bench_yoy - avg_current_yoy
            benefit_uplift_pct = yoy_diff * 5 * 0.6  # rough: 60% of naive compound
            estimated_impact_on_roi = benefit_uplift_pct * 100  # percentage points of ROI

            bench_impl = self.benchmark.get("impl_curve_moderate", [0.20, 0.70, 0.80, 1.00, 1.00])
            bench_eff = self.benchmark.get("eff_curve_moderate", [0.15, 0.35, 0.60, 0.85, 1.00])

            self.proposals.append(ExpansionProposal(
                lever_name=f"Calibrate Loading Curves & YoY Growth to {bench_yoy*100:.0f}%",
                category="curve_calibration",
                estimated_annual_impact=0,  # Doesn't add steady-state, changes timing
                justification=(
                    f"Current YoY growth {avg_current_yoy*100:.0f}% is below benchmark "
                    f"{bench_yoy*100:.0f}% for {self.segment}. Implementation curve also "
                    f"below benchmark moderate case. Calibrating to benchmark curves "
                    f"adds ~{estimated_impact_on_roi:.0f}pp to ROI through faster benefit realization."
                ),
                confidence="HIGH",
                benchmark_source=f"{self.segment} benchmark from roi_examples.md",
                config_patch={
                    "backbase_loading": {
                        "implementation_curve": bench_impl,
                        "effectiveness_curve": bench_eff,
                        "yoy_growth": [bench_yoy] * 5,
                    },
                },
            ))

    def _check_investment_calibration(self):
        """Check if investment is significantly below typical for segment."""
        investment = self.config.get("investment", {})
        total_inv = investment.get("total", 0)
        if not total_inv:
            lic = investment.get("license", {})
            imp = investment.get("implementation", {})
            total_inv = sum(lic.get(f"year_{i+1}", 0) for i in range(5)) + \
                        sum(imp.get(f"year_{i+1}", 0) for i in range(5))

        # Compare against knowledge base examples
        # HNB wealth: $9.6M, Seabank retail: $11M
        # If current is <70% of typical, flag it
        typical_ranges = {
            "Wealth Management": (8_000_000, 12_000_000),
            "Retail Banking": (8_000_000, 15_000_000),
            "Commercial Banking": (6_000_000, 12_000_000),
            "SME Banking": (5_000_000, 10_000_000),
            "Corporate Banking": (8_000_000, 15_000_000),
        }

        low_typical, high_typical = typical_ranges.get(self.segment, (5_000_000, 12_000_000))

        if total_inv < low_typical * 0.7:
            self.proposals.append(ExpansionProposal(
                lever_name=f"Calibrate Investment to ${low_typical/1e6:.1f}M (Knowledge Base Benchmark)",
                category="investment_calibration",
                estimated_annual_impact=0,  # Changes investment, not benefits
                justification=(
                    f"Current investment ${total_inv/1e6:.1f}M is significantly below "
                    f"typical range ${low_typical/1e6:.1f}-{high_typical/1e6:.1f}M for "
                    f"{self.segment}. Under-scoped investment may indicate missing platform "
                    f"components. HNB reference: $9.6M (License $6M + Impl $3.6M)."
                ),
                confidence="HIGH",
                benchmark_source="HNB V12, Seabank reference models",
                data_inputs_needed=["commercial_pricing", "implementation_scope"],
                config_patch=self._build_investment_patch(low_typical),
            ))

    def _build_investment_patch(self, target_total: float) -> dict:
        """Build an investment config patch to match target."""
        # Standard split: ~60% license, ~40% implementation
        # License spread evenly, implementation front-loaded
        license_total = target_total * 0.625
        impl_total = target_total * 0.375
        annual_license = license_total / 5

        return {
            "investment": {
                "license": {
                    "year_1": round(annual_license),
                    "year_2": round(annual_license),
                    "year_3": round(annual_license),
                    "year_4": round(annual_license),
                    "year_5": round(annual_license),
                    "total": round(license_total),
                },
                "implementation": {
                    "year_1": round(impl_total * 0.50),
                    "year_2": round(impl_total * 0.30),
                    "year_3": round(impl_total * 0.20),
                    "year_4": 0,
                    "year_5": 0,
                    "total": round(impl_total),
                },
                "total": round(target_total),
            }
        }

    def _check_cost_avoidance_reframing(self):
        """Check if RM benefits are framed as revenue uplift vs cost avoidance."""
        journeys = self.config.get("journeys", {})
        for j_key, journey in journeys.items():
            j_name = journey.get("journey_name", "").lower()
            if "rm" not in j_name and "productivity" not in j_name:
                continue

            rev_drivers = journey.get("revenue_drivers", {})
            for d_key, driver in rev_drivers.items():
                d_name = driver.get("name", "").lower()
                if "capacity" in d_name or "productivity" in d_name or "freed" in d_name:
                    current_benefit = driver.get("potential_annual_benefit", 0)
                    if current_benefit <= 0:
                        continue

                    # RM cost avoidance calculation
                    inputs = driver.get("inputs", {})
                    rm_count = inputs.get("rm_count", {}).get("value", 45)

                    # Calculate cost avoidance version
                    # Freed capacity = RMs * admin_reduction (60% → 30% = 30% freed)
                    admin_reduction = 0.27  # 27% capacity freed (conservative)

                    bp = self.config.get("bank_profile", {})
                    ac = bp.get("additional_context", {})
                    staff_costs_bw = ac.get("staff_costs_bankwide", {})
                    staff_costs = staff_costs_bw.get("value", 0) if isinstance(staff_costs_bw, dict) else 0
                    employees_bw = ac.get("total_employees_bankwide", {})
                    employees = employees_bw.get("value", 0) if isinstance(employees_bw, dict) else 0

                    if staff_costs and employees:
                        rm_annual_cost = (staff_costs / employees) * 1.5
                    else:
                        rm_annual_cost = 14000

                    cost_avoidance = rm_count * admin_reduction * rm_annual_cost
                    diff = cost_avoidance - current_benefit

                    if abs(diff) > 10_000:
                        self.proposals.append(ExpansionProposal(
                            lever_name="Reframe RM Capacity as Cost Avoidance (FTEs Not Hired)",
                            category="reframe_benefit",
                            estimated_annual_impact=round(diff) if diff > 0 else 0,
                            justification=(
                                f"Current RM capacity benefit framed as revenue uplift "
                                f"(${current_benefit:,.0f}). Reframing as cost avoidance: "
                                f"{rm_count} RMs × {admin_reduction*100:.0f}% capacity freed × "
                                f"${rm_annual_cost:,.0f}/yr RM cost = ${cost_avoidance:,.0f}. "
                                f"Cost avoidance is more defensible and conservative."
                            ),
                            confidence="HIGH",
                            benchmark_source="HNB V12 Lever 1 (RM capacity as cost avoidance)",
                            config_patch={
                                "_journey_key": j_key,
                                "_driver_key": d_key,
                                "_new_benefit": round(cost_avoidance),
                                "_new_name": "RM Cost Avoidance from Freed Capacity",
                                "_new_description": (
                                    f"Reducing admin from 60% to ~33% frees 27% of RM capacity. "
                                    f"Equivalent to {rm_count * admin_reduction:.0f} FTEs not needed "
                                    f"as book grows, at ${rm_annual_cost:,.0f}/yr per RM."
                                ),
                            },
                        ))
                    break

    def _check_missing_standard_levers(self):
        """Check for standard levers that are not modeled."""
        standard = set(self.benchmark.get("standard_levers", []))
        journeys = self.config.get("journeys", {})

        modeled_keywords = set()
        for j in journeys.values():
            name = j.get("journey_name", "").lower()
            if "onboarding" in name or "acquisition" in name:
                modeled_keywords.add("Customer Acquisition / Onboarding")
            if "loan" in name or "origination" in name or "lending" in name:
                modeled_keywords.add("Loan / Product Origination")
            if "servicing" in name or "service" in name:
                modeled_keywords.add("Customer Servicing")
            if "loyalty" in name or "retention" in name:
                modeled_keywords.add("Loyalty & Retention")
            if "rm" in name or "productivity" in name or "prospect" in name:
                modeled_keywords.add("RM Productivity / Prospecting")
            if "it" in name or "cost saving" in name or "legacy" in name:
                modeled_keywords.add("IT Cost Savings")
            if "conversion" in name or "retail" in name or "upgrade" in name:
                modeled_keywords.add("Retail-to-Wealth Conversion")
            if "platform" in name or "unified" in name or "cross" in name:
                modeled_keywords.add("Customer Servicing")  # Platform is effectively servicing

        missing = standard - modeled_keywords

        # Don't duplicate proposals already generated
        proposed_categories = {p.lever_name.lower() for p in self.proposals}

        for lever in missing:
            if any(lever.lower() in pc for pc in proposed_categories):
                continue
            if "retail" in lever.lower() and any("retail" in p.lever_name.lower() for p in self.proposals):
                continue

            self.proposals.append(ExpansionProposal(
                lever_name=f"Missing Standard Lever: {lever}",
                category="missing_lever",
                estimated_annual_impact=0,
                justification=(
                    f"'{lever}' is a standard value lever for {self.segment} "
                    f"engagements but is not modeled in the current config. "
                    f"Consider adding if relevant to the client's use case."
                ),
                confidence="LOW",
                benchmark_source=f"Standard {self.segment} lever template",
            ))

    # ── Report Generation ─────────────────────────────────────────

    def generate_report(self) -> str:
        """Generate a human-readable calibration report."""
        assessment = self.assess()
        lines = []
        lines.append("=" * 70)
        lines.append("ROI CALIBRATION REPORT")
        lines.append("=" * 70)
        lines.append(f"Client:           {self.config.get('client_name', 'Unknown')}")
        lines.append(f"Segment:          {assessment['segment']}")
        lines.append(f"Current ROI:      {assessment['current_roi']}%")
        lines.append(f"Expected Range:   {assessment['expected_range']}")
        lines.append(f"Status:           {assessment['status']}")
        lines.append("")

        m = assessment["metrics"]
        lines.append("CURRENT MODEL METRICS")
        lines.append("-" * 40)
        lines.append(f"  Steady-State Benefit:  ${m['total_steady_state']:,.0f}/yr")
        lines.append(f"  5-Year Benefits:       ${m['total_benefits_5yr']:,.0f}")
        lines.append(f"  5-Year Investment:     ${m['total_investment_5yr']:,.0f}")
        lines.append(f"  Net Benefit:           ${m['net_benefit']:,.0f}")
        lines.append(f"  ROI:                   {m['roi_percent']}%")
        lines.append(f"  NPV:                   ${m['npv']:,.0f}")
        lines.append(f"  IRR:                   {m['irr']}%")
        lines.append(f"  Payback:               {m['payback_years']} years")
        lines.append("")

        proposals = assessment.get("proposals", [])
        if not proposals:
            lines.append("No expansion proposals needed — ROI is within expected range.")
        else:
            gap = assessment["gap_to_lower_bound"]
            lines.append(f"GAP TO LOWER BOUND: {gap:.0f} percentage points")
            lines.append("")
            lines.append("PROPOSED EXPANSIONS (ranked by impact)")
            lines.append("=" * 70)

            for i, p in enumerate(proposals, 1):
                impact_label = "HIGH IMPACT" if p["estimated_annual_impact"] > 1_000_000 else \
                               "MEDIUM" if p["estimated_annual_impact"] > 100_000 else "LOW/TIMING"
                lines.append("")
                lines.append(f"  {i}. [{impact_label}] {p['lever_name']}")
                lines.append(f"     Category:    {p['category']}")
                if p["estimated_annual_impact"] > 0:
                    lines.append(f"     Est. Impact: +${p['estimated_annual_impact']:,.0f}/yr steady-state")
                else:
                    lines.append(f"     Est. Impact: Timing/structural (affects ROI through curves)")
                lines.append(f"     Confidence:  {p['confidence']}")
                lines.append(f"     Benchmark:   {p['benchmark_source']}")
                lines.append(f"     Justification:")
                # Word-wrap justification
                words = p["justification"].split()
                line = "       "
                for w in words:
                    if len(line) + len(w) + 1 > 80:
                        lines.append(line)
                        line = "       " + w
                    else:
                        line += " " + w if line.strip() else "       " + w
                if line.strip():
                    lines.append(line)
                if p["data_inputs_needed"]:
                    lines.append(f"     Data Needed: {', '.join(p['data_inputs_needed'])}")

            lines.append("")
            lines.append("-" * 70)
            lines.append(f"PROJECTED ROI WITH ALL EXPANSIONS: {assessment['projected_roi_with_all']}%")
            lines.append("-" * 70)

        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
# STAGE 2: AUTO-APPLY EXPANSIONS & REGENERATE
# ─────────────────────────────────────────────────────────────────────

class ROIExpander:
    """Applies approved expansion proposals to a config and regenerates."""

    def __init__(self, config: dict, calibrator: ROICalibrator):
        self.config = copy.deepcopy(config)
        self.calibrator = calibrator
        self.applied = []

    def apply_proposal(self, proposal_index: int) -> bool:
        """Apply a single proposal by index."""
        if proposal_index >= len(self.calibrator.proposals):
            return False

        p = self.calibrator.proposals[proposal_index]

        if p.category == "new_journey":
            return self._apply_new_journey(p)
        elif p.category == "curve_calibration":
            return self._apply_curve_calibration(p)
        elif p.category == "investment_calibration":
            return self._apply_investment_calibration(p)
        elif p.category == "multi_role_servicing":
            return self._apply_multi_role_servicing(p)
        elif p.category == "reframe_benefit":
            return self._apply_reframe_benefit(p)
        elif p.category == "missing_lever":
            print(f"  [SKIP] '{p.lever_name}' requires manual definition.")
            return False
        return False

    def apply_all(self) -> int:
        """Apply all proposals. Returns count of applied."""
        count = 0
        for i in range(len(self.calibrator.proposals)):
            if self.apply_proposal(i):
                count += 1
        self._recalculate_summary()
        return count

    def apply_selected(self, indices: list[int]) -> int:
        """Apply selected proposals by index. Returns count of applied."""
        count = 0
        for i in indices:
            if self.apply_proposal(i):
                count += 1
        self._recalculate_summary()
        return count

    def get_updated_config(self) -> dict:
        """Return the modified config."""
        return self.config

    def save_config(self, path: str):
        """Save updated config to JSON file."""
        with open(path, "w") as f:
            json.dump(self.config, f, indent=2)
        print(f"Updated config saved to: {path}")

    def regenerate_excel(self, output_path: str):
        """Regenerate Excel model from updated config."""
        from roi_excel_generator import ROIModelGenerator
        gen = ROIModelGenerator(self.config)
        gen.generate(output_path)

    # ── Appliers ──────────────────────────────────────────────────

    def _apply_new_journey(self, p: ExpansionProposal) -> bool:
        """Add a new journey (e.g., retail-to-wealth conversion)."""
        patch = p.config_patch
        key = patch.get("_new_journey_key", "new_journey")

        estimated_retail = patch.get("_estimated_retail", 200000)
        eligible_pool = patch.get("_eligible_pool", 24000)
        adoption_rate = patch.get("_adoption_rate", 0.15)
        new_clients_yr = patch.get("_new_clients_yr", 3600)
        revenue_annual = patch.get("_revenue_annual", 1700000)
        cost_avoidance = patch.get("_cost_avoidance", 1500000)
        rms_avoided = patch.get("_rms_avoided", 12)
        rm_cost = patch.get("_rm_cost", 14000)
        rev_per_client = patch.get("_rev_per_client", 946)
        rev_per_new_client = patch.get("_rev_per_new_client", rev_per_client * 0.05)
        digital_clients_per_rm = patch.get("_digital_clients_per_rm", 400)

        new_journey = {
            "journey_name": "Retail-to-Wealth Digital Conversion Pipeline",
            "current_state": (
                f"Large retail customer base (~{estimated_retail:,}) with {eligible_pool:,} "
                f"customers eligible for wealth services. No digital pathway for retail-to-wealth "
                f"upgrade. Conversion requires manual branch visit and paper onboarding."
            ),
            "target_state": (
                f"Digital self-enrollment pathway enabling retail customers to upgrade to wealth "
                f"services. Automated eligibility screening, digital onboarding, and RM assignment. "
                f"Target {adoption_rate*100:.0f}% annual conversion of eligible pool."
            ),
            "evidence_ids": ["KB-HNB-V12-L4"],
            "transcript_quotes": [],
            "revenue_drivers": {
                "digital_wealth_conversion_revenue": {
                    "name": "New Digital Wealth Client Revenue",
                    "description": (
                        f"Digital conversion of {new_clients_yr:,} retail customers/yr to wealth "
                        f"services at 50% of average wealth client revenue (ramp-up year)."
                    ),
                    "inputs": {
                        "eligible_pool": {
                            "value": eligible_pool,
                            "unit": "customers",
                            "source": f"DERIVED — {estimated_retail:,} retail × {adoption_rate*100:.0f}% eligible",
                            "confidence": "MEDIUM",
                            "validation_owner": "Head of Retail / Wealth",
                        },
                        "annual_adoption_rate": {
                            "value": adoption_rate,
                            "unit": "ratio",
                            "source": "BENCHMARK — HNB V12 Lever 4 used 20%. Conservative at 15%.",
                            "confidence": "LOW",
                            "validation_owner": "Digital Banking Head",
                        },
                        "revenue_per_new_client": {
                            "value": round(rev_per_new_client),
                            "unit": "USD/year",
                            "source": f"DERIVED — Entry-level digital converts at ~5% of avg wealth revenue (${rev_per_client:,.0f}). Min-threshold clients.",
                            "confidence": "MEDIUM",
                            "validation_owner": "Finance",
                        },
                    },
                    "calculation": "eligible_pool × adoption_rate × revenue_per_new_client",
                    "potential_annual_benefit": round(revenue_annual),
                },
            },
            "cost_drivers": {
                "rm_capacity_avoidance": {
                    "name": "RM Hiring Avoidance from Digital Self-Service",
                    "description": (
                        f"Digital onboarding + self-service portal means {new_clients_yr:,} new clients "
                        f"don't require proportional RM hiring. At {digital_clients_per_rm}:1 digital ratio, "
                        f"{rms_avoided:.0f} RMs avoided at ${rm_cost:,.0f}/yr each."
                    ),
                    "inputs": {
                        "new_clients_per_year": {
                            "value": new_clients_yr,
                            "unit": "clients/year",
                            "source": "DERIVED — From eligible pool × adoption rate.",
                            "confidence": "MEDIUM",
                            "validation_owner": "Head of Wealth",
                        },
                        "rms_not_hired": {
                            "value": round(rms_avoided, 1),
                            "unit": "FTE",
                            "source": f"DERIVED — {new_clients_yr:,} clients / current RM ratio.",
                            "confidence": "MEDIUM",
                            "validation_owner": "HR / Head of Wealth",
                        },
                        "rm_annual_cost": {
                            "value": round(rm_cost),
                            "unit": "USD/year",
                            "source": "DERIVED — 1.5× avg FTE cost from bank profile.",
                            "confidence": "MEDIUM",
                            "validation_owner": "HR/Finance",
                        },
                    },
                    "calculation": "rms_not_hired × rm_annual_cost",
                    "potential_annual_benefit": round(cost_avoidance),
                },
            },
            "totals": {
                "revenue_generation_total": round(revenue_annual),
                "cost_reduction_total": round(cost_avoidance),
                "journey_total": round(revenue_annual + cost_avoidance),
            },
        }

        self.config["journeys"][key] = new_journey
        self.applied.append(p.lever_name)
        print(f"  [APPLIED] {p.lever_name}: +${revenue_annual + cost_avoidance:,.0f}/yr")
        return True

    def _apply_curve_calibration(self, p: ExpansionProposal) -> bool:
        """Apply loading curve calibration."""
        patch = p.config_patch.get("backbase_loading", {})
        bl = self.config.get("backbase_loading", {})
        bl.update(patch)
        self.config["backbase_loading"] = bl

        # Also update scenarios moderate case
        scenarios = self.config.get("scenarios", {})
        if "moderate" in scenarios:
            mod = scenarios["moderate"]
            if "implementation_curve" in patch:
                mod["implementation_curve"] = patch["implementation_curve"]
            if "effectiveness_curve" in patch:
                mod["effectiveness_curve"] = patch["effectiveness_curve"]
            if "yoy_growth" in patch:
                mod["yoy_growth"] = patch["yoy_growth"]

        self.applied.append(p.lever_name)
        print(f"  [APPLIED] {p.lever_name}")
        return True

    def _apply_investment_calibration(self, p: ExpansionProposal) -> bool:
        """Apply investment calibration."""
        patch = p.config_patch.get("investment", {})
        if patch:
            self.config["investment"] = patch
        self.applied.append(p.lever_name)
        total = patch.get("total", 0)
        print(f"  [APPLIED] {p.lever_name}: Investment → ${total:,.0f}")
        return True

    def _apply_multi_role_servicing(self, p: ExpansionProposal) -> bool:
        """Apply multi-role time multipliers to servicing tasks."""
        patch = p.config_patch
        j_key = patch.get("_servicing_journey_key")
        multipliers = patch.get("_multipliers", MULTI_ROLE_MULTIPLIERS)

        if not j_key or j_key not in self.config.get("journeys", {}):
            return False

        journey = self.config["journeys"][j_key]
        sa = journey.get("servicing_analysis", {})

        total_saved = 0
        total_baseline = 0

        for ch_key, channel in sa.items():
            if not isinstance(channel, dict) or "tasks" not in channel:
                continue

            ch_saved = 0
            ch_baseline = 0

            for task in channel["tasks"]:
                task_name = task.get("task", "").lower()
                # Find best matching multiplier
                mult = 1.0
                for mk, mv in multipliers.items():
                    mk_words = mk.replace("_", " ")
                    if any(w in task_name for w in mk_words.split()):
                        mult = mv
                        break

                if mult > 1.0:
                    old_time = task["time_spent_hours"]
                    new_time = round(old_time * mult, 2)
                    task["time_spent_hours"] = new_time
                    task["time_source"] = (
                        f"MULTI-ROLE — Original {old_time}h × {mult}x "
                        f"(RM + RM Assistant + Back Office combined time)"
                    )

                # Recalculate baseline and saved
                vol = task.get("yearly_volume", 0)
                time_h = task.get("time_spent_hours", 0)
                rate = task.get("fte_rate", 7.70)
                impact = task.get("backbase_impact", 0)
                baseline = vol * time_h * rate
                saved = baseline * impact
                task["baseline_cost"] = round(baseline)
                task["cost_saved"] = round(saved)
                ch_saved += saved
                ch_baseline += baseline

            channel["channel_total"]["baseline_cost"] = round(ch_baseline)
            channel["channel_total"]["cost_saved"] = round(ch_saved)
            total_saved += ch_saved
            total_baseline += ch_baseline

        # Update journey totals
        totals = journey.get("totals", {})
        totals["total_baseline_cost"] = round(total_baseline)
        totals["total_cost_saved"] = round(total_saved)
        totals["cost_reduction_total"] = round(total_saved)
        totals["journey_total"] = totals.get("revenue_generation_total", 0) + round(total_saved)
        journey["totals"] = totals

        self.applied.append(p.lever_name)
        print(f"  [APPLIED] {p.lever_name}: Servicing → ${total_saved:,.0f}/yr")
        return True

    def _apply_reframe_benefit(self, p: ExpansionProposal) -> bool:
        """Reframe a revenue driver as cost avoidance."""
        patch = p.config_patch
        j_key = patch.get("_journey_key")
        d_key = patch.get("_driver_key")
        new_benefit = patch.get("_new_benefit", 0)
        new_name = patch.get("_new_name", "")
        new_desc = patch.get("_new_description", "")

        if not j_key or j_key not in self.config.get("journeys", {}):
            return False

        journey = self.config["journeys"][j_key]
        rev_drivers = journey.get("revenue_drivers", {})

        if d_key not in rev_drivers:
            return False

        driver = rev_drivers[d_key]
        old_benefit = driver.get("potential_annual_benefit", 0)

        # Move from revenue_drivers to cost_drivers
        cost_drivers = journey.get("cost_drivers", {})
        cost_driver = copy.deepcopy(driver)
        cost_driver["name"] = new_name
        cost_driver["description"] = new_desc
        cost_driver["potential_annual_benefit"] = new_benefit
        cost_drivers[d_key + "_reframed"] = cost_driver

        # Remove from revenue drivers
        del rev_drivers[d_key]

        journey["revenue_drivers"] = rev_drivers
        journey["cost_drivers"] = cost_drivers

        # Recalculate totals
        rev_total = sum(d.get("potential_annual_benefit", 0) for d in rev_drivers.values())
        cost_total = sum(d.get("potential_annual_benefit", 0) for d in cost_drivers.values())

        # Add servicing cost saved if present
        serv_saved = journey.get("totals", {}).get("total_cost_saved", 0)
        if serv_saved and serv_saved != cost_total:
            cost_total_for_journey = cost_total + serv_saved
        else:
            cost_total_for_journey = cost_total

        totals = journey.get("totals", {})
        totals["revenue_generation_total"] = rev_total
        totals["cost_reduction_total"] = cost_total_for_journey
        totals["journey_total"] = rev_total + cost_total_for_journey

        self.applied.append(p.lever_name)
        print(f"  [APPLIED] {p.lever_name}: ${old_benefit:,.0f} → ${new_benefit:,.0f} (cost avoidance)")
        return True

    def _recalculate_summary(self):
        """Recalculate the summary section from journey totals."""
        journeys = self.config.get("journeys", {})
        benefits = []
        total = 0
        for j_key, journey in journeys.items():
            t = journey.get("totals", {})
            jt = t.get("journey_total", 0)
            benefits.append({
                "journey": journey.get("journey_name", j_key),
                "revenue_generation": t.get("revenue_generation_total", 0),
                "cost_reduction": t.get("cost_reduction_total", 0),
                "total": jt,
            })
            total += jt

        self.config["summary"] = {
            "journey_benefits": benefits,
            "total_annual_benefit_steady_state": round(total),
            "notes": self.config.get("summary", {}).get("notes", ""),
        }


# ─────────────────────────────────────────────────────────────────────
# CLI ENTRYPOINT
# ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ROI Calibrator — Assess and expand ROI models")
    parser.add_argument("--config", "-c", required=True, help="Path to ROI config JSON")
    parser.add_argument("--apply", action="store_true", help="Auto-apply all proposals (Stage 2)")
    parser.add_argument("--apply-indices", type=str, help="Comma-separated indices to apply (e.g., '0,1,3')")
    parser.add_argument("--output-config", type=str, help="Path to save updated config JSON")
    parser.add_argument("--output-excel", type=str, help="Path to save regenerated Excel")
    parser.add_argument("--json", action="store_true", help="Output assessment as JSON instead of text report")

    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config not found: {config_path}")
        exit(1)

    with open(config_path) as f:
        config = json.load(f)

    # Stage 1: Assess
    calibrator = ROICalibrator(config)

    if args.json:
        assessment = calibrator.assess()
        print(json.dumps(assessment, indent=2))
    else:
        report = calibrator.generate_report()
        print(report)

    # Stage 2: Apply if requested
    if args.apply or args.apply_indices:
        print("\n" + "=" * 70)
        print("APPLYING EXPANSIONS")
        print("=" * 70)

        expander = ROIExpander(config, calibrator)

        if args.apply:
            count = expander.apply_all()
        else:
            indices = [int(x.strip()) for x in args.apply_indices.split(",")]
            count = expander.apply_selected(indices)

        print(f"\nApplied {count} expansion(s).")

        # Show new metrics
        new_metrics = compute_roi_metrics(expander.get_updated_config())
        print(f"\nUPDATED MODEL METRICS")
        print("-" * 40)
        print(f"  Steady-State Benefit:  ${new_metrics['total_steady_state']:,.0f}/yr")
        print(f"  5-Year Benefits:       ${new_metrics['total_benefits_5yr']:,.0f}")
        print(f"  5-Year Investment:     ${new_metrics['total_investment_5yr']:,.0f}")
        print(f"  Net Benefit:           ${new_metrics['net_benefit']:,.0f}")
        print(f"  ROI:                   {new_metrics['roi_percent']}%")
        print(f"  NPV:                   ${new_metrics['npv']:,.0f}")
        print(f"  IRR:                   {new_metrics['irr']}%")
        print(f"  Payback:               {new_metrics['payback_years']} years")

        # Save config
        if args.output_config:
            expander.save_config(args.output_config)
        else:
            # Default: save next to original with _calibrated suffix
            out_path = config_path.parent / (config_path.stem + "_calibrated.json")
            expander.save_config(str(out_path))

        # Regenerate Excel
        if args.output_excel:
            expander.regenerate_excel(args.output_excel)


if __name__ == "__main__":
    main()
