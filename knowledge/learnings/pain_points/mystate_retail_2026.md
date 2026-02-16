# Pain Point Harvest — MyState Retail Assessment 2026

> Auto-harvested from engagement: 2026-02_retail_assessment

### Digital Onboarding Funnel Leakage — Retail / APAC

- **Pattern:** High digital application start volume with catastrophic drop-off — 77% of digital starts fail to convert to opened accounts.
- **Business Impact:** Revenue loss — estimated AUD 15.2M in potential lifetime customer value lost annually. 17,412 potential customers lost per year.
- **Frequency:** 2 (also seen in Credins Bank EMEA)
- **Severity Range:** HIGH
- **Typical Evidence:** Digital application funnel analytics, page-level conversion data, ID verification pass rates
- **Last Seen:** 2026-02-16
- **Engagement IDs:** 153681f5-e8aa-40db-b9c9-6d698d63b812
- **Notes:** Root causes: no save-and-resume (40-50% drop at initial steps), single-provider eIDV with 30% failure, no progress indicators. Especially critical for banks with remote/mainland customer acquisition.

### Zero Digital Self-Service Capability — Retail / APAC

- **Pattern:** Every routine servicing task (balance, transfers, password reset, statements) requires human interaction — zero digital containment.
- **Business Impact:** Cost increase — 94 FTEs handling tasks that are 50-80% self-service candidates at digital-first peers. Estimated AUD 668K/year in avoidable servicing cost.
- **Frequency:** 1
- **Severity Range:** HIGH
- **Typical Evidence:** Servicing task inventory with time estimates, FTE counts, channel distribution
- **Last Seen:** 2026-02-16
- **Engagement IDs:** 153681f5-e8aa-40db-b9c9-6d698d63b812
- **Notes:** Common in building society heritage banks. Balance enquiry takes 5 minutes across 2 systems vs. instant in-app at digital-first peers.

### Absent Middle Layer (No Orchestration) — Retail / APAC

- **Pattern:** Core banking data exists (Back layer) and some front-end exists, but zero orchestration, workflow, or business rules engine in the Middle layer.
- **Business Impact:** All processes are manual; no STP; no automated routing; 25% manual error rate; dual audit on 100% of applications.
- **Frequency:** 1
- **Severity Range:** HIGH
- **Typical Evidence:** Capability assessment showing Middle layer at 0 across all capabilities; manual audit processes described
- **Last Seen:** 2026-02-16
- **Engagement IDs:** 153681f5-e8aa-40db-b9c9-6d698d63b812
- **Notes:** This is the structural root cause of all other symptoms. 0/15 capabilities had any Middle layer orchestration. Typical of banks running legacy core without middleware modernization.

### Single-Provider ID Verification Dependency — Retail / APAC

- **Pattern:** Single identity verification provider (Equifax) with 30% failure rate and no fallback routing.
- **Business Impact:** Digital conversion ceiling — 10% of digital funnel drops at ID check. Joint account flows are broken (same person as primary and secondary).
- **Frequency:** 1
- **Severity Range:** HIGH
- **Typical Evidence:** ID verification pass/fail rates, digital ID link statistics, provider failure breakdown
- **Last Seen:** 2026-02-16
- **Engagement IDs:** 153681f5-e8aa-40db-b9c9-6d698d63b812
- **Notes:** Multi-provider eKYC with automated fallback (Jumio/Onfido primary, Equifax secondary) is the standard recommendation.

### Mainland Customer Growth Without Digital Infrastructure — Retail / APAC

- **Pattern:** Majority of new customers (60%) come from geographic regions where branches don't exist, but digital channels are broken.
- **Business Impact:** Revenue loss — non-branch customers have no viable onboarding path with 77% digital leakage. Growth strategy misaligned with digital capability.
- **Frequency:** 1
- **Severity Range:** HIGH
- **Typical Evidence:** Customer acquisition geography data, channel distribution for account opens
- **Last Seen:** 2026-02-16
- **Engagement IDs:** 153681f5-e8aa-40db-b9c9-6d698d63b812
- **Notes:** Specific to banks expanding beyond their branch footprint (e.g., Tasmanian bank acquiring mainland Australian customers). Pattern may apply to any bank with remote/digital-only customer segments.
