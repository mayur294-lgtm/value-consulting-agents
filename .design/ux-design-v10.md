---
version: 10
prd: prd-v10.md
status: draft
date: 2026-08-28
author: Mariam Tahir
previous: ux-design-v8.md
---

# UX Design v10 — Multilingual PII Detection (Latin-script)

> **Numbering.** v9 is skipped in `.design/` for the same reason it is skipped in
> `.prd/`: `prd-v9.md` exists uncommitted in the `proposal-builder` worktree.
> Design and PRD numbers stay aligned, as they have since v6.

The "user" here is a consultant, and the surface is command output, hook
messages and a profile field — not screens. Every message below is the literal
text, not a description of one.

## User Flows

### Flow A — Declaring the language at engagement init

```
./scripts/init_engagement.sh acme_bank 2026-09_retail_assessment assessment
   │
   ├── --language given? ──yes──▶ use it ──────────────────┐
   │        │                                              │
   │        no                                             │
   │        ▼                                              │
   │   stdin a TTY? ──no──▶ default `en`, print:           │
   │        │               "No --language given and not   │
   │        │                interactive — defaulting to   │
   │        │                English (en)."                │
   │        │                                              │
   │       yes                                             │
   │        ▼                                              │
   │   PROMPT:                                             │
   │   "What language are this engagement's source          │
   │    documents in? [en]                                  │
   │     verified:    en, fr, es                            │
   │     provisional: (none)                                │
   │    Enter a code, or press Return for English."         │
   │        │                                              │
   │        ▼                                              │
   └────────┴──────────────────────────────────────────────┘
                          │
                          ▼
              validate against the language registry
                          │
        ┌─────────────────┼──────────────────┬──────────────────┐
        ▼                 ▼                  ▼                  ▼
    verified         provisional        not registered      non-Latin script
        │                 │                  │                  │
        ▼                 ▼                  ▼                  ▼
  write to          write + WARN       REFUSE, offer      REFUSE, explain
  CLIENT_PROFILE    (Flow D)           /pii-add-language  (see E4)
        │
        ▼
  model already installed? ──no──▶ fetch pinned wheel (Flow B)
        │
        ▼
  engagement created
```

The flag always wins. This keeps `init_engagement.sh` scriptable — it has no
interactive `read` today and is exercised by the `engagement_identity` eval row,
so a prompt that blocks unconditionally would break automation.

### Flow B — First install of a language model

```
Language `fr` selected. Checking for its detection model...
   │
   ├── already installed ──▶ "Model fr_core_news_lg already present." ──▶ done
   │
   └── missing
        │
        ▼
   "Installing the French detection model (fr_core_news_lg, ~450 MB).
    This happens once per language on this machine."
        │
        ├── success ──▶ "[OK] Model installed and loads." ──▶ done
        │
        ├── offline / network failure ──▶ E2
        │
        └── no pinned wheel registered for `fr` ──▶ E3
```

Fetch happens at engagement init, never mid-scan, so a consultant never
discovers a 450 MB download while waiting on a document.

### Flow C — Onboarding a language nobody has measured

```
/pii-add-language da
   │
   ▼
1. Script guard — is `da` Latin script?
   └── no ──▶ E4 (refuse)
   │
   ▼
2. Is a pinned model registered for `da`?
   └── no ──▶ E3 (refuse; print the model name and how to pin it)
   │
   ▼
3. Does knowledge/languages/da.yaml exist?
   │
   ├── no ──▶ scaffold it and STOP:
   │          "I've written a starter pack to
   │           knowledge/languages/da.yaml. It needs three things
   │           only a Danish speaker can supply:
   │             · 30 person names as they'd be written in a document
   │             · 5 short sentences per document shape (5 shapes)
   │             · generic words that must NEVER be redacted
   │               (the Danish equivalents of 'bank', 'credit union')
   │           Fill it in and run /pii-add-language da again."
   │
   └── yes ──▶ continue
   │
   ▼
4. Synthesise the five D10 shapes from the pack and measure.
   Ground truth is known because the tool placed every name.
   │
   ▼
5. Write the result to the language registry — per-shape detection,
   model name and version, date.
   │
   ├── clears threshold ──▶ "da is now VERIFIED (138/150, 92%).
   │                         Model: da_core_news_lg 3.8.0."
   │
   └── below threshold ──▶ "da stays PROVISIONAL (94/150, 63%).
                            Weakest shape: attendee_bullet (9/30).
                            It can still be used, with a warning on
                            every run. See the report for detail."
```

Step 3 is the only human step. Everything either side of it is mechanical.

### Flow D — Running an engagement on a provisional language

```
Analysis starts
   │
   ▼
Registry says `da` is PROVISIONAL
   │
   ▼
╔══════════════════════════════════════════════════════════════╗
║  WARNING — PROVISIONAL LANGUAGE                              ║
║                                                              ║
║  This engagement is declared `da` (Danish). Detection        ║
║  quality for Danish has been measured at 63% on person       ║
║  names — below the 90% bar English meets.                    ║
║                                                              ║
║  Names WILL be missed. Review the scrubbed output before     ║
║  it leaves your machine.                                     ║
║                                                              ║
║  To improve this: extend knowledge/languages/da.yaml and     ║
║  re-run /pii-add-language da.                                ║
╚══════════════════════════════════════════════════════════════╝
   │
   ▼
Stamp the journal, then continue (NON-BLOCKING)
```

Deliberately mirrors `_warn_empty_deny_list`: loud, impossible to miss,
non-blocking. Blocking here would strand a consultant with a document and no
way to unblock themselves.

## Screen & Component States

| State | Trigger | What the user sees |
| --- | --- | --- |
| Default (English) | No language declared — every engagement today | Nothing new. Identical to current behaviour. |
| Verified language | Declared language has a passing recorded measurement | One line at analysis start: `PII language: fr (verified, 91% person detection)` |
| Provisional language | Declared, model loads, measurement below threshold or absent | The Flow D banner, every run, plus a journal stamp |
| Model installing | Declared language's model not on this machine | Named progress line with the size, at init only |
| Pack scaffolded | `/pii-add-language` run with no pack present | The stub file, plus the three-item instruction in Flow C |
| Measuring | `/pii-add-language` with a filled pack | Per-shape progress: `prose 28/30 · attendee_bullet 24/30 · …` |
| Measured — verified | Result clears the threshold | Result line, registry updated, language becomes selectable at init |
| Measured — provisional | Result below threshold | Result line naming the weakest shape; language selectable but warns |
| Refused — non-Latin | Declared or onboarded language is non-Latin script | E4 |
| Refused — no model pin | No wheel registered for the language | E3 |
| Refused — uncovered core entity | Declared language has no recogniser for a core entity | E5 |

## Error States

| Error | Cause | User-facing message | Recovery |
| --- | --- | --- | --- |
| **E1 — Unknown language code** | Declared code is not in the language registry | `Unknown language 'xx'. Verified: en, fr, es. Provisional: none. To add a language, run /pii-add-language xx.` | Pick a registered language, or onboard it |
| **E2 — Model download failed** | Offline, or the wheel URL is unreachable | `Could not download the French detection model (fr_core_news_lg). PII scrubbing cannot run for this language without it, so the engagement was NOT created. Check your connection and re-run — nothing was left half-finished.` | Reconnect and re-run init |
| **E3 — No pinned model registered** | Language is Latin-script but no wheel is pinned | `No detection model is pinned for 'da'. spaCy publishes da_core_news_lg — pinning it is an Architect change to the language registry, because an unpinned model makes detection quality vary machine to machine. File a request naming the language.` | Architect pins the model |
| **E4 — Non-Latin script declared** | Declared language uses a non-Latin script | `'si' (Sinhala) is not supported. Non-Latin scripts need multilingual OCR and multilingual detection to land together — installing one without the other transcribes names into cleartext that detection still cannot see, which is worse than refusing. This is deliberate, not an oversight. Use English for now and handle Sinhala source material manually.` | None in this cycle — documented limitation |
| **E5 — Core entity uncovered** | Declared language has no recogniser for CLIENT, PERSON, EMAIL_ADDRESS or PHONE_NUMBER | `Language 'xx' has no detector for PERSON. Scrubbing would run and produce output that looks clean while missing every name. Refusing rather than pretending.` | Refuse; onboard properly or use English |
| **E6 — Non-core entity uncovered** | e.g. `CREDIT_CARD` has no French recogniser | `Note for fr: CREDIT_CARD and US_SSN have no French detector in Presidio. Those types will not be found in this engagement's documents. All other types are covered.` | Warn + journal, continue |
| **E7 — Language pack incomplete** | `/pii-add-language` run against a stub with unfilled fields | `knowledge/languages/da.yaml is still a template — 'names' is empty and 'do_not_redact' has 0 entries. I can't measure detection without real names to detect. Fill those in and re-run.` | Fill the pack |
| **E8 — Pack names rejected by the extractor** | Supplied names fail `_person_name_ok` | `12 of 30 names in the pack were rejected by the deny-list extractor and could not be measured: [list]. If these are correctly written names, that is itself the bug — report it rather than editing the names to fit.` | Report; likely a regex gap |

E8 exists because it is how the accented-name defect would have been caught. A
measurement harness that silently drops the names it cannot parse would have
scored English 30/30 while `José García` was being discarded upstream.
