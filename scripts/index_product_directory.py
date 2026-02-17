#!/usr/bin/env python3
"""
Product Directory Domain Indexer

Generates domain-specific summary files from the full Product Directory CSV.
Each summary is ~200-300 lines — small enough for any agent to load without
exceeding context limits.

Usage:
    python3 scripts/index_product_directory.py

Input:  knowledge/domains/Product Directory (1).csv (3,117 lines)
Output: knowledge/domains/product_directory_{domain}.md (5 files)

Regenerate whenever the CSV is updated.
"""

import csv
import hashlib
from collections import defaultdict
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "knowledge" / "domains" / "Product Directory (1).csv"
OUTPUT_DIR = REPO_ROOT / "knowledge" / "domains"

# --- Domain and lifecycle mappings ---

# Lifecycle stage mapping: Journey name patterns → lifecycle stage
LIFECYCLE_MAP = {
    # Acquire: Discovery, application, onboarding
    "Acquire": [
        "Product Explorer", "Product Selection", "Product Details",
        "Identity Verification", "Application Center", "Application Submission",
        "Loan Application", "Loan Offer", "Loan Calculator",
        "Credit Decisioning", "Credit Report", "Credit Score",
        "Financial Data Gathering", "Financial Ratios Calculation",
        "Financial Spreading", "Pre-Qualification",
        "Eligibillity Questionnaire", "Credit Union Eligibility",
        "Due Diligence", "Customer & Account Creation",
        "Account Funding", "User Registration", "User Self-Enrollment",
        "Self-Enrollment", "User enrollment", "Credential Creation",
        "Resume Application", "eConsent", "eSignature",
        "Agreements Review", "Terms & Conditions",
        "Risk Assessment", "Anti-Money Laundering",
        "Lending Regulatory Compliance", "Adverse Action Notice",
        "US Address Validation", "Address Validation",
        "US Residency Declaration", "Document Request",
        "Company Lookup", "Business Credit Report",
    ],
    # Activate: Day-to-day banking
    "Activate": [
        "App Foundation", "Authentication", "Dashboard",
        "Accounts & Transactions", "Accounts and Transactions",
        "Payments", "Card Management", "Transfers",
        "Direct Debits", "Direct Deposit Switch",
        "Statements", "Account Statements",
        "Remote Deposit Capture", "Bill Pay",
        "Forex", "Stop Checks", "Check Positive Pay",
        "ACH Positive Pay", "Positive Pay",
        "External Account", "Account Recovery",
        "Context Selection", "User Self-Service",
        "Manage devices", "Manage security",
        "Step-up Authentication", "One-Time Password",
        "Transaction Signing", "Profile", "Personal Data",
        "Settings", "User Profile", "Marketing Preferences",
        "Family Banking", "Joint Account",
        "Pockets", "Credit Cards", "Loans", "Loan Servicing",
        "Plan Management", "Savings Plan",
    ],
    # Expand: Growth, cross-sell, investing
    "Expand": [
        "Trading", "Digital Investing",
        "Portfolio", "Portfolio Overview", "Portfolio Reporting",
        "Robo-view", "Portfolio selection",
        "Tailored Value Proposition", "Engagements",
        "Create engagement", "Manage engagements",
        "Create audience", "Manage audiences",
        "Push engagement notification", "Analyze Engagement",
        "Financial Insights", "Direct Insights",
        "Cash Flow Forecasting",
    ],
    # Retain: Service, support, relationship
    "Retain": [
        "Case Manager", "Cases", "Case Data Store",
        "Messages", "Message Center", "Message delivery",
        "Messaging Management", "Messages Center Service",
        "Live chat", "Chat history", "Chat inbox", "Chat management",
        "Real Time Communication", "Real-Time Communication",
        "Quick assist", "Assist Messaging",
        "Appointments", "Appointment management",
        "Notifications", "Manage general notifications",
        "Notifications list",
        "Customer overview", "Customer Profile Service",
        "Customer information", "Customer account",
        "Relationship Manager Dashboard",
        "Activity Timeline", "Activity log",
        "Document Storage", "Document Store",
        "Places", "Overlays", "Banner",
        "Progress", "Progress Tracking",
    ],
    # Platform: Shared infrastructure
    "Platform": [
        "API ToolKit", "Backend Devkit", "Mobile Devkit", "Web DevKit",
        "Design System", "Edge", "Remote Config",
        "Integration Engine", "Interaction Engine",
        "Process & Decision Engine", "Service Discovery",
        "Provisioning", "PDF Generation",
        "Centralized Data Validation", "Data Collections",
        "Flow Selector", "Step Navigation",
        "Questionnaire", "Questionnaire Capability",
        "Language selector", "Collapsable panels",
        "Identity & Access Management", "Access Control",
        "Entitlements", "User Management", "User Search",
        "User Lifecycle", "User sessions", "Create user",
        "Impersonation", "Emulation", "Audit",
        "Account Verification & Transaction Import",
        "Accounting Import", "Information Reporting",
        "EBP Integrations",
    ],
}

# Domain mapping: Which lifecycle stages + specific journeys belong to each domain
# shared = Platform + Activate (core banking used by all)
DOMAIN_MAP = {
    "retail": {
        "lifecycle_stages": ["Acquire", "Activate", "Expand", "Retain", "Platform"],
        "include_keywords": [],  # Retail gets everything not claimed by others
        "exclude_keywords": [
            "Trade Finance", "Boardroom", "Business Profile",
            "Business Relations", "Approvals Dashboard",
        ],
        "description": "Core retail banking: onboarding, day-to-day banking, payments, cards, lending, engagement",
    },
    "wealth": {
        "lifecycle_stages": ["Activate", "Expand", "Retain", "Platform"],
        "include_keywords": [
            "Portfolio", "Trading", "Digital Investing", "Robo-view",
            "Relationship Manager", "Customer overview",
            "Tailored Value Proposition", "Financial Insights",
            "Engagements", "Appointments",
        ],
        "exclude_keywords": [],
        "description": "Wealth management & investing: portfolio, trading, advisor workspace, client engagement",
    },
    "sme": {
        "lifecycle_stages": ["Acquire", "Activate", "Retain", "Platform"],
        "include_keywords": [
            "Business Profile", "Business Relations", "Business Credit",
            "Cash Flow Forecasting", "Approvals", "Batches",
            "Entitlements", "Contacts", "Beneficiaries",
            "Company Lookup", "Financial Spreading",
            "Financial Ratios", "Financial Data Gathering",
        ],
        "exclude_keywords": ["Trade Finance", "Boardroom"],
        "description": "SME banking: business accounts, cash management, approvals, lending, business services",
    },
    "investing": {
        "lifecycle_stages": ["Activate", "Expand", "Platform"],
        "include_keywords": [
            "Digital Investing", "Trading", "Portfolio",
            "Robo-view", "Account Funding",
            "Product Explorer", "Product Selection",
        ],
        "exclude_keywords": [],
        "description": "Digital investing: self-directed trading, portfolio management, robo-advisory",
    },
    "commercial": {
        "lifecycle_stages": ["Acquire", "Activate", "Retain", "Platform"],
        "include_keywords": [
            "Trade Finance", "Boardroom", "Positive Pay",
            "Information Reporting", "Approvals",
            "Entitlements", "Batches", "Contacts",
            "Beneficiaries", "Forex",
        ],
        "exclude_keywords": [],
        "description": "Commercial & corporate banking: trade finance, treasury, payments, reporting",
    },
}


def compute_file_hash(path: Path) -> str:
    """SHA256 of the source CSV for staleness detection."""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def parse_csv(path: Path) -> list[dict]:
    """Parse the Product Directory CSV."""
    rows = []
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean whitespace from keys and values
            cleaned = {k.strip(): v.strip() if v else "" for k, v in row.items()}
            rows.append(cleaned)
    return rows


def classify_lifecycle(journey: str) -> str:
    """Map a journey name to a lifecycle stage."""
    for stage, patterns in LIFECYCLE_MAP.items():
        for pattern in patterns:
            if pattern.lower() in journey.lower():
                return stage
    return "Other"


def journey_matches_domain(journey: str, domain_config: dict) -> bool:
    """Check if a journey belongs to a domain."""
    j_lower = journey.lower()

    # Check explicit exclusions
    for kw in domain_config.get("exclude_keywords", []):
        if kw.lower() in j_lower:
            return False

    # Check explicit inclusions (if any specified, journey must match one)
    include_kws = domain_config.get("include_keywords", [])
    if include_kws:
        return any(kw.lower() in j_lower for kw in include_kws)

    # For retail (no include_keywords): include everything not excluded
    return True


def build_domain_summary(rows: list[dict], domain: str, config: dict) -> dict:
    """Build summary statistics for a domain."""
    journey_stats = defaultdict(lambda: {
        "total": 0, "essential": 0, "premium_only": 0,
        "signature_only": 0, "mobile": 0, "web": 0,
        "lifecycle": "", "features": [],
    })

    for row in rows:
        journey = row.get("Journey", "").strip()
        if not journey or not journey_matches_domain(journey, config):
            continue

        lifecycle = classify_lifecycle(journey)
        stats = journey_stats[journey]
        stats["total"] += 1
        stats["lifecycle"] = lifecycle

        ess = row.get("Essential", "").lower() == "true"
        prem = row.get("Premium", "").lower() == "true"
        sig = row.get("Signature", "").lower() == "true"

        if ess:
            stats["essential"] += 1
        if prem and not ess:
            stats["premium_only"] += 1
        if sig and not prem and not ess:
            stats["signature_only"] += 1

        if "available" in row.get("Mobile", "").lower():
            stats["mobile"] += 1
        if "available" in row.get("Web", "").lower():
            stats["web"] += 1

        # Track premium/signature-only features for the differentiators list
        feature = row.get("Feature", "").strip()
        sub = row.get("Sub Feature", "").strip()
        if (prem and not ess) or (sig and not prem):
            tier = "Premium" if prem else "Signature"
            fid = row.get("Subfeature ID", "")
            stats["features"].append({
                "id": fid, "feature": feature, "sub": sub, "tier": tier,
            })

    return dict(journey_stats)


def write_domain_file(domain: str, config: dict, stats: dict, csv_hash: str):
    """Write a domain summary markdown file."""
    output_path = OUTPUT_DIR / f"product_directory_{domain}.md"

    # Group journeys by lifecycle
    by_lifecycle = defaultdict(list)
    for journey, data in sorted(stats.items()):
        by_lifecycle[data["lifecycle"]].append((journey, data))

    lines = []
    lines.append(f"# Product Directory Summary — {domain.title()}")
    lines.append(f"")
    lines.append(f"> Auto-generated by `scripts/index_product_directory.py`")
    lines.append(f"> Source: `knowledge/domains/Product Directory (1).csv` (hash: {csv_hash})")
    lines.append(f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"> Domain: **{domain.title()}** — {config['description']}")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    # Summary stats
    total_features = sum(d["total"] for d in stats.values())
    total_journeys = len(stats)
    lines.append(f"## Overview")
    lines.append(f"")
    lines.append(f"- **Journeys:** {total_journeys}")
    lines.append(f"- **Total sub-features:** {total_features}")
    lines.append(f"")

    # By lifecycle stage
    lifecycle_order = ["Acquire", "Activate", "Expand", "Retain", "Platform", "Other"]

    for stage in lifecycle_order:
        journeys = by_lifecycle.get(stage, [])
        if not journeys:
            continue

        stage_total = sum(d["total"] for _, d in journeys)
        lines.append(f"## {stage} ({stage_total} sub-features)")
        lines.append(f"")
        lines.append(f"| Journey | Total | Essential | Premium+ | Signature+ | Mobile | Web |")
        lines.append(f"|---------|-------|-----------|----------|------------|--------|-----|")

        for journey, data in sorted(journeys, key=lambda x: -x[1]["total"]):
            lines.append(
                f"| {journey} | {data['total']} | {data['essential']} | "
                f"{data['premium_only']} | {data['signature_only']} | "
                f"{data['mobile']} | {data['web']} |"
            )
        lines.append(f"")

    # Key differentiators (Premium/Signature only features)
    all_diffs = []
    for journey, data in stats.items():
        for feat in data.get("features", []):
            all_diffs.append({**feat, "journey": journey})

    if all_diffs:
        lines.append(f"## Key Differentiators (Premium/Signature Only)")
        lines.append(f"")
        lines.append(f"These features are NOT available in Essential tier:")
        lines.append(f"")
        lines.append(f"| ID | Journey | Feature | Sub-Feature | Tier |")
        lines.append(f"|----|---------|---------|-------------|------|")

        # Show top 30 by journey relevance
        for diff in all_diffs[:30]:
            lines.append(
                f"| {diff['id']} | {diff['journey']} | "
                f"{diff['feature']} | {diff['sub'][:60]} | {diff['tier']} |"
            )

        if len(all_diffs) > 30:
            lines.append(f"")
            lines.append(f"*...and {len(all_diffs) - 30} more. Load the full CSV for complete list.*")
        lines.append(f"")

    # OOTB coverage estimate
    total_ess = sum(d["essential"] for d in stats.values())
    ootb_pct = round(total_ess / total_features * 100) if total_features > 0 else 0
    lines.append(f"## OOTB Coverage")
    lines.append(f"")
    lines.append(f"- **Essential tier coverage:** {ootb_pct}% ({total_ess}/{total_features} sub-features)")
    lines.append(f"- For feature-level detail beyond this summary, query MCP Infobank or load the full CSV")
    lines.append(f"- **Only the Use Case Designer agent should load the full CSV** (3,117 lines)")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"*End of {domain.title()} Product Directory Summary*")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Written: {output_path.name} ({len(lines)} lines)")


def main():
    if not CSV_PATH.exists():
        print(f"Error: CSV not found at {CSV_PATH}")
        return

    csv_hash = compute_file_hash(CSV_PATH)
    rows = parse_csv(CSV_PATH)
    print(f"Loaded {len(rows)} rows from Product Directory (hash: {csv_hash})")

    for domain, config in DOMAIN_MAP.items():
        stats = build_domain_summary(rows, domain, config)
        write_domain_file(domain, config, stats, csv_hash)

    print(f"\nDone. {len(DOMAIN_MAP)} domain summaries generated.")


if __name__ == "__main__":
    main()
