# Findings Backlog

Small issues parked by reviews and audits; `/bb-prd` Phase 0.2 offers these at the start of each cycle. Mark `[done vN]` when folded into a PRD.

## From the PR #153 review (2026-08-19)

- [ ] knowledge/domains/pricing/pricing-methodology.md:34 — 7+ citations across pricing-model.md/pricing-methodology.md/negotiation-tactics.md/pricing_model.py point at nonexistent `knowledge/product/banking-os.md` §10 (real: knowledge/banking_os.md, conversational content is §6/conversational_banking.md); plus dead fork-era provenance paths (pipeline_gaps/*, gtm-os-proposal-builder/) (from PR #153 review)
- [ ] tools/proposal_builder.py:200 — ladder_position documented as engine stage keys (anchor/counter1/…) but strategy.json ladder rows carry only display names; emit "key" per row (additive) (from PR #153 review)
- [ ] templates/proposal-longform/template.html:357 — template demo fails the proposal rubric (3 scenario cards, no data-scenario attrs, no deal-type meta); conventions documented only in the rubric docstring — add markers + document in authoring-guide.md (from PR #153 review)
- [ ] templates/proposal-longform/authoring-guide.md:17 — canonical tokens source named as knowledge/design-system/frontline-tokens.json (nonexistent); real: presentations/frontline-2026/design-tokens.json (from PR #153 review)
- [ ] .claude/commands/proposal-builder.md:552 — zip-packaging paragraph inserted mid-table breaks GFM rendering of the ACT 4 output rows (incl. the Audience:Internal column); move below the table (from PR #153 review)
- [ ] evals/rubrics/deliverable/proposal.py:283 — bilingual detection requires literal lang="ar"; lang="ar-SA" fails open (Arabic disclaimer check silently skipped); detect Arabic-script chars instead (from PR #153 review)
- [ ] tools/pricing_model.py:205 — pof_backsolve discount unclamped; mistyped target yields >100% discount / negative uplift rows silently; add guard (from PR #153 review)
- [ ] tools/pricing_model.py:1 — zero CI wiring for the pricing engine (no registry row, no selftest in evals.yml); root enabler of shipped math bugs; add components.pricing-model row + selftest call (from PR #153 review)
- [ ] .prd/prd-v5.md:83 — "Schroders Q-06367" pairs a real client with a real deal ID; genericize the ID (client names in planning docs are repo norm; the deal-ID pairing is the elevated-sensitivity element) (from PR #153 review)
