# Benchmark Shortlist — Meridian Mutual Bank (Northland Retail Banking)

> **House disclaimer:** This shortlist is a fully synthetic golden fixture used
> to test the `benchmark-librarian` eval rubric. "Meridian Mutual Bank" and all
> figures below are fictional. No real client, institution, or engagement data
> is represented. Every benchmark carries an explicit confidence level and a
> bracketed provenance tag per the Value Consulting evidence-sourcing standard —
> do not cite these numbers outside of eval fixtures.

## Purpose

Meridian Mutual Bank (retail banking, Northland region, ~$4.1B assets) needs a
defensible benchmark set to support the ROI model's digital onboarding and
contact-center deflection levers. This shortlist was curated against Northland
regional peers and, where regional data was thin, cross-industry proxies. Each
row states its match type and confidence so the ROI modeler can weight it
appropriately.

## Shortlist

| # | Metric | Benchmark Value | Peer Set | Match Type | Confidence Level | Provenance |
|---|--------|------------------|----------|------------|-------------------|------------|
| 1 | Digital account opening completion rate | 68% | Northland regional mutuals, $2-6B assets | Direct peer | High confidence | [annual report — Northland Mutual Holdings FY2025, p.34] |
| 2 | Average time-to-fund new checking account | 6.2 minutes | Northland regional mutuals, $2-6B assets | Direct peer | High confidence | [annual report — Northland Mutual Holdings FY2025, p.35] |
| 3 | Contact-center cost per inbound call | $4.85 | US regional/community banks, $1-10B assets | Adjacent proxy | Medium confidence | [investor presentation — Q3 2025 Community Banking Investor Day] |
| 4 | First-call resolution rate | 74% | US regional/community banks, $1-10B assets | Adjacent proxy | Medium confidence | [investor presentation — Q3 2025 Community Banking Investor Day] |
| 5 | Core deposit attrition (annual) | 9.1% | Northland credit unions and mutuals | Direct peer | Medium confidence | [regulator — Northland Financial Authority Sector Statistics 2025] |
| 6 | Digital-channel share of total transactions | 71% | Northland regional mutuals, $2-6B assets | Direct peer | High confidence | [annual report — Northland Mutual Holdings FY2025, p.41] |
| 7 | Mobile app rating (store average) | 4.1 / 5.0 | Northland regional mutuals | Direct peer | Medium confidence | [industry — Northland App Store Banking Category Review 2025] |
| 8 | Cost-to-income ratio | 58% | Northland regional mutuals, $2-6B assets | Direct peer | High confidence | [annual report — Northland Mutual Holdings FY2025, p.12] |
| 9 | Net promoter score, retail banking | +22 | Global retail banking, cross-industry | Cross-industry proxy | Low confidence | [industry — Global Retail Banking Experience Index 2025] |
| 10 | Loan origination cycle time (personal loans) | 3.4 days | US regional/community banks, $1-10B assets | Adjacent proxy | Medium confidence | [investor presentation — Q3 2025 Community Banking Investor Day] |
| 11 | Call-deflection rate from self-service digital tools | 31% | Not available for Northland peer set; estimated from adjacent proxy | Estimated proxy | Low confidence | [estimated — derived from item 3 and 10 using Meridian's stated call-volume baseline; not independently sourced] |
| 12 | Branch transaction volume decline (YoY) | -14% | Northland regional mutuals, $2-6B assets | Direct peer | Medium confidence | [consultant-provided — Meridian Mutual Bank management discussion, discovery session 2, not independently verified] |

## Confidence rationale

- **High confidence** rows (1, 2, 6, 8) come directly from a named Northland
  peer holding company's own published annual report, matched on asset size
  and geography — the closest possible match type.
- **Medium confidence** rows (3, 4, 5, 7, 10, 12) either widen the peer set to
  US regional/community banks generally (asset-size match but not geography),
  or rely on a single client-management data point that has not been
  independently verified against a third-party source.
- **Low confidence** rows (9, 11) are the weakest links in this shortlist: row
  9 is a cross-industry global proxy with no Northland or US regional anchor,
  and row 11 is an estimated figure derived algebraically from two other
  benchmarks rather than observed directly — flag both for validation before
  they carry any load-bearing weight in the ROI model.

## Gaps and validation asks

- No first-party Northland source was found for call-deflection rate (row 11)
  or retail NPS (row 9). Both should be validated with Meridian's own contact
  center analytics before use in a client-facing deliverable.
- Regulator-sourced attrition data (row 5) is sector-wide, not segmented by
  asset size — treat as directional only.
- One candidate metric from the initial search was excluded as synthetic
  pipeline-test data before this shortlist was compiled.

Note: 1 synthetic-test entry excluded — fabricated pipeline-test data, never citable in client work (see knowledge/standards/benchmark_evolution.md).
