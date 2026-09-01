# Recording brief — the `/frontline` screencast

A real screen recording of a deck being built, cut in after clip 7. Everything
else in the film is generated; this is the one place a viewer sees the actual
tool doing the actual thing.

**Target on screen: ~10 seconds.** Record it at whatever length it really takes,
then it gets speed-ramped down. Do not rush the take.

---

## Before you press record

**1. Deal with the sidebar.** It carries live client session names — Bank
several real client names were visible in the screenshot you sent me. This film
goes to the whole team and may outlive the engagements. Either collapse the
sidebar entirely, or start Claude Code in a clean window with no session history
showing. Do not rely on it being too small to read: people pause videos.

**2. Check the chips under the input box.** They show `Local`, the repo, and the
branch name. A branch called `mariamt/20260826-eval-gate-v7-pr6` is fine. A
branch named after a client is not.

**3. Silence the machine.** Do Not Disturb on. No notification banners, no Slack
badge, no calendar alert mid-take.

**4. Window size.** The film is 1280×720. Record the Claude Code window at
roughly 16:9 so it scales without letterboxing. Full screen is fine too — I can
crop to the window.

**5. Clear the deck you're about to build**, if a file of that name already
exists, so the "file created" moment is real rather than an overwrite.

---

## The take

Type slowly enough to read. The point of this shot is that it looks easy.

**1 — Invoke it.** In the task box, type and send:

```
/frontline
```

**2 — Let it ask.** It comes back with the four-format menu: HTML slide deck,
long-form HTML, PDF, PPT — plus two clarifiers, presented-or-async and
editable-or-locked. Let that render fully and pause a beat. This is the moment
that makes the point: you did not have to know which builder you wanted.

**3 — Answer it.** Type and send:

```
an HTML deck, presented. 5 slides on why we split the pipeline into skills
```

Deliberately internal — no client, no engagement, nothing that needs scrubbing
later. It is also on-message: the deck is about the same change the film is
about.

**4 — Let it build.** It reads the engine files, designs the slide structure and
writes a single self-contained HTML file. This is the long part, minutes not
seconds. **Keep recording through it.** Do not cut — the speed-ramp needs the
real footage to compress, and a hard cut here would look like a fake.

**5 — Open the result.** When it names the output file, open it in the browser.

**6 — Page through it.** Arrow-right through 2 or 3 slides, about a second each.
Land on a slide that looks good and hold for two seconds. Stop recording.

---

## What the shot has to prove

In order of importance, because the speed-ramp will keep the first and may lose
the last:

1. One command, no decision about which tool
2. It asked what format rather than assuming
3. A real branded deck came out the other end

---

## After

Save it into `Runway ouputs/` as `07b.Deck.mp4` and tell me. I will:

- crop to the window and conform to 1280×720 / 24fps
- speed-ramp the build: real time on the typing and the answer, hard acceleration
  through the wait, real time again on the deck
- cut it in after clip 7 and shift clips 8 and 9 down

No credits, no Runway. It is a local ffmpeg operation.

---

## What this does to the film

| | before | after |
|---|---|---|
| Runtime | 42.4s | ~52s |
| Scenes | 6 | 7 |
| Voiceover | 8 lines | 9 lines |

The new voiceover line sits over the screencast, in `VO.txt` as its own
paragraph so the assembler can still find the scene break:

> That's it. One command, and it asks you the rest.

Re-record the whole voiceover in one pass as before, rather than splicing a line
in — one continuous read is what makes the narrator sound like one person.
