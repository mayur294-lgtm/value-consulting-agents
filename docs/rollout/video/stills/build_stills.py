#!/usr/bin/env python3
"""Build the locked start-frames for the Cortex announcement video.

Runway never draws a letter. Every frame that carries text is composed here and
handed to Runway as an image-to-video start frame. Runway supplies motion only.
That is what fixes the garbled-typography problem.

The gryphon is docs/rollout/assets/gryphon.png, pasted in rather than generated,
so the character is byte-identical across all 8 clips. Continuity is structural,
not something we hope the model gets right.

Skill names are read from docs/rollout/catalog.yaml so they cannot drift from
the cheat sheet.

Rendered with Pillow, not a browser: headless Chrome takes over 90s a frame on
a consultant laptop, and these are geometric compositions.

Usage:  python3 docs/rollout/video/stills/build_stills.py
"""

import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[4]
ASSETS = ROOT / "docs/rollout/assets"
CATALOG = ROOT / "docs/rollout/catalog.yaml"
OUT = Path(__file__).resolve().parent

W, H = 1920, 1080

# The warm room. A pure white ground lit flat reads clinical, which is wrong for
# a pastel mascot and wrong for the tone. Everything sits on this.
CREAM = (250, 245, 238)
CREAM_LIT = (255, 253, 248)
CREAM_DEEP = (238, 230, 218)
NAVY = (4, 19, 38)
NAVY_DIM = (46, 62, 82)
BLUE = (51, 103, 255)
MUTED = (107, 119, 134)
GREEN = (46, 204, 113)
RED = (255, 80, 60)
WHITE = (255, 255, 255)

# train livery, taken from the reference: white body, cool grey shadow, dark glass
STEEL = (201, 210, 220)
STEEL_DEEP = (168, 180, 193)
GLASS = (42, 54, 68)
BOGIE = (58, 70, 84)

FONTS = {
    "regular": "/System/Library/Fonts/Supplemental/Arial.ttf",
    "bold": "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "mono": "/System/Library/Fonts/Menlo.ttc",
}

# Ten agents, in pipeline order, read off assess-pipeline-chain.svg.
CARRIAGES = [
    "discovery", "journey", "market", "capability", "roi-hypothesis",
    "benchmark", "roi-model", "roadmap", "assembly", "harvest",
]

# The measured reference run: 6618s and $25.93. As a clock that is 01:50:18, and the
# timer in scene 2 shows exactly that. Do not round it for effect.
RUNTIME_CLOCK = "01:50:18"

# Sidebar rows for the Claude Code frame. Deliberately internal-only: the real
# app sidebar carries live client names and this film goes to the whole team.
SESSIONS = [
    "Cortex changes rollout plan",
    "Rerun evals for recent builds",
    "PII scrubbing support",
    "Harness evals and goldens",
    "Assessment dashboard build",
    "ROI fix harness",
    "Pipeline split follow-ups",
    "Catalog drift check",
]

# One type scale for every caption in the film. Change it here, not at the call
# site, or the captions drift out of step once the clips are cut together.
EYEBROW = 28   # spaced uppercase, muted: the scene label
HEAD = 52      # bold navy: the line the viewer actually reads
SUB = 30       # regular muted: the qualifier under a headline

# Reference mode. With --refs the frames are emitted without a single letter:
# they become layout guides for Runway to reinterpret, not finished frames.
# Runway renders far better than flat vector art, but anything it is free to
# redraw includes any text it can see, so the two modes are exclusive.
REFS = False

# Livery names garble. Runway re-renders the train in 3D and re-invents the small
# text painted on it: "roi-hypmark", "jo-hypmey", "market reseach" all came back
# from real takes. Big graphic captions survive, paint on a re-rendered object
# does not. --no-livery drops the carriage names and keeps the captions, which is
# the right trade because scene 2 already names all ten agents.
LIVERY = True

_font_cache: dict = {}


def font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    key = (size, weight)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FONTS[weight], size)
    return _font_cache[key]


def pending_skills() -> list:
    """(cmd, name) for every catalog entry marked status: pending."""
    out, name, cmd = [], None, None
    for line in CATALOG.read_text().splitlines():
        s = line.strip()
        m = re.match(r'- name:\s*"(.+)"', s)
        if m:
            name, cmd = m.group(1), None
            continue
        m = re.match(r'cmd:\s*"(.+)"', s)
        if m:
            cmd = m.group(1)
            continue
        if s.startswith("status:") and "pending" in s and cmd and name:
            out.append((cmd, name))
    return out


# --------------------------------------------------------------------------
# the room
# --------------------------------------------------------------------------
def room() -> Image.Image:
    """Warm off-white with a soft golden pool of light and a floor falloff."""
    small = Image.new("RGB", (W // 8, H // 8), CREAM)
    px = small.load()
    sw, sh = small.size
    cx, cy = sw * 0.5, sh * 0.38
    rx, ry = sw * 0.62, sh * 0.52
    for y in range(sh):
        dy = ((y - cy) / ry) ** 2
        for x in range(sw):
            d = min(1.0, (((x - cx) / rx) ** 2 + dy) ** 0.5)
            t = d * d
            px[x, y] = tuple(int(CREAM_LIT[i] + (CREAM_DEEP[i] - CREAM_LIT[i]) * t) for i in range(3))
    img = small.resize((W, H), Image.BICUBIC)

    floor = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(floor)
    top = int(H * 0.66)
    for y in range(top, H):
        fd.line([(0, y), (W, y)], fill=(198, 176, 148, int(46 * (y - top) / (H - top))))
    return Image.alpha_composite(img.convert("RGBA"), floor).convert("RGB")


def _blur_layer(img: Image.Image, lay: Image.Image, radius: int) -> None:
    lay = lay.filter(ImageFilter.GaussianBlur(radius))
    img.paste(Image.alpha_composite(img.convert("RGBA"), lay).convert("RGB"), (0, 0))


def ground_shadow(img: Image.Image, cx: int, cy: int, rx: int, ry: int, alpha: int = 66) -> None:
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(150, 122, 88, alpha))
    _blur_layer(img, lay, 26)


def paste_gryphon(img: Image.Image, width: int, cx: int, bottom: int) -> None:
    g = Image.open(ASSETS / "gryphon.png").convert("RGBA")
    h = int(g.height * width / g.width)
    g = g.resize((width, h), Image.LANCZOS)
    ground_shadow(img, cx, bottom - 8, int(width * 0.33), max(12, int(width * 0.042)))
    img.paste(g, (cx - width // 2, bottom - h), g)


def text(d: ImageDraw.ImageDraw, xy, s: str, size: int, weight: str = "regular",
         fill=NAVY, anchor: str = "la", spacing: int = 0) -> None:
    if REFS:
        return
    f = font(size, weight)
    if not spacing:
        d.text(xy, s, font=f, fill=fill, anchor=anchor)
        return
    total = sum(d.textlength(c, font=f) + spacing for c in s) - spacing
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill, anchor="l" + anchor[1])
        x += d.textlength(ch, font=f) + spacing


def card(img: Image.Image, box, radius: int, fill, shadow: int = 40) -> None:
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle(
        [box[0], box[1] + 14, box[2], box[3] + 18], radius, fill=(150, 122, 88, shadow))
    _blur_layer(img, lay, 15)
    ImageDraw.Draw(img).rounded_rectangle(box, radius, fill=fill)


def bezier(p0, p1, p2, p3, n: int = 46) -> list:
    """Cubic bezier as a point list, for the fan-out connectors in scene 2."""
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        pts.append((
            u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0],
            u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1],
        ))
    return pts


# --------------------------------------------------------------------------
# the train: white modern EMU in flat side elevation, per the reference
# --------------------------------------------------------------------------
# Real carriages are 4:1, not 2:1. Ten of them across 1920px forces the wrong
# proportion and they read as a row of cards, so the train runs off both edges
# instead. Scene 2 already names all ten agents; scene 3 only has to say "long,
# and welded".
CAR_W, CAR_H = 330, 88


def _rails(d: ImageDraw.ImageDraw, y: int, scale: float) -> None:
    th = max(3, int(6 * scale))
    for i in range(-40, W + 40, int(34 * scale)):
        d.rounded_rectangle([i, y + th, i + int(15 * scale), y + th + int(8 * scale)],
                            2, fill=CREAM_DEEP)
    d.rounded_rectangle([0, y, W, y + th], th // 2, fill=STEEL_DEEP)


def _bogies(d: ImageDraw.ImageDraw, x: int, w: int, base: int, scale: float) -> None:
    bw, bh = int(78 * scale), int(15 * scale)
    wr = max(5, int(24 * scale / 2))
    for bx in (x + int(w * 0.13), x + int(w * 0.87) - bw):
        d.rounded_rectangle([bx, base, bx + bw, base + bh], int(5 * scale), fill=BOGIE)
        for wx in (bx + int(bw * 0.24), bx + int(bw * 0.76)):
            d.ellipse([wx - wr, base + bh - wr, wx + wr, base + bh + wr], fill=BOGIE)


def draw_car(img: Image.Image, x: int, y: int, label: str, scale: float = 1.0,
             nose: bool = False, accent=None, dim: bool = False) -> int:
    """One carriage in flat side elevation: white body, dark glass band, name on
    the livery. Nose sits on the left, so the train faces the way it reads."""
    d = ImageDraw.Draw(img)
    w, h = int(CAR_W * scale), int(CAR_H * scale)
    body = (248, 250, 252) if not dim else (235, 239, 243)
    edge = STEEL if not dim else STEEL_DEEP
    glass = GLASS if not dim else (108, 120, 134)
    r = int(10 * scale)

    card(img, [x, y, x + w, y + h], r if not nose else int(30 * scale), body, shadow=30)
    d.rounded_rectangle([x, y, x + w, y + h], r if not nose else int(30 * scale),
                        outline=edge, width=max(1, int(1.4 * scale)))
    # roof
    d.rounded_rectangle([x + int(14 * scale), y + int(2 * scale),
                         x + w - int(14 * scale), y + int(9 * scale)], int(3 * scale), fill=edge)
    # skirt
    d.rounded_rectangle([x + int(8 * scale), y + h - int(11 * scale),
                         x + w - int(8 * scale), y + h - int(3 * scale)],
                        int(3 * scale), fill=(228, 234, 240) if not dim else edge)

    # glass band with pillars
    gy0, gy1 = y + int(19 * scale), y + int(46 * scale)
    gx0 = x + int(46 * scale if nose else 20 * scale)
    gx1 = x + w - int(20 * scale)
    d.rounded_rectangle([gx0, gy0, gx1, gy1], int(4 * scale), fill=glass)
    span = gx1 - gx0
    for k in range(1, 5):
        px = gx0 + int(span * k / 5)
        d.rectangle([px - int(3 * scale), gy0, px + int(3 * scale), gy1], fill=body)
    # doors
    for frac in (0.34, 0.70):
        dx = x + int(w * frac)
        d.rounded_rectangle([dx, y + int(16 * scale), dx + int(4 * scale), y + int(64 * scale)],
                            int(2 * scale), fill=edge)
    if nose:   # cab windscreen, raked
        d.polygon([(x + int(8 * scale), y + int(34 * scale)),
                   (x + int(40 * scale), y + int(19 * scale)),
                   (x + int(40 * scale), y + int(46 * scale)),
                   (x + int(10 * scale), y + int(46 * scale))], fill=glass)
    if accent:
        d.rounded_rectangle([x + int(16 * scale), y + int(52 * scale),
                             x + w - int(16 * scale), y + int(56 * scale)],
                            int(2 * scale), fill=accent)

    if LIVERY:
        fs = max(11, int(17 * scale))
        text(d, (x + w // 2, y + int(68 * scale)), label, fs, "bold",
             NAVY if not dim else MUTED, anchor="mm")
    _bogies(d, x, w, y + h, scale)
    return x + w


def draw_coupler(d: ImageDraw.ImageDraw, x: int, y: int, gap: int, scale: float) -> None:
    th = max(4, int(9 * scale))
    cy = y + int(CAR_H * scale * 0.60)
    d.rounded_rectangle([x, cy - th // 2, x + gap, cy + th // 2], th // 2, fill=BOGIE)
    d.rounded_rectangle([x + gap // 2 - int(4 * scale), cy - th,
                         x + gap // 2 + int(4 * scale), cy + th], 3, fill=BLUE)


def draw_train(img: Image.Image, y: int, scale: float, gap: int, x0: int,
               labels: list, coupled: bool = True, lead_nose: bool = True) -> None:
    """A strip of the train. It runs off both edges on purpose."""
    d = ImageDraw.Draw(img)
    x = x0
    for i, label in enumerate(labels):
        x = draw_car(img, x, y, label, scale, nose=(i == 0 and lead_nose),
                     accent=GREEN if (i == 0 and lead_nose) else None)
        if i < len(labels) - 1:
            if coupled:
                draw_coupler(d, x, y, gap, scale)
            x += gap
    _rails(d, y + int(CAR_H * scale) + int(26 * scale), scale)


# --------------------------------------------------------------------------
# the eight frames
# --------------------------------------------------------------------------
def still_01() -> Image.Image:
    img = room()
    paste_gryphon(img, 640, W // 2, 858)
    text(ImageDraw.Draw(img), (W // 2, 962), "I'm Cortex.", HEAD, "bold", NAVY, anchor="mm")
    return img


def still_02() -> Image.Image:
    """One small ask fans out into every agent, and the clock runs.

    A node graph, not a document. This is what people picture when they hear
    'workflow', and it carries the all-or-nothing point far better than a
    vertical chain diagram did.
    """
    img = room()
    d = ImageDraw.Draw(img)

    orb = (250, 470)
    cols = [(560, 176), (900, 176), (1240, 176)]
    rows = [(0, 4), (1, 3), (2, 3)]
    cw, chh, vgap = 176, 58, 26
    boxes = []
    i = 0
    for ci, count in rows:
        cx0, _ = cols[ci]
        span = count * chh + (count - 1) * vgap
        yy = 470 - span // 2
        for _ in range(count):
            boxes.append((cx0, yy, CARRIAGES[i]))
            yy += chh + vgap
            i += 1
    out = (1620, 470)

    # connectors first, so cards sit on top
    for (bx, by, _) in boxes:
        pts = bezier(orb, (orb[0] + 190, orb[1]), (bx - 150, by + chh // 2), (bx, by + chh // 2))
        d.line(pts, fill=(196, 206, 218), width=2, joint="curve")
        pts = bezier((bx + cw, by + chh // 2), (bx + cw + 150, by + chh // 2),
                     (out[0] - 190, out[1]), out)
        d.line(pts, fill=(210, 219, 229), width=2, joint="curve")

    for (bx, by, label) in boxes:
        card(img, [bx, by, bx + cw, by + chh], 12, WHITE, shadow=30)
        d.rounded_rectangle([bx, by, bx + cw, by + chh], 12, outline=(226, 232, 240), width=2)
        d.rounded_rectangle([bx, by + 12, bx + 4, by + chh - 12], 2, fill=BLUE)
        text(d, (bx + 18, by + chh // 2), label, 19, "bold", NAVY, anchor="lm")

    for c, r in ((orb, 56), (out, 44)):
        ImageDraw.Draw(img).ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r],
                                    fill=WHITE, outline=BLUE, width=3)
    text(d, (orb[0], orb[1] + 96), "one small ask", 24, "bold", NAVY, anchor="mm")
    text(d, (out[0], out[1] + 84), "one deliverable", 24, "bold", NAVY, anchor="mm")

    # the clock, showing the real measured runtime
    tb = [1500, 118, 1840, 226]
    card(img, tb, 16, WHITE, shadow=40)
    d.rounded_rectangle(tb, 16, outline=RED, width=3)
    if not REFS:
        d.text(((tb[0] + tb[2]) // 2, (tb[1] + tb[3]) // 2), RUNTIME_CLOCK,
               font=font(58, "mono"), fill=RED, anchor="mm")

    text(d, (W // 2, 880), "Every agent ran. Even for a small job.", HEAD, "bold", NAVY, anchor="mm")
    text(d, (W // 2, 944), "One pipeline, ten agents, all or nothing", SUB, "regular", MUTED, anchor="mm")
    return img


def still_03() -> Image.Image:
    img = room()
    draw_train(img, 430, 1.0, 20, -150,
               ["Presidio gate", "discovery", "journey", "market", "capability", "roi-hypothesis"])
    d = ImageDraw.Draw(img)
    text(d, (W // 2, 236), "TEN CARRIAGES, WELDED TOGETHER", EYEBROW, "bold", MUTED,
         anchor="mm", spacing=5)
    text(d, (W // 2, 748), "Want the ROI model? You ran the whole train.", HEAD, "bold",
         NAVY, anchor="mm")
    text(d, (W // 2, 816), "About 2 hours and real cost", SUB, "regular", MUTED, anchor="mm")
    return img


def still_04() -> Image.Image:
    img = room()
    draw_train(img, 700, 0.86, 18, -120,
               ["Presidio gate", "discovery", "journey", "market", "capability", "roi-hypothesis",
                "benchmark"])
    paste_gryphon(img, 400, W // 2, 540)
    return img


def still_05() -> Image.Image:
    """Tight on the couplings. Nothing has moved apart yet."""
    img = room()
    draw_train(img, 430, 1.55, 46, -140,
               ["capability", "roi-hypothesis", "benchmark", "roi-model"], lead_nose=False)
    return img


def still_06() -> Image.Image:
    """The weld has gone. Carriages stand apart and one has rolled ahead."""
    # Same framing as clip 5 on purpose. Only the couplings change, which is what
    # makes the release read rather than looking like a different shot.
    img = room()
    draw_train(img, 430, 1.55, 150, -240,
               ["capability", "roi-hypothesis", "benchmark", "roi-model"],
               coupled=False, lead_nose=False)
    text(ImageDraw.Draw(img), (W // 2, 880), "Every carriage runs on its own",
         HEAD, "bold", NAVY, anchor="mm")
    return img


def still_07() -> Image.Image:
    """The Claude Code desktop app, light theme, as it actually looks.

    Session titles are internal-only on purpose: the real sidebar carries live
    client names and this film goes to the whole team.
    """
    img = room()
    d = ImageDraw.Draw(img)
    win = [92, 66, 1244, 754]
    card(img, win, 14, WHITE, shadow=58)

    # title bar
    d.rounded_rectangle([win[0], win[1], win[2], win[1] + 40], 14, fill=(246, 245, 243))
    d.rectangle([win[0], win[1] + 26, win[2], win[1] + 40], fill=(246, 245, 243))
    for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
        cx = win[0] + 26 + i * 22
        d.ellipse([cx - 6, win[1] + 14, cx + 6, win[1] + 26], fill=c)

    # sidebar
    sb = win[0] + 262
    d.rectangle([win[0], win[1] + 40, sb, win[3]], fill=(247, 246, 244))
    d.line([(sb, win[1] + 40), (sb, win[3])], fill=(232, 230, 226), width=1)
    d.rounded_rectangle([win[0] + 14, win[1] + 56, sb - 14, win[1] + 90], 8, fill=(236, 234, 230))
    text(d, (win[0] + 30, win[1] + 73), "+  New", 17, "bold", NAVY, anchor="lm")
    for i, row in enumerate(["Artifacts", "Customize", "More"]):
        text(d, (win[0] + 30, win[1] + 118 + i * 32), row, 17, "regular", (74, 84, 96), anchor="lm")
    text(d, (win[0] + 30, win[1] + 240), "value-consulting-agents", 15, "bold", MUTED, anchor="lm")
    for i, row in enumerate(SESSIONS):
        text(d, (win[0] + 30, win[1] + 276 + i * 32), row, 16, "regular", (74, 84, 96), anchor="lm")
    d.ellipse([win[0] + 22, win[3] - 44, win[0] + 46, win[3] - 20], fill=(214, 120, 88))
    text(d, (win[0] + 58, win[3] - 32), "Mariam · Max", 15, "regular", (74, 84, 96), anchor="lm")

    # main pane
    mid = (sb + win[2]) // 2
    d.ellipse([mid - 172, win[1] + 96, mid - 152, win[1] + 116], fill=(214, 120, 88))
    text(d, (mid + 6, win[1] + 106), "Welcome back, Mariam", 27, "bold", NAVY, anchor="mm")

    # the ask
    box = [sb + 40, win[3] - 190, win[2] - 40, win[3] - 108]
    d.rounded_rectangle(box, 12, fill=WHITE, outline=(216, 220, 226), width=2)
    d.text((box[0] + 22, (box[1] + box[3]) // 2), "/frontline",
           font=font(24, "mono"), fill=NAVY, anchor="lm")
    cx = box[0] + 22 + d.textlength("/frontline", font=font(24, "mono")) + 8
    d.rectangle([cx, (box[1] + box[3]) // 2 - 14, cx + 12, (box[1] + box[3]) // 2 + 14], fill=BLUE)

    chips = ["Local", "value-consulting-agents", "mariamt/2026…"]
    x = box[0]
    for ch in chips:
        w = int(d.textlength(ch, font=font(15))) + 26
        d.rounded_rectangle([x, box[3] + 14, x + w, box[3] + 44], 8, fill=(244, 243, 241))
        text(d, (x + 13, box[3] + 29), ch, 15, "regular", (86, 96, 108), anchor="lm")
        x += w + 10
    text(d, (win[2] - 40, box[3] + 29), "Opus 5   High", 15, "regular", MUTED, anchor="rm")

    paste_gryphon(img, 520, 1580, 1010)
    text(d, (92, 862), "Need a deck? Ask for the deck.", HEAD, "bold", NAVY)
    return img


def still_08(pending: list) -> Image.Image:
    img = room()
    d = ImageDraw.Draw(img)
    text(d, (W // 2, 258), "And there's more coming", HEAD, "bold", NAVY, anchor="mm")
    cw, chh, gap = 300, 190, 26
    lifts = [32, 10, 0, 10, 32]
    x = (W - (5 * cw + 4 * gap)) // 2
    for i, (cmd, name) in enumerate(pending[:5]):
        y = 500 + lifts[i]
        card(img, [x, y, x + cw, y + chh], 20, WHITE, shadow=46)
        d.rounded_rectangle([x, y, x + cw, y + chh], 20, outline=CREAM_DEEP, width=2)
        size = 23 if d.textlength(cmd, font=font(23, "mono")) < cw - 60 else 19
        d.text((x + 30, y + 42), cmd, font=font(size, "mono"), fill=BLUE)
        text(d, (x + 30, y + 100), name, 21, "regular", MUTED)
        x += cw + gap
    return img


def still_09() -> Image.Image:
    """The sign-off. Deliberately the same composition as clip 1, so the film
    closes where it opened, and it points at the cheat sheet rather than just
    ending."""
    img = room()
    paste_gryphon(img, 600, W // 2, 806)
    d = ImageDraw.Draw(img)
    text(d, (W // 2, 900), "Everything Cortex can do, on one page", HEAD, "bold", NAVY, anchor="mm")
    text(d, (W // 2, 964), "cortex-cheat-sheet.html", SUB, "regular", MUTED, anchor="mm")
    return img


def main() -> int:
    global REFS, LIVERY
    REFS = "--refs" in sys.argv
    LIVERY = "--no-livery" not in sys.argv
    out = (OUT / "refs") if REFS else (OUT if LIVERY else OUT / "plain")
    out.mkdir(exist_ok=True)
    pending = pending_skills()
    if len(pending) != 5:
        print(f"expected 5 pending catalog entries, found {len(pending)}", file=sys.stderr)
        return 1

    shots = {
        "01-hello": still_01,
        "02-pipeline": still_02,
        "03-train": still_03,
        "04-flyover": still_04,
        "05-couplings": still_05,
        "06-split": still_06,
        "07-tutorial": still_07,
        "08-coming": lambda: still_08(pending),
        "09-goodbye": still_09,
    }
    # 7 and 8 exist to be read, not admired. They are never emitted as refs.
    if REFS:
        for locked in ("07-tutorial", "08-coming"):
            shots.pop(locked)

    for name, fn in shots.items():
        p = out / f"{name}.png"
        fn().save(p, "PNG", optimize=True)
        print(f"  {p.relative_to(ROOT)}  {p.stat().st_size // 1024} KB")
    if REFS:
        print(f"\n{len(shots)} layout references at {W}x{H}, no text. "
              "Runway is free to reinterpret these.")
    elif not LIVERY:
        print(f"\n{len(shots)} frames at {W}x{H}: captions kept, carriage names "
              "dropped so there is nothing to misspell.")
    else:
        print(f"\n{len(shots)} locked start frames at {W}x{H}. Runway supplies motion only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
