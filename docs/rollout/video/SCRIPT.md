# Cortex announcement video

**~55 seconds · 6 scenes · 9 clips · 16:9 · voiceover over frames that carry their own text**

One idea: the assessment pipeline used to be all or nothing, and now every agent
in it runs on its own. `CHANGE_BRIEF.md` §3 says this in prose. This is the
version people will watch.

Companion: [RUNWAY-PROMPTS.md](RUNWAY-PROMPTS.md) is the paste-ready build.

---

## Rules this script is built on

**Two kinds of clip.** Clips 1-6 are *generated*: Runway gets a text-free
layout reference from `stills/refs/` and free rein to render it properly, and
their captions go on in the edit. Clips 7 and 8 are *locked*: they carry the
Claude Code interface and the five command names, so the finished frame from
`stills/` is animated as-is and Runway draws no letter. Runway can reinterpret a
frame or preserve text in it, never both.

**The gryphon is composited, not generated.** `docs/rollout/assets/gryphon.png`
is pasted into every frame it appears in, so the character is byte-identical
across all 8 clips. Continuity is structural, not something we hope the model
gets right.

**Warm light everywhere.** The room is off-white and lit warm. A flat white
field reads clinical and fights a pastel mascot. The look clause is identical in
all 8 prompts.

**Captions go on in the edit, over clips 1-6 only.** Those clips are
generated, so nothing in them is guaranteed legible. Clips 7 and 8 already carry
their text; typing over those doubles it. The caption spec (52 px navy, lower
third) is in [RUNWAY-PROMPTS.md](RUNWAY-PROMPTS.md) so the six read as one set.

**Ten carriages, one per agent**, in pipeline order, read off
`assess-pipeline-chain.svg`. The locomotive is the Presidio anonymise gate.

---

## Scene 1 · Hi, I'm Cortex

**Clip 1 · 5s · still `01-hello.png`**

| | |
|---|---|
| **VO** | "Hi. I'm Cortex. Your value consulting assistant that runs in parallel, and shows its working." |
| **Caption** | `I'm Cortex.` |
| **On screen** | The gryphon alone in the warm room, wings settling, one slow blink. |

---

## Scene 2 · What Cortex was

**Clip 2 · 5s · still `02-pipeline.png`**

| | |
|---|---|
| **VO** | "This is what I used to be. One pipeline. Ten agents. All or nothing." |
| **Caption** | `Every agent ran. Even for a small job.` · timer `01:50:18` |
| **On screen** | The real `assess-pipeline-chain` diagram stands to the left, warm-graded. The gryphon looks at it from the right. Slow downward drift so the chain reads as long. |

The diagram is the actual repo asset, not a drawing of one. Anyone who has seen
the cheat sheet recognises it.

---

## Scene 3 · The train

**Clips 3 and 4 · 5s + 5s · stills `03-train.png`, `04-flyover.png`**

| | |
|---|---|
| **VO** | "Think of it as a train. Ten carriages welded together. Want just the ROI model? You still ran the whole train. About 2 hours and real cost." |
| **Caption** | `Ten carriages, welded together` · qualifier `About 2 hours and real cost` |
| **Clip 3** | Camera tracks along the train. Blue couplings visible between every carriage. |
| **Clip 4** | The gryphon flies left to right above the train. |

Carriages, in order: `discovery` · `journey` · `market` · `capability` ·
`roi-hypothesis` · `benchmark` · `roi-model` · `roadmap` · `assembly` ·
`harvest`. Short stems, because the full agent names are unreadable at carriage
width and scene 2 has just shown them in full.

**"About 2 hours" is measured, not rhetorical.** The reference run logged 6618s and
$25.93. Do not round it up for effect.

---

## Scene 4 · The split

**Clips 5 and 6 · 5s + 5s · stills `05-couplings.png`, `06-split.png`**

| | |
|---|---|
| **VO** | "You told us that was too much. So we split the train up. Every carriage runs on its own now." |
| **Caption** | `Every carriage runs on its own`, over clip 6. Clip 5 stays bare |
| **Clip 5** | Close on the couplings. The blue links release and drop. Nothing else moves. |
| **Clip 6** | The carriages drift apart and `roi-model` rolls forward alone. |

**This has to be two clips.** A block that spreads in one move reads as
collapse, which is the opposite of the point. "The weld gives" and "the pieces
move apart" are separate beats, and separating them is what makes it read as
release rather than failure.

---

## Scene 5 · Using it

**Clips 7 and 8 · 10s + 5s · stills `07-tutorial.png`, `08-coming.png`**

| | |
|---|---|
| **VO (7)** | "Need a deck? Ask for the deck. One skill, not the whole train." |
| **VO (8)** | "And there's more coming. The proposal builder lands next. Same idea: ask for the deliverable." |
| **In the frame** | already baked, both clips. Add nothing in the edit |
| **Clip 7** | Claude Code window top-left running `/frontline`, gryphon bottom-right presenting. Only the landing and the cursor move. |
| **Clip 8** | Five coming-soon cards lift and fan out. The one energetic beat in the film. |

The terminal shows the real catalog example: `/frontline` asks what you are
making, the answer is "a deck for the CFO", and it routes to
`/frontline-slides-html`.

The five cards are pulled from `catalog.yaml` at build time, so they cannot
drift from the cheat sheet: `/proposal-builder`, `/proposal-longform`,
`/deal-notes`, `/pricing-model` and `/critty`. All are real `status: pending`
entries against `#153` and `#97`. Nothing on that card wall is invented.

---

## Scene 6 · Goodbye

**Clip 9 · 5s · still `09-goodbye.png`**

| | |
|---|---|
| **VO** | "Everything I can do is on one page. Start there, and just ask for the deliverable." |
| **In the frame** | already baked: `Everything Cortex can do, on one page` and `cortex-cheat-sheet.html` |
| **On screen** | The gryphon back in the centre of the warm room, lifting a wing. |

Same composition as scene 1, so the film closes where it opened. It ends by
sending people to the cheat sheet rather than just stopping, which is the point
of the rollout.

---

## Timing

| | |
|---|---|
| Clip runtime | 50s (7 × 5s + 1 × 10s + 1 × 5s) |
| VO | 120 words ≈ 50s at 145 wpm |
| With crossfades | ~55s |

If it overruns, cut words. Do not cut a scene, and do not cut clip 5, which is
the beat the whole film turns on.
