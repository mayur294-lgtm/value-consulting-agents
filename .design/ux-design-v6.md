---
version: 6
prd: prd-v6.md
status: draft
date: 2026-08-25
author: Mariam Titus George
previous: ux-design-v5.md
---

# UX Design v6 — Presidio PII Gate

The user is a **non-technical value consultant**. Every message in this spec is written to be understood by someone who does not know what `pip` is. The governing rule for all copy:

> **What broke → what it means for you → how to fix it → whether you're blocked.**

A message that leads with a technical cause ("Presidio import failed") gets ignored, and an ignored PII warning is the same as no PII warning.

---

## User Flows

### Flow A — First session after this ships

```
git pull  →  SessionStart: pii-preflight.sh
        │
        ├── Python < 3.10 ─────┐
        ├── venv missing ──────┤
        ├── Presidio missing ──┼──▶ ⚠ PLAIN-LANGUAGE NOTICE (below)
        ├── model missing ─────┤        │
        ├── Tesseract missing ─┘        ▼
        │                         session continues — NOT blocked
        │                         guard is failing closed on inputs/
        │                                │
        │                                ▼
        │                    consultant runs: bash scripts/setup_pii.sh
        │                                │
        │                                ▼
        │                    next session → silent, everything works
        │
        └── all green ──▶ silent (no output)
```

The notice, verbatim:

```
⚠️  Cortex can't protect client information right now

What's wrong
   The tool that strips client names, emails and account numbers out of
   documents before they go to Claude isn't set up on this computer.

What this means for you
   • You can keep working. Nothing is locked.
   • Files in your engagement's inputs/ folder won't open until this is
     fixed. That's on purpose — opening one right now would send the
     client's real details to Claude with nothing removed.
   • Everything else works normally.

How to fix it — about 5 minutes, once
   Paste this into your terminal:

       bash scripts/setup_pii.sh

   It downloads a language pack (~380 MB), so give it a few minutes.

   Stuck? Just ask Claude: "help me set up PII protection"
```

**Design note.** The preflight prints exactly **one** command. An earlier draft printed four (`brew install`, `venv`, `activate`, `pip install`); a four-step sequence is where a non-technical consultant disengages. `setup_pii.sh` absorbs the steps and reports its own progress in the same register.

### Flow B — Reading a client document (the common case)

```
consultant: "read the annual report in inputs/"
        │
        ▼
 anonymize-guard intercepts Read
        │
        ├── not under engagements/*/inputs/ ──▶ ALLOW (unchanged)
        │
        ├── a .anon_ artifact ───────────────▶ ALLOW
        │
        └── raw client material
                 │
                 ▼
            DENY + the scrub command
                 │
                 ▼
   consultant runs the command → .anon_ produced → reads that
```

Deny message:

```
🛑 This file hasn't been cleaned yet

   inputs/Annual_Report_2025.pdf is straight from the client. Opening it
   would send their real names, emails and account numbers to Claude.

   Clean it first — this also turns the PDF into readable text:

       python3 scripts/anonymize_transcript.py \
           --file "inputs/Annual_Report_2025.pdf" --engagement-dir .

   That creates .anon_Annual_Report_2025.md — open that one instead.
```

The flags shown are the flags the script accepts. (Folded backlog fix: today's message prints a form the CLI rejects.)

### Flow C — Reading an image

One local OCR pass produces **two** artifacts; the agent picks what it needs. No classifier decides which.

```
inputs/Screenshot 2026-06-22.png
        │
        ▼
   local OCR (Tesseract — never leaves the machine)
        │
        ├──▶ text  ──▶ Presidio text pipeline ──▶ .anon_Screenshot….md
        │                                         (placeholders — carries the round-trip)
        │
        └──▶ PII regions ──▶ redacted copy ─────▶ .anon_Screenshot….png
                                                  (layout preserved, boxes filled)
```

Agents read the sidecar text when they need words, and open the redacted image when the layout *is* the content. Images embedded inside `.docx` / `.pptx` go through the identical path during document ingest — this is not a separate lane.

**Stated limitation, surfaced to the consultant on first image ingest:**

```
ℹ️  About screenshots

   Cortex blanks out any client details it can *read* in an image —
   names, emails, account numbers.

   It cannot blank a logo. A logo is a picture, not text, so it stays
   visible and reaches Claude.

   If a screenshot shows the client's logo, crop it out before adding it.
```

### Flow D — MCP query carrying a client identifier *(PR 1 — ships first)*

```
agent calls mcp__backbase-infobank__search("HNB digital onboarding capabilities")
        │
        ▼
 mcp-query-guard scans the query against the engagement deny-list
        │
        ├── clean ──▶ ALLOW
        │
        └── match ──▶ DENY
                        │
                        ▼
              agent rewrites generically and retries
```

```
🛑 That Infobank search names the client

   Your search contained "HNB". Infobank sits outside Cortex, so client
   names must not go into it.

   Ask the same question generically:
       "digital onboarding capabilities for a Tier-2 retail bank in South Asia"

   (Security protocol §5)
```

This flow fires in **both** interactive sessions and pipeline runs — hooks fire under the Agent SDK, and `bypassPermissions` does not bypass hooks.

### Flow E — Delivery (the round trip)

```
.anon_ inputs ──▶ agents work in placeholders ──▶ outputs/ carry placeholders
                                                          │
                                                          ▼
                                          artifact_boundary deanon (exit gate)
                                                          │
                        ┌─────────────────────────────────┴────────────────┐
                        ▼                                                  ▼
              every file restored                          something couldn't be restored
              client_ready: true                           client_ready: false
                        │                                                  │
                        ▼                                                  ▼
                 safe to send                        names the file + the re-run command
```

```
🛑 Not ready to send to the client

   These files still have placeholders in them instead of real names:
       outputs/ROI_Model.xlsx

   Fix it and check again:
       python3 scripts/artifact_boundary.py deanon outputs/
```

### Flow F — Presidio broken mid-engagement

Guard **fails closed on `engagements/*/inputs/` only**; everything else stays open. A consultant can keep writing, editing and building deliverables — they just can't open raw client material until the install is repaired. The denial message is the Flow A notice, so the cause is never mysterious.

This is deliberate: the guard once failed closed *everywhere* and wedged every session (PR #82). Narrow fail-closed keeps the guarantee without repeating that.

### Flow G — Engagements get opaque directory names

```
./scripts/init_engagement.sh hdfc 2026-08_retail_assessment
        │
        ▼
  creates engagements/e7f3a2c1/2026-08_retail_assessment/
  writes  .engagement_map.json   (gitignored, local, chmod 600)
        │
        ▼
  "Created engagement e7f3a2c1 for HDFC.
   Find it any time with:  ./scripts/find_engagement.sh hdfc"
```

Consultants never hand-type an ID. `find_engagement.sh <client>` resolves the name; `ls` inside the engagement is unchanged. Existing directories migrate once via `migrate_engagement_ids.sh`, which rewrites paths and preserves history.

**Why this exists:** the directory name *is* the client's identity, and `compose_prompt` renders `engagement_dir` into prompt text on every agent call. Without this, the client's name is sent to the API on every invocation no matter how well the file contents are scrubbed.

---

## Screen & Component States

### `pii-preflight.sh` (SessionStart)

| State | Trigger | What the consultant sees |
| --- | --- | --- |
| Silent | All checks pass | Nothing |
| Python too old | `python3 --version` < 3.10 | Flow A notice, "how to fix" = `setup_pii.sh` |
| Not installed | Presidio import fails | Flow A notice |
| Model missing | spaCy model absent | Flow A notice, mentions the ~380 MB download |
| OCR missing | Tesseract absent | Flow A notice, adds: "screenshots won't be usable until this is fixed" |
| Partially set up | Some checks pass | One notice listing only what's missing — never a wall of green ticks |

### `anonymize-guard.py` (PreToolUse: Read, Bash)

| State | Trigger | Behaviour |
| --- | --- | --- |
| Pass-through | Path outside `engagements/*/inputs/` | Allow silently |
| Already clean | `.anon_` artifact, or placeholders present | Allow silently |
| Needs scrubbing | Raw client material | Deny + Flow B message |
| Image | `.png/.jpg/.jpeg` under `inputs/` | Deny + Flow C ingest command + logo warning |
| Unsupported binary | Format with no extractor | Deny, name the format, suggest exporting to PDF |
| Engine unavailable | Presidio import fails | Deny **only** under `inputs/`; allow elsewhere |
| Guard crash | Unexpected exception | Allow (never wedge the session) — except under `inputs/`, which stays denied |

### `mcp-query-guard.py` (PreToolUse: `mcp__*`)

| State | Trigger | Behaviour |
| --- | --- | --- |
| Clean | No deny-list match in the query | Allow |
| Client identifier | Deny-list match | Deny + Flow D message |
| No deny-list | Engagement has no names configured | Allow + stderr warning (cannot verify) |
| Engine unavailable | Presidio import fails | Deny — an unverifiable outbound query is not sent |

---

## Error States

| Error | Cause | User-facing message | Recovery |
| --- | --- | --- | --- |
| Not installed | Presidio / model / Tesseract absent | Flow A notice | `bash scripts/setup_pii.sh` |
| Python too old | Interpreter < 3.10 | Flow A notice | `setup_pii.sh` installs 3.11 into a venv |
| Raw file blocked | Unscrubbed client material | Flow B message | Run the scrub command shown |
| Image blocked | Image not yet ingested | Flow C message + logo warning | Run ingest; crop logos first |
| Unsupported format | No extractor for the type | "Cortex can't read `.key` files yet. Export it as PDF and add that instead." | Export and re-add |
| No names configured | Intake lists no client/stakeholder names | "⚠️ No client or stakeholder names found in `inputs/engagement_intake.md` or `ENGAGEMENT_CONTEXT.md`. Only generic details (emails, phones, ID numbers) were removed — the client's own name may still reach Claude. Add the names and run this again." | Add names, re-run. **Warns, never blocks** |
| MCP query names the client | Deny-list match in outbound query | Flow D message | Agent rewrites generically |
| Not client-ready | Placeholders left in outputs | Flow E message, names each file | Re-run the deanon gate |
| Unrestorable file | Workbook can't be opened for restore | Same, plus "this file may need regenerating" | Regenerate, re-run |
| Logo present | Not detectable | Flow C notice (proactive, not an error) | Crop before adding |

---

## Copy Rules (binding on implementation)

1. **No tool names in consultant-facing text.** "Presidio", "spaCy", "Tesseract", "pip" appear nowhere a consultant reads. `setup_pii.sh`'s own output may name them; the preflight notice may not.
2. **Consequence before instruction.** Every blocking message says what it means for the consultant before it says what to type.
3. **Say whether they're blocked.** Ambiguity gets warnings ignored.
4. **One command, not a sequence.** If remediation needs several steps, a script absorbs them.
5. **Never "an error occurred".** Every message names the file and the next action.
