# Profile Bank — Public Financial Data Extraction

Research a bank's public financial data to pre-populate ROI model inputs with HIGH confidence metrics instead of estimates.

## What This Skill Does

Identifies a bank, fetches public financial data (annual reports, investor presentations, press releases), and extracts ROI-relevant metrics — both direct (read from statements) and derived (calculated from multiple data points). Outputs a structured JSON that maps directly to the ROI config `basic_information` section.

## Usage

```
/profile-bank [bank name] [country]
```

Arguments:
- `[bank name]` — Required. The bank's name (or common abbreviation)
- `[country]` — Optional but recommended. Prevents misidentification of similarly-named banks

## Instructions

When this skill is invoked, follow this 6-step protocol **exactly**. Do NOT skip steps.

### Step 1: Parse Input

Extract from the user's message:
- **Bank name** (required)
- **Country** (optional — if not provided, search will attempt to identify)
- **Segment focus** (optional — retail, wealth, SME, commercial, corporate)

### Step 2: Bank Identification (WebSearch)

Search the web to gather:
- Official legal name
- Country of incorporation
- Stock exchange & ticker (if publicly listed)
- Website URL
- Parent company / group (if subsidiary)
- Key facts: year founded, bank type (commercial, retail, Islamic, cooperative, etc.)
- Latest fiscal year reported

### Step 3: Human Confirmation (MANDATORY — DO NOT SKIP)

**You MUST present your findings and ask the user to confirm before proceeding.** Use the AskUserQuestion tool with a format like:

```
I found the following bank:

  Name:     [Official Legal Name]
  Country:  [Country]
  Ticker:   [Ticker] ([Exchange])
  Website:  [URL]
  Type:     [Bank Type]
  Parent:   [Parent or "Standalone"]

Is this the correct bank?
```

Options:
- **Yes, proceed** — Continue to Step 4
- **No, let me clarify** — User provides correction, return to Step 2

**Why this step exists:** Banks with similar names exist in different countries (e.g., Bank Rakyat Malaysia vs Bank Rakyat Indonesia, Standard Bank vs Standard Chartered). Misidentification would corrupt the entire ROI model.

### Step 4: Find Financial Data Sources (WebSearch + WebFetch)

Search for the bank's latest financial data. Try sources in this priority order:

1. **Financial highlights / fact sheet** — Often 1-2 page HTML summaries, easiest to parse
2. **Investor presentation** — Condensed financial data, usually available on investor relations page
3. **Annual report (HTML version)** — Comprehensive; look for HTML or summary pages rather than full PDFs
4. **Press releases** — Q4/FY results announcements often contain key figures
5. **Wikipedia / financial data aggregators** — Good for summary metrics, lower confidence

For each source found, note the URL, publication date, and what metrics it contains.

### Step 5: Extract & Derive Metrics

Refer to the **Bank Profiler Agent definition** (`agents/definitions/bank-profiler.md`) for the full metric extraction framework, derivation rules, and confidence classification.

**Key requirements:**
- Every metric must have: value, unit, source (with page/URL), and confidence level
- Derived metrics must show the full derivation chain so the user can verify
- Confidence levels: HIGH (direct from audited statements), MEDIUM (derived from 2+ public data points), LOW (estimated/benchmarked)
- Record values in the bank's **local currency** AND note the currency code
- If a metric is not available, add it to `data_gaps` with priority and impact assessment

#### Direct Metrics to Extract

| Metric | Where to Find | ROI Config Field |
|--------|---------------|------------------|
| Total customers | Annual report overview | `basic_information.total_customers` |
| Total employees / FTE | HR section or notes | `basic_information.total_fte` |
| Total operating income | Income statement | `basic_information.annual_revenue` |
| Total operating expenses | Income statement | `basic_information.operating_costs` |
| Staff costs | Income statement / notes | (used for derivation) |
| Cost-to-income ratio | Financial highlights | `basic_information.cost_to_income_ratio` |
| Net interest income | Income statement | `additional_context` |
| Non-interest income | Income statement | `additional_context` |
| Total assets | Balance sheet | `additional_context` |
| Total loans | Balance sheet | `additional_context` |
| Total deposits | Balance sheet | `additional_context` |
| Number of branches | Annual report | `additional_context` |
| Digital active users | Digital section | `additional_context` |
| NPL ratio | Annual report | `additional_context` |
| Capital adequacy ratio | Annual report | `additional_context` |
| ROE | Annual report | `additional_context` |

#### Derived Metrics to Calculate

| Metric | Formula | ROI Config Field |
|--------|---------|------------------|
| Cost per FTE (hourly) | `staff_costs / fte_count / 2000` | `basic_information.average_fte_rate_hour` |
| Revenue per customer | `annual_revenue / total_customers` | `basic_information.average_revenue_per_customer` |
| Cost-to-income ratio | `opex / operating_income` (if not directly stated) | `basic_information.cost_to_income_ratio` |
| Digital adoption rate | `digital_active_users / total_customers` | `additional_context` |
| Avg deposit per customer | `total_deposits / total_customers` | `additional_context` |
| Employees per branch | `fte_count / num_branches` | `additional_context` |

**Derivation transparency example:**
```
Cost per FTE (hourly): $18.75
  <- Staff costs: $75M (Income Statement, AR p.45)
  <- FTE count: 2,000 (HR Section, AR p.12)
  <- $75M / 2,000 = $37,500/year
  <- $37,500 / 2,000 hours = $18.75/hour
  Confidence: MEDIUM (derived from two public data points)
```

### Step 6: Generate Output

Produce **two files** in the engagement's outputs folder:

#### A. `bank_profile.md` — Human-Readable Summary

Structure:
1. Bank identity (name, country, type, ticker, fiscal year)
2. Financial overview (key headline numbers)
3. ROI-relevant metrics table (value, source, confidence)
4. Derived metrics with full derivation chains
5. Additional context metrics
6. Data gaps (what's missing and why it matters)
7. Assumptions register entries (for downstream ROI model)
8. Sources list (all URLs and documents referenced)

#### B. `bank_profile_roi_inputs.json` — Structured ROI Pre-fill

```json
{
  "bank_identity": {
    "name": "Official Bank Name",
    "country": "Country",
    "currency": "USD",
    "ticker": "TICK.ER",
    "report_year": 2024,
    "report_source": "Annual Report 2024"
  },
  "basic_information": {
    "total_customers": {
      "value": 500000,
      "source": "Annual Report 2024, p.12",
      "confidence": "HIGH"
    },
    "annual_revenue": {
      "value": 200000000,
      "source": "Income Statement, AR 2024 p.45",
      "confidence": "HIGH"
    },
    "operating_costs": {
      "value": 130000000,
      "source": "Income Statement, AR 2024 p.45",
      "confidence": "HIGH"
    },
    "cost_to_income_ratio": {
      "value": 0.65,
      "source": "Key Financial Highlights, AR 2024 p.3",
      "confidence": "HIGH"
    },
    "total_fte": {
      "value": 2000,
      "source": "HR Section, AR 2024 p.89",
      "confidence": "HIGH"
    },
    "average_fte_rate_hour": {
      "value": 18.75,
      "source": "DERIVED: Staff costs ($75M, p.45) / FTE (2000, p.89) / 2000hrs",
      "confidence": "MEDIUM",
      "derivation": "staff_costs / fte_count / 2000"
    },
    "average_revenue_per_customer": {
      "value": 400,
      "source": "DERIVED: Revenue ($200M) / Customers (500K)",
      "confidence": "MEDIUM",
      "derivation": "annual_revenue / total_customers"
    }
  },
  "additional_context": {
    "net_interest_income": {"value": null, "source": "..."},
    "total_assets": {"value": null, "source": "..."},
    "total_loans": {"value": null, "source": "..."},
    "total_deposits": {"value": null, "source": "..."},
    "num_branches": {"value": null, "source": "..."},
    "digital_active_users": {"value": null, "source": "..."},
    "npl_ratio": {"value": null, "source": "..."},
    "roe": {"value": null, "source": "..."},
    "car": {"value": null, "source": "..."}
  },
  "data_gaps": [
    {
      "metric": "metric_name",
      "priority": "HIGH|MEDIUM|LOW",
      "note": "Why it's missing and where to get it",
      "impact": "What ROI analysis this blocks"
    }
  ],
  "assumptions_register_entries": [
    {
      "id": "BP-1",
      "assumption": "Description",
      "value": "Formatted value",
      "confidence": "HIGH|MEDIUM|LOW",
      "source": "Source reference",
      "validation_owner": "Client (for confirmation)",
      "sensitivity": "HIGH|MEDIUM|LOW"
    }
  ]
}
```

## Integration with ROI Workflow

The output JSON is designed to feed directly into the ROI config:
1. Read `bank_profile_roi_inputs.json`
2. Use its `basic_information` values (with HIGH confidence) instead of LOW confidence estimates
3. Merge its `data_gaps` with the ROI model's data gaps
4. Merge its `assumptions_register_entries` into the ROI assumptions register

## Example

```
User: /profile-bank HNB Sri Lanka

[Step 2: WebSearch identifies Hatton National Bank PLC]