# Findings Backlog

Plain notes — small issues parked by past reviews that weren't worth a full plan. Append-only, non-versioned. A future `/bb-prd` folds in anything still relevant (rewriting `- [ ]` to `- [done vN]`).

- [ ] evals/registry.yaml:critty,critical-thought-partner — No negative/stripped fixture proves the checks discriminate; add a WITH/WITHOUT fixture pair (like roi-excel-generator) or an inline assertion that evaluate() on a stripped copy scores <0.80 (from PR #97 review)
- [ ] CLAUDE.md:142 — CTP suppression summary drops "low confidence AND" from standard rule S4 ("Low confidence AND low impact"); the self-sufficient CLAUDE.md section applies a looser suppression rule than the standard (from PR #97 review)
