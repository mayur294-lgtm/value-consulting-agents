# Multi-Country Rollout Engagement Framework

## Overview

Multi-country rollouts are a specialized engagement type where a banking group implements Backbase across multiple countries/subsidiaries. This framework provides guidance on assessment, planning, and execution patterns specific to this engagement type.

**IMPORTANT:** This framework should ONLY be applied when the engagement explicitly involves multiple countries or subsidiaries. Do NOT assume multi-country patterns for standard single-entity implementations.

---

## When to Apply This Framework

### Qualifying Triggers (ALL must be present)

1. **Multiple Legal Entities**: Client has banking operations in 2+ countries/regions
2. **Shared Platform Intent**: Client wants to reuse components across entities
3. **Centralized Decision Making**: Group-level technology/digital strategy exists
4. **Explicit Multi-Country Scope**: Client has stated intent for regional/global rollout

### NOT Multi-Country Engagements

- Single country with multiple branches (use standard retail engagement)
- Single entity serving cross-border customers (use standard engagement)
- Client considering future expansion but only implementing one country now
- Regional bank with operations in multiple states (same regulatory environment)

---

## Engagement Phases

### Phase 0: Multi-Country Assessment

**Purpose:** Determine if multi-country approach is viable and valuable

**Key Questions:**
- What is the regulatory overlap across target countries?
- What is the core banking system landscape (same/different across countries)?
- What is the customer journey similarity across countries?
- What is the timeline for subsequent country rollouts?

**Output:** Multi-Country Viability Assessment

---

### Phase 1: Inception & Country 1 Foundation

**Duration:** 1-2 months (depending on complexity)

**Objectives:**
- Establish platform architecture for reusability
- Define component categorization framework
- Set up shared services foundation
- Begin Country 1 requirements

**Team Composition (Typical):**

| Role | FTE | Day Rate Range | Notes |
|------|-----|----------------|-------|
| PM | 1.0 | $800-1000 | Program-level coordination |
| BA/PO | 1.0 | $800-1000 | Cross-country requirements |
| Solution Architect | 1.0 | $900-1100 | Platform architecture |
| UX Designer | 1.0 | $500-700 | Design system foundation |
| Backend Developer | 0.5 | $500-700 | API standards |
| Frontend Developer | 0.5 | $500-700 | Component library |
| QA | 0.5 | $500-700 | Test framework |
| DevOps | 0.5 | $500-700 | CI/CD foundation |

---

### Phase 2: Country 1 Go-Live + Platform Hardening

**Duration:** 6-12 months (varies by scope)

**Objectives:**
- Complete Country 1 implementation
- Identify and abstract reusable components
- Document country-specific variations
- Build reusability assessment

**Team Composition (Typical):**

| Role | BB FTE | Client FTE | Notes |
|------|--------|------------|-------|
| PM | 1.0 | 0-1 | Delivery management |
| BA/PO | 1.0 | 1.0 | Requirements & prioritization |
| Solution Architect | 1.0 | 1.0 | Technical decisions |
| UX Designer | 1.0 | 0-1 | Country-specific UX |
| Backend Developer | 2.0 | 1.0 | Integration heavy |
| Web Developer | 1.0 | 1.0 | Web banking |
| iOS Developer | 1.0 | 1.0 | Mobile banking |
| Android Developer | 1.0 | 1.0 | Mobile banking |
| QA | 2.0 | 1.0 | Comprehensive testing |
| DevOps | 0.5 | 1.0 | Environment management |

---

### Phase 3: Country Platform Readiness

**Duration:** 6-18 months (parallel with Phase 2 or sequential)

**Objectives:**
- Abstract country-specific logic into configuration
- Build country deployment templates
- Create country onboarding playbook
- Validate reusability with Country 2 requirements

**Key Deliverables:**
- Component Reusability Matrix (see below)
- Country Deployment Template
- Country Onboarding Checklist
- Configuration Guide per Journey

---

### Phase 4: Country N Rollouts

**Duration:** 1-3 months per country (after first country)

**Objectives:**
- Configure platform for new country
- Implement country-specific integrations
- Localize and test
- Go-live with support

**Team Composition (Significantly reduced):**

| Role | BB FTE | Client FTE | Notes |
|------|--------|------------|-------|
| PM | 0.5-1.0 | 0-1 | Coordination |
| BA/PO | 0-0.5 | 1.0 | Local requirements |
| Solution Architect | 0.5-1.0 | 1.0 | Integration design |
| Backend Developer | 1.0 | 1.0 | Country integrations |
| Frontend Developer | 0.5-1.0 | 1.0 | Localization |
| QA | 1.0-2.0 | 1.0 | Country testing |
| DevOps | 0.5 | 1.0 | Deployment |

**Key Value Proposition:** Each subsequent country costs 30-50% of the first country due to reusability.

---

## Component Reusability Assessment

### Categorization Framework

| Category | Definition | Reusability | Example |
|----------|------------|-------------|---------|
| **OOTB (No Custom)** | Standard Backbase component, no modifications | 100% | Account statements, Card management |
| **Extended** | Backbase component with client customizations | 80-95% | Custom dashboard, Modified payments |
| **Custom** | Net-new component built for client | 50-80% | Country-specific tax payments |
| **Country-Specific** | Component unique to one country's regulations | 0-30% | Local instant payment scheme |

### Assessment Matrix Template

| Component/Journey | Country 1 Status | Reusable for Others? | Country-Specific Notes |
|-------------------|------------------|---------------------|----------------------|
| Account Overview | OOTB | Yes | - |
| Domestic Payments | Extended | Yes | Payment scheme varies |
| Tax Payments | Custom | Partial | Regulatory differences |
| Mobile Money | Custom | Yes (Africa) | Scheme-specific |
| Instant Payments | Extended | No | Different rails per country |

### Common Country-Specific Variations

1. **Instant Payment Schemes**: Different rails per country (e.g., Pesalink in Kenya, TIPS in Tanzania)
2. **Tax Integration**: Country-specific tax authority systems
3. **Mobile Money**: Varies by market (M-Pesa, MTN Mobile Money, etc.)
4. **KYC/AML Requirements**: Regulatory variations
5. **Currency & FX**: Multi-currency handling, exchange rate sources

---

## Implementation Effort Benchmarks

### Journey-Level Sizing

| Journey | Size | Min Days | Max Days | Notes |
|---------|------|----------|----------|-------|
| App Foundations | XS | 1 | 2 | Platform setup |
| Landing Page | XS | 1 | 2 | Standard |
| New User Registration | M | 5 | 10 | KYC integration varies |
| Authentication | L | 10 | 20 | Security requirements vary |
| Dashboard | L | 10 | 20 | Customization level varies |
| CASA/Deposits Overview | L | 10 | 20 | Core integration |
| Card Management | S | 3 | 5 | Processor integration |
| Domestic Payments | XL | 20 | 40 | Payment scheme complexity |
| International Payments | L | 10 | 20 | SWIFT/correspondent |
| Bill Payments | XL | 20 | 40 | Biller ecosystem |
| Mobile Payments | L | 10 | 20 | Mobile money integration |
| Loan Origination | M | 5 | 10 | Decisioning integration |
| Profile/Settings | S | 3 | 5 | Standard |
| Notifications | M | 5 | 10 | Channel preferences |

### Sizing Key

| Size | Days | Duration Equivalent |
|------|------|---------------------|
| XS | 1-2 | 1-2 days |
| S | 3-5 | 3-5 days |
| M | 5-10 | 1-2 weeks |
| L | 10-20 | 2-4 weeks |
| XL | 20-40 | 1-2 months |
| XXL | 40-60 | 2-3 months |

---

## Cost Model Framework

### Day Rate Ranges by Role (USD)

| Role | Junior | Mid | Senior | Lead |
|------|--------|-----|--------|------|
| Project Manager | $700 | $850 | $950 | $1,100 |
| Business Analyst | $600 | $750 | $900 | $1,000 |
| Solution Architect | $800 | $950 | $1,100 | $1,300 |
| UX Designer | $500 | $600 | $700 | $850 |
| Developer (any stack) | $500 | $600 | $700 | $850 |
| QA Engineer | $450 | $550 | $650 | $750 |
| DevOps Engineer | $550 | $650 | $750 | $900 |

*Rates vary by region. Adjust for local market conditions.*

### Typical Multi-Country Investment Pattern

| Phase | % of Total Investment | Cumulative |
|-------|----------------------|------------|
| Inception | 3-5% | 3-5% |
| Country 1 + Platform | 40-50% | 45-55% |
| Platform Readiness | 25-35% | 75-85% |
| Country 2 | 8-12% | 85-95% |
| Country 3+ | 5-8% each | - |

---

## Value Proposition for Multi-Country

### Cost Efficiency

| Scenario | Investment Pattern | Notes |
|----------|-------------------|-------|
| 5 Countries (Sequential) | 100% + 35% + 30% + 25% + 25% = 215% | vs. 500% if done independently |
| 5 Countries (Aggressive Reuse) | 100% + 25% + 20% + 20% + 20% = 185% | High platform investment |

### Time to Market

- **Country 1:** 12-18 months (full implementation)
- **Country 2:** 3-6 months (with platform readiness)
- **Country 3+:** 2-4 months (optimized playbook)

### Quality Benefits

- Consistent customer experience across countries
- Shared security standards and certifications
- Centralized support and maintenance
- Common upgrade path

---

## Risk Factors

### High Risk Indicators

1. **Divergent Core Banking Systems**: Each country on different CBS requires more integration work
2. **Regulatory Fragmentation**: Countries with very different banking regulations
3. **Timeline Pressure**: Countries demanding simultaneous go-lives
4. **Organizational Silos**: Country teams not aligned on shared platform

### Mitigation Strategies

1. Start with countries sharing same CBS or similar integration patterns
2. Engage regulators early for compliance clarity
3. Stagger go-lives with 2-3 month gaps minimum
4. Establish cross-country governance from Day 1

---

## Source Reference

This framework is derived from multi-country implementation experience including:
- East African banking group rollouts
- Multi-subsidiary wealth management implementations
- Regional retail banking transformations

The specific metrics and benchmarks have been generalized for broad applicability. Adjust based on actual client context.
