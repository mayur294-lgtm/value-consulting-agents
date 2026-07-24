# Ignite Workshop Synthesis — Golden Fixture (Synthetic)

> **House disclaimer:** This is a fully synthetic fixture built for the eval harness. "Meridian Mutual Bank," "Northland," all stakeholders, hypotheses, metrics, and evidence references below are fictional and were constructed to exercise the `ignite-workshop-synthesizer` scoring checks (`hypothesis_validation_statuses`, `usecase_candidates_present`, `usecase_classification_present`). Do not cite any figure or claim here in client-facing work.

## Engagement Context

**Client:** Meridian Mutual Bank (Northland region, retail banking)
**Workshops completed:** Strategy · Member Experience · Employee Experience · Architecture
**Purpose of this document:** Consolidate findings across all four workshops, validate or invalidate the pre-workshop hypotheses, and hand off a prioritized use-case candidate list to use-case design.

---

## 1. Hypothesis Validation Matrix

Each pre-workshop hypothesis is marked against workshop evidence using one of four statuses: **Confirmed**, **Partially Confirmed**, **Not Confirmed**, or **Needs More Data**.

| # | Hypothesis | Status | Evidence |
|---|------------|--------|----------|
| H1 | Northland members abandon digital account opening due to manual document upload steps | **Confirmed** | Member Experience workshop: 6 of 8 participants described re-uploading ID documents after a failed OCR check; branch staff corroborated a recurring "document reject" queue in Employee Experience workshop |
| H2 | Contact center staff lack a unified view of member accounts across deposit and lending systems | **Confirmed** | Employee Experience workshop: front-line staff demoed switching between 3 separate screens per call; Architecture workshop confirmed deposit core and loan origination system are not integrated at the data layer |
| H3 | Members would adopt a self-service loan modification flow if offered | **Partially Confirmed** | Member Experience workshop: strong interest expressed by 5 of 8 participants, but 3 flagged trust concerns about self-service for hardship-related changes; needs a hybrid (self-serve + advisor check-in) model, not pure self-service |
| H4 | Branch staff want AI-assisted next-best-action prompts during member conversations | **Not Confirmed** | Employee Experience workshop: staff explicitly pushed back, citing concern that scripted prompts would feel impersonal to long-tenured members; preference was for better account context, not recommendation prompts |
| H5 | Current core banking architecture can support real-time balance updates without a middleware layer | **Needs More Data** | Architecture workshop: core banking vendor confirmed batch settlement runs nightly; real-time feasibility depends on a vendor roadmap item not yet scheduled — follow-up call with vendor architecture team required before this can be scored |
| H6 | Small business members are underserved by the current digital channel relative to retail members | **Confirmed** | Strategy workshop: leadership cited small-business deposit growth trailing retail by 4 points over two years; Member Experience workshop found no small-business-specific onboarding path exists today |
| H7 | Employees believe the current employee desktop reduces, not increases, their capacity to serve members | **Partially Confirmed** | Employee Experience workshop: majority agreed the desktop is dated, but a minority (3 of 11) said the bigger blocker is training, not tooling — mixed causal read |

**Summary:** 3 Confirmed, 2 Partially Confirmed, 1 Not Confirmed, 1 Needs More Data (vendor follow-up required for H5 before Architecture can commit to a real-time roadmap position).

---

## 2. Prioritized Use Case Candidates

Each use case candidate below is classified as **Quick Win**, **Foundational**, **Transformational**, or **Defer**, based on member/employee value observed in workshops, evidence strength, and Architecture-confirmed feasibility.

### Quick Wins

- **Use case candidate: Document re-upload retry flow.** Fixes the specific failure point in H1 (OCR reject queue) without new integrations. Feasible within existing document capture vendor. Classification: **Quick Win**.
- **Use case candidate: Consolidated contact-center account summary panel.** Surfaces existing deposit + loan data behind one screen using read-only API calls, addressing H2 without requiring core replacement. Classification: **Quick Win**.

### Foundational

- **Use case candidate: Unified member data layer across deposit and lending systems.** Required precursor for H2 and any future real-time or cross-product use case; Architecture workshop flagged this as the dependency most other candidates sit behind. Classification: **Foundational**.
- **Use case candidate: Small-business digital onboarding path.** Addresses H6; requires new product configuration and a segment-specific journey, but no core system changes. Classification: **Foundational**.

### Transformational

- **Use case candidate: Hybrid self-service loan modification with advisor check-in.** Directly responds to the nuance in H3 — full automation was rejected by members, but a hybrid flow tests well. Requires new workflow orchestration and advisor queuing; largest scope of the candidate list. Classification: **Transformational**.
- **Use case candidate: Real-time balance and posting experience.** Would resolve the batch-settlement friction underlying several member complaints, but is gated entirely on H5 (vendor roadmap, Needs More Data). Classification: **Transformational**, contingent on the H5 follow-up.

### Defer

- **Use case candidate: AI-assisted next-best-action prompts for branch staff.** H4 was Not Confirmed — staff explicitly do not want this in its proposed form. Revisit only if a differently-scoped version (context surfacing rather than scripted prompts) is requested by staff. Classification: **Defer**.
- **Use case candidate: Employee desktop full rebuild.** H7 was only Partially Confirmed and the causal driver (tooling vs. training) is unresolved; a full rebuild is premature until that's disambiguated. Classification: **Defer**.

---

## 3. Handoff Notes

- H5 (real-time architecture feasibility) needs a vendor follow-up before the Transformational-tier "real-time balance" candidate can be scoped with confidence — flagged to the consultant, not assumed resolved.
- H7's mixed read (tooling vs. training) should be tested with a short follow-up survey before committing to the deferred desktop rebuild.
- All Quick Win and Foundational candidates are ready to proceed to use-case design; Transformational candidates proceed pending the H5 data gap.
