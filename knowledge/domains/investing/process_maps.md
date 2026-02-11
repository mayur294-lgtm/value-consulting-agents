# Investing Domain Process Maps

## Status: Skeleton

Process maps for investing are structured but awaiting engagement data for specific time-per-step, system-per-step, and cost-per-step detail. These skeletons will be populated after the first engagement workshops.

---

## Process 1: Investment Account Opening (Bank-Led Model)

### Current State (Typical)
```
Banking Client → Awareness (website/branch) → Navigate to investing →
Re-enter personal info → Suitability questionnaire (paper or basic digital) →
KYC review (manual) → Compliance review → Account approval (1-3 days) →
Funding (ACH 3-5 days) → Account active (total: 5-10 days)
```

### Friction Points (to be validated in workshop)
- [ ] Re-entry of banking data already on file
- [ ] Suitability questionnaire completion rate
- [ ] KYC manual review bottleneck
- [ ] Funding delay (ACH settlement)
- [ ] Drop-off between approval and funding

### Target State (Backbase)
```
Banking Client → In-app prompt (NBA) → Pre-populated application →
Conversational suitability → eIDV (real-time) → Auto-approval (STP) →
Instant funding from linked account → Account active + first investment prompt
(total: <15 minutes)
```

---

## Process 2: Investment Account Opening (Pure Investing Provider)

### Current State (Typical)
```
Prospect → Website/app → Account type selection → Personal info entry →
Suitability questionnaire → Identity verification → Compliance review →
Account approval → Bank account linking → ACH funding → Account active
```

### Target State (Backbase)
```
Prospect → App download → Guided account selection → Personal info →
Conversational suitability → eIDV (real-time) → Auto-approval →
Instant deposit → Account active + guided first investment
```

---

## Process 3: ACAT Transfer-In

### Current State (Typical)
```
Investor decides to transfer → Finds ACAT form (if they know it exists) →
Manual entry of delivering firm details → Paper/digital submission →
NSCC/ACATS processing (3-6 business days) → Assets appear (no notification) →
Investor calls to confirm → Manual portfolio review
```

### Target State (Backbase)
```
Proactive "consolidate" prompt → Firm lookup (auto-populate DTC/details) →
Guided transfer type selection → Digital submission →
Real-time status tracking → Completion notification →
Automated portfolio analysis + rebalancing recommendations
```

---

## Process 4: Advisor-Assisted Onboarding (Hybrid Model)

### Current State (Typical)
```
Advisor identifies prospect → Manual fact-finding (paper/Excel) →
Advisor fills application on behalf → Compliance review →
Client signs (wet signature or separate eSign) → Account setup →
Advisor calls client to confirm → Follow-up for funding
```

### Target State (Backbase)
```
Digital Assist: Advisor initiates → Pre-populated from Client 360 →
Client completes suitability digitally (link sent) → eSignature →
Auto-compliance check → STP approval → Client funds via app →
Advisor notified of completion
```

---

## Process 5: Robo-Advisory Onboarding

### Current State (Typical)
```
Self-directed investor → Finds robo product (marketing email or website) →
Separate application → Re-do suitability → Fee disclosure →
Fund transfer from self-directed to managed → Wait for allocation →
First rebalance (manual or delayed)
```

### Target State (Backbase)
```
In-app contextual prompt ("Automate your investing?") →
Suitability carry-forward (update only if changed) →
Portfolio preview + fee transparency → One-click enrollment →
Seamless in-platform transfer → Immediate allocation →
Automated rebalancing from day 1
```

---

## Workshop Data Collection Template

When running workshops, collect the following for each process:

| Data Point | What to Capture |
|------------|-----------------|
| **Steps** | Number of discrete steps end-to-end |
| **Time per step** | Minutes/hours/days at each step |
| **Systems per step** | Which systems are touched |
| **Actors per step** | Who does what (investor, advisor, ops, compliance) |
| **Handoffs** | Where does work pass between people/systems |
| **Drop-off points** | Where do investors abandon or delay |
| **Exceptions** | What triggers manual intervention |
| **Volume** | How many times per month/year does this process run |
| **Cost** | Cost per execution (labor + system + third-party) |

---

*Last Updated: 2026-02-09*
*Status: Skeleton — ready for engagement workshop data*
