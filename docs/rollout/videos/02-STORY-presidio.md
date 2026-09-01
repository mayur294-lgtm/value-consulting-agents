# The story: "We stopped writing the rules ourselves"

A story brief and transcript for the PII protection setup video.
Written to be handed to an animation tool. ~2 minutes.

---

# Background — what this is and why it matters

**None of this appears in the video.** It is here so whoever builds the animation
understands what is being described. If a decision comes up that this brief
doesn't cover, decide it in the spirit of this section.

## Who this is for

Backbase makes software for banks. Inside Backbase, a small team of **value
consultants** work with a bank's executives to build the business case for change
— what the bank is losing today, what it would gain, and what has to be true for
that to hold. Their output is what a board reads before approving several million
in spend.

There are about forty of them. They are the audience. **They are not technical.**
Most of them have never opened a terminal for anything other than Cortex. Any
sentence that assumes they know what a script, a library or an environment is
will lose them.

## What Cortex is, and what the problem was

Cortex is the internal system this team uses. It reads client material — call
transcripts, annual reports, RFPs, pricing spreadsheets — and helps produce
assessments, ROI models and proposals.

That material is confidential. Client names, the names of the executives in the
room, account numbers, unpublished financials. Before any of it reaches the AI
model, it is supposed to be stripped out and replaced with placeholders, then put
back at the end so the final document reads normally.

**The system that did the stripping was written by hand.** Five patterns someone
wrote out — things that look like an email address, things that look like a phone
number — plus a list of names a consultant was expected to type in manually for
each engagement.

When it was measured, the results were bad:

- It examined **3 of the 77 real client files** sitting in engagement folders.
  Everything else — the PDFs, the Word documents, the spreadsheets and decks that
  make up almost all real work — went through untouched.
- Names were only found if someone had typed them into a form first. When that
  form was left empty, the system quietly did almost nothing and said nothing.
- In a test, a real client's name and the names of real people went through in
  plain text, with no warning.

This is the honest shape of the problem: **it wasn't broken, it was outgrown.**
It was written for a smaller, simpler version of the work, and the work moved
faster than the hand-written rules did. Nobody was careless. It just stopped
being enough, and — worse — it didn't say so.

## What changed

Microsoft builds a tool for exactly this job, called Presidio. It is open source,
maintained, and it is what this problem looks like when someone works on it full
time. Instead of matching patterns, it actually recognises what a name is, in
context.

Cortex now uses it. That means:

- Every kind of document is covered, not just three text files — PDF, Word,
  PowerPoint, Excel, CSV.
- The client's own name is held as a specific thing to hide, because that is the
  single most important thing to get right and pattern-matching was worst at it.
- Protection now sits where consultants actually work. Previously it only ran
  inside the full pipeline, which — as the other video explains — almost nobody
  ran. The strongest lock was on the least-used door.
- If a document can't be cleaned, it simply doesn't open. Failing shut, not open.

The cost of all this is a one-time setup on each person's laptop, because the tool
needs a language model downloaded to work. **That setup is the entire reason this
video exists.**

## The tone this needs

This is a safety change with a required action, and the two pull in opposite
directions. Too alarming and people freeze or feel accused. Too casual and they
don't do it.

The line to walk: **matter-of-fact.** Something was not good enough, we know why,
we fixed it properly, here is the one thing you need to do. No blame — nobody
watching wrote the old rules. No drama — nothing has leaked to a client, and the
video should not imply otherwise.

## Look and feel

**White background**, unlike the other Cortex videos which are dark. This one is
instructional rather than announcemental, and light reads as calm and clear. Navy
text on white or very light grey. Blue for anything the viewer should notice. Red
used once, sparingly, for the old state.

**The terminal must be a real Claude Code session**, not a generic movie hacker
terminal. This matters: the viewer needs to recognise the thing on screen as the
same thing on their own machine. That means Claude Code's actual interface — the
plain prompt, the real wording of its messages — not green text on black, not
scrolling code, not a Matrix effect.

## What success looks like

Someone watches, understands in fifteen seconds why this is worth their time,
runs one command, and never thinks about it again.

## Confidentiality

Nothing in this brief names a bank, and nothing on screen should either. Any real
screen recording must come from a test engagement.

---

# The video

## The spine

We used to write the rules for hiding client information ourselves, by hand. They
covered far less than we thought. Microsoft makes a tool built for exactly this,
so we use that now instead. It needs about ten minutes of setup on your laptop,
once — and here is what to type.

## The shape

Three parts, in this order, and the proportions matter:

1. **Why** — 35 seconds. Enough to make the setup feel worth doing.
2. **What to do** — 50 seconds. The actual instruction, slowly, once.
3. **What changes afterwards** — 35 seconds. So nothing is a surprise later.

People will scrub back to part 2. Make it easy to find — it should look visibly
different from everything around it.

---

## The arc, beat by beat

### Beat 1 — What we're protecting
**We see:** White. A single document slides gently into frame — recognisably a
client report, with a name and some numbers on it, though not legible enough to
read. It moves toward the edge of frame, as if being sent somewhere.

**We hear:** *Everything we work from belongs to a client. Their name, their people, their numbers.*

---

### Beat 2 — The old guard
**We see:** The document's path is intercepted by a small handwritten list — five
short lines on a single sheet, visibly modest, visibly hand-made. It checks the
document and waves it through.

**We hear:** *Before any of it reaches Claude, it's supposed to be stripped out and put back afterwards. Until now, the thing doing the stripping was a short list of rules we wrote ourselves — by hand.*

---

### Beat 3 — The scale of it
**We see:** Pull back. The one document becomes a large stack — dozens of them,
of every shape: PDFs, spreadsheets, slide decks, Word files. The small
handwritten list checks three of them. The rest flow straight past it, untouched.

**We hear:** *When we measured it, it was looking at three files out of seventy-seven. Annual reports, spreadsheets, client decks — almost everything real — went straight past.*

---

### Beat 4 — The quiet part
**We see:** One document that got through comes back into focus. A name on it is
plainly visible. Nothing flashes, nothing alarms. It simply passes.

**We hear:** *And when it missed something, it didn't tell us. In one test, a client's name and the names of people in the room went through in plain text, with no warning at all.*

---

### Beat 5 — Not careless, outgrown
**We see:** The handwritten list again, alone on white. It doesn't tear or burn —
it is simply, gently set aside.

**We hear:** *That's not carelessness. It was written for a smaller version of this job, and the work moved faster than the rules did.*

---

### Beat 6 — The replacement
**We see:** In its place, something built and solid arrives — clearly a made
object rather than a handwritten note. Calm, unshowy, permanent-looking.

**We hear:** *So we stopped writing them ourselves. Microsoft builds a tool for exactly this job — it's open source, it's maintained, and recognising names in documents is the only thing it does. That's what Cortex uses now.*

---

### Beat 7 — What it catches
**We see:** The full stack of documents flows past the new object. Every one is
checked. As each passes, the sensitive parts on it quietly turn into neutral
placeholders. Nothing is destroyed — the documents carry on, just with the names
covered.

**We hear:** *It reads every kind of document — PDFs, Word, PowerPoint, spreadsheets. It understands what a name looks like in context, instead of matching patterns. And if it can't clean something, that file simply won't open. It fails safe.*

---

### Beat 8 — The ask
**We see:** A clear, deliberate change of gear. The frame settles into something
plainer and more instructional than everything before it.

**We hear:** *There's one thing it needs from you. It uses a language pack that has to be downloaded onto your laptop, so there's a setup step — once, about ten minutes, and then you never think about it again.*

---

### Beat 9 — What you'll see
**We see:** A real Claude Code session on screen, on the white background. It
shows the actual message Cortex gives when protection isn't set up yet: a short
warning, an explanation in plain words, and one command. The command is
highlighted.

**We hear:** *Cortex will tell you. Every time you start it, it checks — and if this isn't set up, you'll see this. It doesn't block you from working. It just won't open client files until it's sorted.*

---

### Beat 10 — The command
**We see:** The command, large and alone, held on screen long enough to be typed
out by someone watching. It is typed into the real Claude Code session and runs.
Progress appears. It finishes.

**We hear:** *Two lines. First, get the latest Cortex. Then run the setup. It downloads about four hundred megabytes, so give it a few minutes. When it says "setup complete", you're done — close it and carry on.*

---

### Beat 11 — If it complains
**We see:** Briefly, a different message, then the one command that answers it.

**We hear:** *If it says it can't find the right version of Python, that's the one thing it won't install for you — there's a single command for that too, then run the setup again. And if anything else goes wrong, just ask Claude to help you set up PII protection. It can read the error.*

---

### Beat 12 — What looks different afterwards
**We see:** A folder list. Where client names used to be, there are now short
neutral codes. Then a search: a client's name typed in, and the right folder
surfacing immediately.

**We hear:** *One thing will look odd afterwards. Engagement folders are named with codes now instead of client names — because the folder name itself was being sent to Claude on every single message, which gave the client away no matter how well the documents inside were cleaned. You never need to know the codes. You search the client's name, the way you always did.*

---

### Beat 13 — The honest limits
**We see:** Calm white. Three short lines appear in turn.

**We hear:** *Two things it won't do. It works in English — flag it if you're working in another language. And it protects files you put in the engagement folder, not text you paste straight into the chat. So put client material in the folder, and point Claude at it.*

---

### Beat 14 — Close
**We see:** White, quiet. The closing words, and the Backbase mark.

**We hear:** *Ten minutes, once. Then it's invisible, and the client's details stop leaving the building.*

---

## The transcript

Read calmly and slowly. This is an instruction, not an announcement, and people
will be following along. Roughly two minutes.

> Everything we work from belongs to a client. Their name, their people, their
> numbers.
>
> Before any of it reaches Claude, it's supposed to be stripped out, and put back
> afterwards. Until now, the thing doing the stripping was a short list of rules we
> wrote ourselves, by hand.
>
> When we measured it, it was looking at three files out of seventy-seven. Annual
> reports, spreadsheets, client decks — almost everything real — went straight past.
>
> And when it missed something, it didn't tell us. In one test, a client's name and
> the names of people in the room went through in plain text, with no warning at all.
>
> That's not carelessness. It was written for a smaller version of this job, and the
> work moved faster than the rules did.
>
> So we stopped writing them ourselves. Microsoft builds a tool for exactly this job.
> It's open source, it's maintained, and recognising names in documents is the only
> thing it does. That's what Cortex uses now.
>
> It reads every kind of document — PDFs, Word, PowerPoint, spreadsheets. It
> understands what a name looks like in context, instead of matching patterns. And if
> it can't clean something, that file simply won't open. It fails safe.
>
> There's one thing it needs from you.
>
> It uses a language pack that has to be downloaded onto your laptop, so there's a
> setup step. Once. About ten minutes. Then you never think about it again.
>
> Cortex will tell you. Every time you start it, it checks — and if this isn't set
> up, you'll see this. It doesn't block you from working. It just won't open client
> files until it's sorted.
>
> Two lines. First, get the latest Cortex. Then run the setup.
>
> It downloads about four hundred megabytes, so give it a few minutes. When it says
> "setup complete", you're done. Close it and carry on.
>
> If it says it can't find the right version of Python, that's the one thing it won't
> install for you — there's a single command for that too, and then you run the setup
> again. And if anything else goes wrong, just ask Claude to help you set up PII
> protection. It can read the error and tell you what it means.
>
> One thing will look different afterwards. Engagement folders are named with codes
> now, instead of client names. That's deliberate — the folder name itself was being
> sent to Claude on every single message, which gave the client away no matter how
> well the documents inside had been cleaned. You never need to know the codes. You
> search the client's name, the way you always did.
>
> Two things it won't do. It works in English, so flag it if you're working in
> another language. And it protects files you put in the engagement folder, not text
> you paste straight into the chat — so put client material in the folder, and point
> Claude at it.
>
> Ten minutes, once. Then it's invisible, and the client's details stop leaving the
> building.

---

## The words that must be exactly right on screen

Everything else can be paraphrased. These cannot — people will type them.

**The two commands, shown one after the other:**

```
git checkout main && git pull
```

```
bash scripts/setup_pii.sh
```

**What finishing looks like:**

```
=== Setup complete ===
```

**The one thing it won't install for you:**

```
brew install python@3.11
```

**Finding an engagement afterwards:**

```
./scripts/find_engagement.sh navy_federal
```

**The message Cortex shows when protection isn't set up.** This is real text from
the actual product — reproduce it as it is, don't rewrite it:

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
```

---

## Language rules

This audience is non-technical. These words do not appear, in the voiceover or on
screen:

| Don't say | Say instead |
|---|---|
| Regex, regular expression, pattern matching | a short list of rules we wrote by hand |
| Named entity recognition, NER, model, inference | it understands what a name looks like |
| Presidio | *(name Microsoft, not the product — the credibility is in who built it)* |
| Anonymisation, pseudonymisation, redaction | stripping out, hiding, covering up |
| Virtual environment, dependency, package, library | *(don't mention — it's inside the one command)* |
| Fails closed | it fails safe / the file simply won't open |
| Hook, preflight, session start | every time you start Cortex, it checks |
| Opaque identifier | a short code instead of the client's name |
| spaCy model, en_core_web_lg | a language pack |
| Repository, repo, branch, pull | get the latest Cortex |

"Python" is allowed to appear once, in Beat 11, because the error message says it
and they'll see that word. Everywhere else, avoid it.

---

## Things that must stay true

- **Nothing has leaked to a client.** The failure described in Beat 4 was found in
  an internal test. The video must not imply a client was exposed, because that
  isn't what happened.
- **Nobody watching is at fault.** No wagging fingers, no "you should have". The
  old rules were ours, not theirs.
- **The numbers are real.** Three files out of seventy-seven is a measurement. Use
  it exactly; don't round it into something punchier.
- **Don't overclaim the new tool.** It is much better. It is not perfect — Beat 13
  exists so nobody assumes it is, and it should not be cut for time.
- **Real screens only.** Any Claude Code session shown must be a real one from a
  test engagement. This is a video about not faking things.
- **Ten minutes, not five.** The in-product message says five; the download often
  makes it longer. Promise the longer number and let people be pleasantly
  surprised.
