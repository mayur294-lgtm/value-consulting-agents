# The story: "We took the machine apart"

A story brief and transcript for the Cortex change announcement.
Written to be handed to an animation tool. ~95 seconds.

---

# Background — what Cortex is and why this matters

**None of this appears in the video.** It is here so that whoever or whatever
builds the animation understands what is being described, and can make sensible
choices without asking. If a decision comes up that this brief doesn't cover,
decide it in the spirit of this section.

## Who this is for

Backbase makes software for banks. Inside Backbase there is a small team of
**value consultants** — the people who sit with a bank's executives and work out
whether a piece of change is actually worth doing. They build the business case:
what the bank is losing today, what it would gain, over how long, and what has to
be true for that to hold. Their output is the thing a bank's board reads before
approving several million in spend.

There are roughly forty of them. They are the entire audience for this video.
They are not engineers. They are commercially sharp, sceptical, and busy, and
they will stop watching the moment something feels like marketing.

## What Cortex is

Cortex is the internal system that team uses to do that work. It reads discovery
call transcripts, annual reports and client spreadsheets, and helps produce the
deliverables: capability assessments, ROI models, journey maps, roadmaps,
executive decks, commercial proposals.

It matters that Cortex is not a chatbot. It is a set of specialists — each one
carrying a piece of the consulting method, so the work comes out consistent
whoever ran it, and so a number in a board pack can be traced back to the
sentence in the transcript it came from.

## The two words in the script

- An **agent** is one specialist — the thing that reads transcripts and pulls out
  evidence, or the thing that builds the financial model.
- A **skill** is a shortcut a consultant types to reach one, like `/build-roi`.
- The **pipeline** was all of the agents chained together in a fixed order.

The video doesn't explain these terms and shouldn't. It just needs the animation
to treat the ten pieces as *specialists*, not as generic boxes.

## Why the change happened

The pipeline was written as a single program. Each specialist's instructions
lived inside it rather than inside the specialist, so nothing could be run on its
own. Getting one ROI model meant running all ten — hours of work and real money —
when the consultant needed one artifact before a meeting that afternoon.

So they stopped using it. They did the work in a single skill, or in plain
Claude, or by hand. That was rational. But it meant the method didn't travel with
them: no evidence trail, no recorded assumptions, none of the governance that
makes the output defensible in front of a bank's board.

The fix was to move each specialist's instructions into the specialist. The
pipeline still runs, unchanged. But now every step also stands alone.

**That is what the breaking-apart image in Beat 6 means.** Nothing is destroyed
and nothing is thrown away — a thing that was welded shut becomes a thing you can
take pieces from. The animation should feel like *release*, not like damage or
collapse. It's a relief, not an explosion.

## The culture this has to respect

The single strongest value in this team is that **every claim traces to a
source**, and that you never present a guess as a fact. When Cortex doesn't have
a number, it is built to say so rather than fill the gap.

Two consequences for this video:

1. **It sets the tone.** These are people who distrust polish. A confident,
   understated, slightly self-critical video will land. A glossy one will be
   dismissed on sight — and quietly reduce trust in the tool it's describing.
2. **It sets a hard rule.** Nothing on screen may be fabricated. If the video
   fakes a frame of output while claiming the tool never fabricates, that is the
   most damaging thing it could possibly do. Real output, or pick a different
   example.

## Where it will be watched

A link in a chat channel or on a shared drive. Often at a desk mid-morning,
sometimes on a phone with the sound off. It competes with everything else in
someone's day, so it has to be worth the first ten seconds — hence the cold open.

## What success looks like

A consultant watches it, thinks *"so I can just ask for the one thing"*, opens
the cheat sheet, and tries something that week.

That's it. Not admiration. Use.

## One note on confidentiality

This is internal Backbase material. Nothing in this brief names a bank, and
nothing on screen should either. If a real screen recording is used, it must come
from a test engagement rather than a live client.

---

# The video

## The spine

Cortex was built as one big machine. To get anything out of it, you had to run
the whole thing — so most people quietly stopped using it. They told us why, and
they were right. So we took the machine apart. Every part of it now works on its
own, and you pick up only the part you need. The machine still assembles when you
want all of it. And we keep making new parts — with a map so you can find them.

---

## Why this story

Every version of this announcement wants to open by celebrating the new thing.
It shouldn't. It should open by admitting the old thing didn't work, because
that is the sentence the audience already believes and has been too polite to
say. Once they hear us say it first, they'll listen to the rest.

So the emotional arc runs: **recognition → relief → curiosity.**

- *Recognition* — "yes, that was my experience, and someone noticed."
- *Relief* — "I don't have to run the whole thing any more."
- *Curiosity* — "what else is in there?"

The visual arc runs alongside it, and carries the same meaning without needing
to be explained: **one heavy locked block → the block comes apart → separate
pieces you can lift → more pieces arriving → a map of all of them.**

If someone watches with the sound off, that sequence of images alone should tell
them what changed.

---

## The arc, beat by beat

### Beat 1 — The admission
**We see:** Darkness. A single sentence appears, quietly, with nothing else
around it. No logo, no music, no motion. It sits there long enough to be slightly
uncomfortable.

**We hear:** *If you've used Cortex this year, there's a good chance you never ran the pipeline.*

---

### Beat 2 — The evidence
**We see:** The sentence clears. A number rises in its place, and settles.

**We hear:** *We looked. Almost every engagement this year was run as a single skill — or in plain Claude, with no Cortex at all. Hardly anyone ran the full pipeline.*

---

### Beat 3 — Whose fault it was
**We see:** Still and plain. One more line of text, alone.

**We hear:** *That wasn't people using it wrong. That was us building it wrong. And several of you told us so.*

---

### Beat 4 — The machine
**We see:** Out of the dark, a heavy object assembles itself: ten thick slabs
stacking one on top of another until they lock into a single solid block. It
looks welded shut. It looks like it weighs a great deal. The camera holds on it.

**We hear:** *Cortex's pipeline was one machine. Ten agents, bolted together in a fixed order.*

---

### Beat 5 — The long way round
**We see:** A thin band of light begins at the top of the block and travels
slowly down its face, lighting each slab in turn, one after another, never
skipping. It takes an uncomfortably long time to reach the bottom. When it
finally does, one small object drops out of the base of the machine.

**We hear:** *And the only way to get anything out of it was to run all ten. Hours, and real cost, to produce one thing you needed in the next twenty minutes. So people went around it. And when they went around it, none of the method came with them — no evidence trail, no assumptions, no governance.*

---

### Beat 6 — The break
**We see:** The block breaks apart. Not shattering, not crumbling — the ten
slabs cleanly separate and move away from one another, each staying whole, until
they are floating as ten distinct pieces.

**We hear:** *So we took it apart.*

> This is the moment the whole video exists for. The line and the break happen
> together. Everything before it is setup; everything after it is consequence.

---

### Beat 7 — Pick one up
**We see:** The ten pieces arrange themselves in front of us. One of them
brightens and lifts toward the camera; the others dim and fall back.

**We hear:** *Every one of those agents now works on its own. You need an ROI model — you ask for an ROI model. Not the other nine.*

---

### Beat 8 — It actually runs
**We see:** The lifted piece opens into a real working screen. A command is
typed. Real output appears, line by line: the levers it found, the evidence
behind each one, and — plainly marked — the one number it didn't have and refused
to invent.

**We hear:** *One command. A few minutes. And the method comes with it — every lever traced to evidence, and the gap it couldn't fill flagged rather than guessed.*

---

### Beat 9 — Still building
**We see:** Pull back to the ten pieces. Then an eleventh arrives from off-screen
and settles among them. Then a twelfth. They are visibly newer than the rest.

**We hear:** *And we're still adding. The newest is a proposal builder — it runs a live deal through the negotiation method and gives you the internal strategy and the client document, with a hard wall between the two.*

---

### Beat 10 — The map
**We see:** The floating pieces resolve into a clean page — a list, organised and
readable, with a title. As we watch, a new row writes itself onto the page
without anyone touching it.

**We hear:** *You'll get a cheat sheet with all of it — organised by the job you're trying to do, not by whether the thing is a skill or an agent. It's built from the code itself, so it updates when Cortex does. It won't go stale.*

---

### Beat 11 — What's next
**We see:** Calm. The page settles. A short closing line.

**We hear:** *Pull the latest Cortex, and have a look. Short how-to videos on the individual skills are coming, one at a time.*

---

### Beat 12 — Close
**We see:** Dark again. The closing words. The Backbase mark.

**We hear:** *We heard you. It's in pieces now — use the ones you need.*

---

## The transcript

Read at conversational pace, not presenter pace. Roughly 95 seconds.

> If you've used Cortex this year, there's a good chance you never ran the pipeline.
>
> We looked. Almost every engagement this year was run as a single skill — or in
> plain Claude, with no Cortex at all. Hardly anyone ran the full pipeline.
>
> That wasn't people using it wrong. That was us building it wrong. And several of
> you told us so.
>
> Cortex's pipeline was one machine. Ten agents, bolted together in a fixed order.
> And the only way to get anything out of it was to run all ten. Hours, and real
> cost, to produce one thing you needed in the next twenty minutes.
>
> So people went around it. And when they went around it, none of the method came
> with them — no evidence trail, no assumptions, no governance.
>
> So we took it apart.
>
> Every one of those agents now works on its own. You need an ROI model — you ask
> for an ROI model. Not the other nine. One command, a few minutes. And the method
> comes with it: every lever traced to evidence, and the gap it couldn't fill
> flagged rather than guessed.
>
> The full pipeline still runs, exactly as it did, for when you genuinely want the
> whole assessment. It's just not the entry fee any more.
>
> And we're still adding. The newest is a proposal builder — it runs a live deal
> through the negotiation method and gives you the internal strategy and the client
> document, with a hard wall between the two.
>
> You'll get a cheat sheet with all of it — organised by the job you're trying to
> do, not by whether the thing is a skill or an agent. It's built from the code
> itself, so it updates when Cortex does. It won't go stale.
>
> Pull the latest Cortex, and have a look. Short how-to videos on the individual
> skills are coming, one at a time.
>
> We heard you. It's in pieces now — use the ones you need.

**Pronunciation:** read `/build-roi` as "slash build R-O-I".

---

## Tone

Plain and unhurried. This is a colleague explaining something, not a product
launch. The script admits a mistake in its first fifteen seconds, and that
admission is the reason the rest gets listened to — so nothing in the treatment
should undercut it. No triumphant build, no swooshes, no "introducing".

The one moment allowed to be dramatic is the break in Beat 6.

---

## Things that must stay true

- **The example has to be a real run.** Beat 8 shows actual output from an actual
  command. If the real output is boring, pick a better example — never write a
  better-looking fake. The whole point of the tool is that it doesn't invent
  things, and a faked frame would say the opposite.
- **No client information anywhere.** Whatever is on screen in Beat 8 gets seen by
  forty people. Use a test engagement.
- **No invented numbers.** Beat 2's figure needs checking before it goes up; if it
  can't be confirmed, "almost every" works fine on its own. Don't put a cost
  figure on the old pipeline — the internal estimate isn't solid enough to show.
- **The full pipeline still exists.** Say so. People who like it shouldn't think
  it's been taken away.
- **Ten pieces means ten.** If the animation shows a different number, change the
  script to match rather than letting the two disagree.

---

## One dependency

The proposal builder in Beat 9 is on an unmerged pull request. If it hasn't
landed by the time this ships, cut Beat 9 and its lines — the story still works,
and the "more is coming" idea survives in Beat 11.
