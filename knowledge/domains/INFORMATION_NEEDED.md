# Backbase Information Needed to Train Domain Knowledge

This document outlines the Backbase-specific information required to populate the domain knowledge base for value consulting.

---

## 1. BENCHMARKS (All Domains)

**Source:** Consulting Playbook CSV already provides customer data. Additional needs:

### What's Available
- Customer-specific metrics from implementations (Tech CU, Sandy Spring, EWB, Pichincha, BSF, etc.)
- Journey-based KPIs (Onboarding, Loan Origination, Cards, Payments)

### What's Needed
- [ ] **Benchmark Ranges:** Official Backbase definitions for Poor/Average/Good/Best-in-Class thresholds
- [ ] **Industry Benchmarks:** Third-party benchmark sources Backbase references (Gartner, Forrester, regional banking associations)
- [ ] **Wealth Management Benchmarks:** Limited coverage in CSV - need wealth-specific KPIs
- [ ] **Commercial/Corporate Benchmarks:** Limited coverage - need treasury, trade finance, payments KPIs

---

## 2. RETAIL BANKING

### Use Cases (`retail/use_cases.md`)
- [ ] **Backbase Retail Product Capabilities:** Complete list of retail banking capabilities with:
  - Feature descriptions
  - API/integration points
  - Demo availability
  - Customer references

- [ ] **Use Case Prioritization:** Which use cases are:
  - Quick wins (commonly implemented first)
  - High ROI drivers
  - Differentiators vs competition

### Journey Maps (`retail/journey_maps.md`)
- [ ] **Backbase Journey Blueprints:** Standard journey designs for:
  - Account opening (current account, savings)
  - Card application
  - Personal loan
  - Mortgage pre-qualification
  - Onboarding to engagement

### Value Propositions (`retail/value_propositions.md`)
- [ ] **Customer Success Stories:** Retail banking wins with:
  - Customer name (or anonymized reference)
  - Before/after metrics
  - Implementation timeline
  - Key capabilities deployed

- [ ] **Competitive Differentiation:** How Backbase positions against:
  - Temenos Infinity
  - FIS Digital One
  - Finastra Fusion
  - Build in-house
  - Neobank platforms

### Personas (`retail/personas.md`)
- [ ] **Backbase Persona Research:** Any existing persona definitions used in:
  - Product design
  - Marketing
  - Demo scripts

---

## 3. COMMERCIAL BANKING

### Use Cases (`commercial/use_cases.md`)
- [ ] **Backbase Business Banking Capabilities:** Complete list with:
  - Cash management features
  - Payment initiation & approval workflows
  - User administration & entitlements
  - Trade finance (if applicable)
  - ERP integration capabilities

### Journey Maps (`commercial/journey_maps.md`)
- [ ] **Commercial Client Journey Blueprints:**
  - Client onboarding flow
  - User provisioning
  - Payment approval workflows
  - Cash position management

### Value Propositions (`commercial/value_propositions.md`)
- [ ] **Commercial Banking Customer Stories:** Wins with metrics
- [ ] **Competitive Positioning:** vs Finastra, Bottomline, Kyriba, CGI, etc.

---

## 4. SME BANKING

### Use Cases (`sme/use_cases.md`)
- [ ] **Backbase SME/Business Banking Capabilities:**
  - Digital account opening for businesses
  - SME lending (if applicable)
  - Cash flow tools
  - Multi-user access & approvals
  - Accounting integrations

### Journey Maps (`sme/journey_maps.md`)
- [ ] **SME Journey Blueprints:**
  - Business account opening
  - SME loan application
  - Daily banking operations

### Value Propositions (`sme/value_propositions.md`)
- [ ] **SME Customer Stories:** Especially vs neobank competition
- [ ] **Competitive Positioning:** vs Tide, Mercury, neobanks, core vendor solutions

---

## 5. WEALTH MANAGEMENT

### Benchmarks (`wealth/benchmarks.md`)
- [ ] **Wealth-Specific KPIs:** Need complete benchmark set for:
  - Advisor productivity metrics
  - AUM per advisor ranges
  - Digital engagement benchmarks
  - Client retention benchmarks
  - Onboarding time benchmarks

### Use Cases (`wealth/use_cases.md`)
- [ ] **Backbase Wealth Management Capabilities:**
  - Client onboarding
  - Portfolio view & reporting
  - Advisor workstation features
  - Client portal features
  - Goal-based planning
  - Secure messaging/collaboration

### Journey Maps (`wealth/journey_maps.md`)
- [ ] **Wealth Journey Blueprints:**
  - Client onboarding (HNW vs mass affluent)
  - Portfolio review meeting
  - Investment proposal
  - Self-service investing

### Value Propositions (`wealth/value_propositions.md`)
- [ ] **Wealth Customer Stories:** Advisor productivity gains, client satisfaction
- [ ] **Competitive Positioning:** vs Envestnet, SS&C, Temenos WealthSuite, etc.

---

## 6. CORPORATE BANKING

### Benchmarks (`corporate/benchmarks.md`)
- [ ] **Corporate/Treasury KPIs:** Need benchmarks for:
  - Payment STP rates
  - Onboarding time (large corporates)
  - API adoption metrics
  - Treasury visibility metrics

### Use Cases (`corporate/use_cases.md`)
- [ ] **Backbase Corporate Banking Capabilities:**
  - Global cash visibility
  - Multi-bank aggregation
  - Complex approval workflows
  - Trade finance capabilities
  - API/host-to-host connectivity
  - ERP/TMS integration

### Journey Maps (`corporate/journey_maps.md`)
- [ ] **Corporate Journey Blueprints:**
  - Corporate client onboarding
  - High-value payment journey
  - Cash position management
  - Trade document processing

### Value Propositions (`corporate/value_propositions.md`)
- [ ] **Corporate Customer Stories**
- [ ] **Competitive Positioning:** vs Finastra, TIS, global bank proprietary solutions

---

## 7. CROSS-DOMAIN NEEDS

### Pain Points (All Domains)
- [ ] **Discovery Question Bank:** Standard questions used in Backbase discovery workshops
- [ ] **Common Pain Point Themes:** From actual engagements - what do banks say most?

### Objection Handling (All Domains)
- [ ] **Sales Objection Library:** Common objections and approved responses for:
  - "We're building in-house"
  - "Too expensive"
  - "Our core vendor has this"
  - "We've already invested in X"
  - Domain-specific objections

### Reference Customers
- [ ] **Referenceable Customers by Domain:** Which customers can be named/referenced?
- [ ] **Case Studies:** Published or internal case studies with metrics

### Competitive Intelligence
- [ ] **Competitor Comparison Sheets:** Official Backbase positioning vs key competitors by domain

---

## Priority Order for Population

### Phase 1 - High Impact (Immediate)
1. Retail benchmarks ranges + customer stories
2. Retail use cases with Backbase capability mapping
3. Discovery question bank (cross-domain)

### Phase 2 - Expand Coverage
4. SME use cases and journeys
5. Commercial use cases and journeys
6. Objection handling library

### Phase 3 - Complete Coverage
7. Wealth domain (needs most content)
8. Corporate domain
9. Competitive positioning per domain

---

## Format for Providing Information

When providing information, please use this format:

```markdown
## [Domain] - [Section]

### [Topic/Item]
**Description:** ...
**Backbase Capability:** ...
**Value/Metrics:** ...
**Customer Reference:** ...
```

Or provide:
- Links to internal documentation
- Existing presentations/decks
- Customer case studies
- Product specification documents
- Demo scripts
