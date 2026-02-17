#!/usr/bin/env python3
"""
Capability Taxonomy Domain Splitter

Splits the master capability_taxonomy.md (2,109 lines) into domain-specific
slices (~300-500 lines each) so agents load only what they need.

Usage:
    python3 scripts/split_capability_taxonomy.py

Input:  knowledge/standards/capability_taxonomy.md
Output: knowledge/standards/capability_taxonomy_{domain}.md (5 files)

The master file stays intact for reference.
"""

from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MASTER_PATH = REPO_ROOT / "knowledge" / "standards" / "capability_taxonomy.md"
OUTPUT_DIR = REPO_ROOT / "knowledge" / "standards"

# Part boundaries (1-indexed line numbers from the master file)
# These correspond to ## Part N headers found via grep
PARTS = {
    "shared_header": (1, 8),         # File header
    "part1": (9, 38),                # Maturity Scale Definition
    "part2": (40, 57),               # Front / Middle / Back Layer Definitions
    "part3": (60, 81),               # BIAN Business Areas mapping
    "part4_retail": (83, 688),       # Retail Capability Catalog
    "part5_unconsidered": (689, 746),# Unconsidered Needs Library (all domains)
    "part6_problem_cats": (749, 770),# Problem Statement Categories
    "part7_wealth": (772, 824),      # Wealth Capability Catalog
    "part8_sme": (825, 1262),        # SME Capability Catalog
    "part9_commercial": (1263, 1677),# Commercial Capability Catalog
    "part10_corporate": (1678, 2078),# Corporate Capability Catalog
    "part11_howto": (2079, 2109),    # How to Use This Taxonomy
}

# Unconsidered Needs sub-sections (line numbers within Part 5)
UNCONSIDERED_SECTIONS = {
    "retail": (693, 702),
    "wealth": (704, 712),
    "sme": (714, 723),
    "commercial": (725, 733),
    "corporate": (736, 746),
}

# Domain → which parts to include
DOMAIN_SLICES = {
    "retail": {
        "catalog_part": "part4_retail",
        "unconsidered_key": "retail",
        "label": "Retail Banking",
    },
    "wealth": {
        "catalog_part": "part7_wealth",
        "unconsidered_key": "wealth",
        "label": "Wealth Management",
    },
    "sme": {
        "catalog_part": "part8_sme",
        "unconsidered_key": "sme",
        "label": "SME Banking",
    },
    "commercial": {
        "catalog_part": "part9_commercial",
        "unconsidered_key": "commercial",
        "label": "Commercial Banking",
    },
    "investing": {
        # Investing uses wealth catalog + retail digital investing subset
        "catalog_part": "part7_wealth",
        "unconsidered_key": "wealth",
        "label": "Investing / Digital Wealth",
        "extra_note": "For pure investing engagements (e.g., self-directed trading), use this slice. For full wealth management (advisor-led), use the wealth slice.",
    },
}


def read_lines(path: Path) -> list[str]:
    """Read file into list of lines (1-indexed access via lines[n-1])."""
    return path.read_text(encoding="utf-8").splitlines()


def extract_range(lines: list[str], start: int, end: int) -> list[str]:
    """Extract lines from start to end (1-indexed, inclusive)."""
    return lines[start - 1:end]


def write_domain_slice(domain: str, config: dict, all_lines: list[str]):
    """Write a domain-specific taxonomy slice."""
    output_path = OUTPUT_DIR / f"capability_taxonomy_{domain}.md"

    sections = []

    # Header
    sections.append(f"# Capability Taxonomy — {config['label']}")
    sections.append(f"")
    sections.append(f"> **Domain slice** auto-generated from `capability_taxonomy.md`")
    sections.append(f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    sections.append(f"> Master file: `knowledge/standards/capability_taxonomy.md` (2,109 lines)")
    sections.append(f"> This slice: ~{config['label']} capabilities only")
    if config.get("extra_note"):
        sections.append(f"> Note: {config['extra_note']}")
    sections.append(f"")
    sections.append(f"---")
    sections.append(f"")

    # Part 1: Maturity Scale (always needed)
    sections.extend(extract_range(all_lines, *PARTS["part1"]))
    sections.append("")

    # Part 2: F/M/B Layers (always needed)
    sections.extend(extract_range(all_lines, *PARTS["part2"]))
    sections.append("")

    # Part 3: BIAN Mapping (always needed)
    sections.extend(extract_range(all_lines, *PARTS["part3"]))
    sections.append("")

    # Domain-specific catalog
    catalog_key = config["catalog_part"]
    sections.extend(extract_range(all_lines, *PARTS[catalog_key]))
    sections.append("")

    # Unconsidered Needs for this domain
    un_key = config["unconsidered_key"]
    un_range = UNCONSIDERED_SECTIONS[un_key]
    sections.append("## Unconsidered Needs")
    sections.append("")
    sections.append("Problems the bank has NOT raised but should be assessed:")
    sections.append("")
    sections.extend(extract_range(all_lines, *un_range))
    sections.append("")

    # Part 6: Problem Statement Categories (always needed)
    sections.extend(extract_range(all_lines, *PARTS["part6_problem_cats"]))
    sections.append("")

    # Part 11: How to Use (always needed)
    sections.extend(extract_range(all_lines, *PARTS["part11_howto"]))

    content = "\n".join(sections)
    output_path.write_text(content, encoding="utf-8")
    line_count = len(sections)
    print(f"  Written: {output_path.name} ({line_count} lines)")


def main():
    if not MASTER_PATH.exists():
        print(f"Error: Master taxonomy not found at {MASTER_PATH}")
        return

    all_lines = read_lines(MASTER_PATH)
    print(f"Loaded master taxonomy: {len(all_lines)} lines")

    for domain, config in DOMAIN_SLICES.items():
        write_domain_slice(domain, config, all_lines)

    print(f"\nDone. {len(DOMAIN_SLICES)} domain slices generated.")
    print(f"Master file unchanged at: {MASTER_PATH}")


if __name__ == "__main__":
    main()
