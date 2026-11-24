"""Render iOS WhatsApp (dark) chat screenshots and caption photo slides in the account's square look.

Real assets (all in this folder):
  ios_header.png      the current iOS WhatsApp header bar (glass back button, avatar, Apple heart emoji,
                      video/call pill), lifted from real iPhone 16 Pro Max screenshots
  ios_wall_strip.png  the real iOS doodle wallpaper, rebuilt pixel-for-pixel from dozens of real screenshots
                      (row r = wallpaper phase r + WALL_PHASE0; the wallpaper is fixed to the screen)
  SF-Pro-Text-Regular.otf  Apple's iOS font, drawn with its real kerning (sftext.py)
Caption slides copy the account's old Rizz Studio captions: Proxima Nova Semibold, thick black outline.

Usage: python wa_render.py story.json out_dir
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sftext import layout as sf_layout  # noqa: E402

SS = 2
W1 = 1320
FONT_MSG = os.path.join(HERE, "SF-Pro-Text-Regular.otf")
FONT_CAP = os.path.join(HERE, "Proxima-Nova-Semibold.otf")
WALL = os.path.join(HERE, "ios_wall_strip.png")
WALL_PHASE0 = 196
HEADER = os.path.join(HERE, "ios_header.png")
HEADER_H = 214           # header bar ends here; wallpaper phase == canvas row on header slides

C_IN = (34, 38, 37)
C_OUT = (22, 76, 53)
C_TEXT = (255, 255, 255)
C_TIME_IN = (178, 181, 180)
C_TIME_OUT = (168, 203, 187)

# type (1x px) - SF Pro Text 19pt @3x, tracking fitted to real screenshots
MSG_SIZE, MSG_TRACK = 57, -1.7
TIME_SIZE, TIME_TRACK = 42, 0.5

# bubble metrics (1x px), measured from real screenshots
MARGIN_IN = 49
MARGIN_OUT = 52
MAX_BUBBLE = 1006        # widest real bubble measured across 100+ screenshots
TEXT_MAX = 934           # widest real text line is 931-932px ink on both sides -> wrap limit
PAD_L = 37
PAD_R_IN = 41
PAD_R_OUT = 31
TIME_GAP = 54
TICK_GAP = 10
TICK_W = 52
LINE1_BASE = 76
LINE_PITCH = 72
BUBBLE_1LINE = 128
TIME_FROM_BOTTOM = 24
OWN_TIME_LINE = 46
RADIUS = 53
GAP_SAME = 15
GAP_CHANGE = 42
FIRST_BUBBLE_HDR = 257   # first bubble top under the header bar
TOP_MARGIN = 44          # first bubble top on slides without the header (square look)
BOTTOM_MARGIN = 20
WALL_TOP = 300           # wallpaper phase shown at the top of slides without the header

TAIL = [(0, -60), (0, -36), (1, -30), (2, -25), (3, -20), (5, -15), (8, -11), (11, -7), (14, -3), (17, 0),
        (13, 0.5), (9, 0), (5, -1.5), (1, -3), (-3, -4.5), (-7, -6.5), (-11, -9), (-16, -11.5), (-21, -13), (-21, -60)]


def S(v):
    return v * SS


_fonts = {}


def font(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def sf_width(text, size, track):
    return sf_layout(text, FONT_MSG, size, track)[1] if text else 0


def sf_draw(d, x, base, text, size, track, fill):
    f = font(FONT_MSG, size)
    for ch, cx in sf_layout(text, FONT_MSG, size, track)[0]:
        d.text((x + cx, base), ch, font=f, fill=fill, anchor="ls")


def wrap(text, maxw, measure):
    lines, cur = [], ""
    for w in text.split(" "):
        t = f"{cur} {w}" if cur else w
        if measure(t) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def smart(text, sender):
    """iPhone sender gets curly apostrophes; the other side keeps straight ones (as in real chats)."""
    return text.replace("'", "’") if sender == "me" else text


# ---------------------------------------------------------------- background
_wall = None


def wall_window(phase, h):
    global _wall
    if _wall is None:
        _wall = Image.open(WALL).convert("RGB")
    top = phase - WALL_PHASE0
    if top < 0 or top + h > _wall.height:
        raise ValueError(f"wallpaper window {phase}..{phase + h} is outside the rebuilt band")
    return _wall.crop((0, top, W1, top + h))


# ---------------------------------------------------------------- bubbles
def ticks(d, x, base, color):
    w = S(4.8)
    a = [(x + S(1), base - S(13)), (x + S(11), base - S(2)), (x + S(34), base - S(28))]
    b = [(x + S(21), base - S(6)), (x + S(25), base - S(2)), (x + S(48), base - S(28))]
    for pts in (a, b):
        d.line(pts, fill=color, width=round(w), joint="curve")
        for p in (pts[0], pts[-1]):
            d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=color)


def layout(msgs, has_header):
    y = FIRST_BUBBLE_HDR if has_header else TOP_MARGIN
    out = []
    for i, m in enumerate(msgs):
        me = m["sender"] == "me"
        text = smart(m["text"], m["sender"])
        pad_r = PAD_R_OUT if me else PAD_R_IN
        tblock = sf_width(m["time"], TIME_SIZE, TIME_TRACK) + ((TICK_GAP + TICK_W) if me else 0)
        maxw = TEXT_MAX
        meas = lambda t: sf_width(t, MSG_SIZE, MSG_TRACK)
        lines = wrap(text, maxw, meas)
        if m.get("no_orphan") and len(lines) > 1 and len(lines[-1].split()) < 2:  # split() also breaks on NBSP
            # opt-in: the widest narrower wrap with the same line count that doesn't leave one word alone
            for wmax in range(int(maxw), int(maxw * 0.5), -4):
                L = wrap(text, wmax, meas)
                if len(L) == len(lines) and len(L[-1].split()) > 1 and max(meas(l) for l in L) <= wmax:
                    lines = L
                    break
        widths = [sf_width(l, MSG_SIZE, MSG_TRACK) for l in lines]
        inline = widths[-1] + TIME_GAP + tblock <= maxw
        inner = max(max(widths), widths[-1] + TIME_GAP + tblock) if inline else max(max(widths), tblock)
        bw = round(PAD_L + inner + pad_r)
        bh = BUBBLE_1LINE + LINE_PITCH * (len(lines) - 1) + (0 if inline else OWN_TIME_LINE)
        if i > 0:
            y += GAP_SAME if msgs[i - 1]["sender"] == m["sender"] else GAP_CHANGE
        x0 = (W1 - MARGIN_OUT - bw) if me else MARGIN_IN
        out.append(dict(m=m, me=me, lines=lines, x0=x0, y0=y, w=bw, h=bh, tblock=tblock, pad_r=pad_r))
        y += bh
    return out, y + BOTTOM_MARGIN


def render_chat(msgs, next_sender, out_path, has_header=False, min_h=0, wall_top=WALL_TOP):
    boxes, H = layout(msgs, has_header)
    H = max(H, min_h)
    # 1x background: real header + real wallpaper
    if has_header:
        bg = Image.new("RGB", (W1, H), (17, 17, 17))
        bg.paste(wall_window(HEADER_H - 1, H - HEADER_H + 1), (0, HEADER_H - 1))
        hdr = Image.open(HEADER).convert("RGB")
        bg.paste(hdr.crop((0, 0, W1, HEADER_H - 1)), (0, 0))
        # keep the real 1px anti-aliased bar edge
        edge = hdr.crop((0, HEADER_H - 1, W1, HEADER_H))
        under = bg.crop((0, HEADER_H - 1, W1, HEADER_H))
        bg.paste(Image.blend(under, edge, 0.5), (0, HEADER_H - 1))
    else:
        bg = wall_window(wall_top, H)
    # 2x bubble layer
    lay = Image.new("RGBA", (S(W1), S(H)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i, b in enumerate(boxes):
        nxt = boxes[i + 1]["m"]["sender"] if i + 1 < len(boxes) else next_sender
        tail = nxt != b["m"]["sender"]
        col = C_OUT if b["me"] else C_IN
        x0, y0, x1, y1 = b["x0"], b["y0"], b["x0"] + b["w"], b["y0"] + b["h"]
        d.rounded_rectangle([S(x0), S(y0), S(x1), S(y1)], radius=S(RADIUS), fill=col)
        if tail:
            if b["me"]:
                pts = [(S(x1 + px), S(y1 + py)) for px, py in TAIL]
            else:
                pts = [(S(x0 - px), S(y1 + py)) for px, py in TAIL]
            d.polygon(pts, fill=col)
        base = y0 + LINE1_BASE
        for ln in b["lines"]:
            sf_draw(d, S(x0 + PAD_L), S(base), ln, S(MSG_SIZE), S(MSG_TRACK), C_TEXT)
            base += LINE_PITCH
        tb = y1 - TIME_FROM_BOTTOM
        tx = x1 - b["pad_r"] - b["tblock"]
        sf_draw(d, S(tx), S(tb), b["m"]["time"], S(TIME_SIZE), S(TIME_TRACK), C_TIME_OUT if b["me"] else C_TIME_IN)
        if b["me"]:
            ticks(d, S(x1 - b["pad_r"] - TICK_W), S(tb), C_TIME_OUT)
    # premultiplied downsample so edges blend cleanly onto the 1x background
    r, g, bl, a = lay.split()
    pm = Image.merge("RGB", [Image.composite(c, Image.new("L", lay.size, 0), a) for c in (r, g, bl)])
    pm = pm.resize((W1, H), Image.LANCZOS)
    a1 = a.resize((W1, H), Image.LANCZOS)
    # out = bg*(1-a) + pm  (pm already premultiplied)
    A = np.asarray(a1, dtype=np.float32)[..., None] / 255.0
    res = np.asarray(bg, dtype=np.float32) * (1 - A) + np.asarray(pm, dtype=np.float32)
    Image.fromarray(np.clip(res, 0, 255).round().astype("uint8")).save(out_path)
    return (W1, H)


# ---------------------------------------------------------------- caption slides (old Rizz Studio look)
def cap_width(f, s):
    return f.getlength(s)


def render_caption(photo, text, out_path, size=(1320, 1320), fx=0.5, fy=0.4, zoom=1.0, hook=False, cy=0.5):
    # measured on the account's old 1080x1080 slides: Proxima Nova Semibold 63px (hook 80px),
    # line pitch 81px (hook 103px), solid black outline ~8.5px, centred; scaled here to 1320
    k = size[0] / 1080
    fs = (80 if hook else 63) * k
    pitch = (103 if hook else 81) * k
    outline = 8.5 * k
    maxw = 920 * k
    im = Image.open(photo).convert("RGB")
    tw_, th_ = size
    r = tw_ / th_
    w, h = im.size
    cw, ch = (h * r, h) if w / h > r else (w, w / r)
    cw, ch = cw / zoom, ch / zoom
    cx, cyy = w * fx, h * fy
    x0 = min(max(cx - cw / 2, 0), w - cw)
    y0 = min(max(cyy - ch / 2, 0), h - ch)
    im = im.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((S(tw_), S(th_)), Image.LANCZOS)
    f = font(FONT_CAP, S(fs))
    lines = []
    for part in text.split("\n"):  # "\n" in the spec forces a line break
        lines += wrap(part, S(maxw), lambda t: cap_width(f, t))
    # balance a short last line (no orphan words)
    if "\n" not in text and len(lines) >= 2 and len(lines[-1].split()) == 1 and len(lines[-2].split()) > 2:
        prev = lines[-2].split()
        lines[-2], lines[-1] = " ".join(prev[:-1]), prev[-1] + " " + lines[-1]
    asc = f.getbbox("H")[1]
    capH = f.getbbox("H")[3] - asc
    total = S(pitch) * (len(lines) - 1) + capH
    base0 = S(th_ * cy) - total / 2 + capH
    # outline + soft shadow layer, then white fill on top (paint-order: stroke, fill)
    stroke = Image.new("L", im.size, 0)
    sd = ImageDraw.Draw(stroke)
    fill = Image.new("L", im.size, 0)
    fd = ImageDraw.Draw(fill)
    for i, ln in enumerate(lines):
        x = (S(tw_) - cap_width(f, ln)) / 2
        base = base0 + i * S(pitch)
        sd.text((x, base), ln, font=f, fill=255, anchor="ls", stroke_width=round(S(outline)), stroke_fill=255)
        fd.text((x, base), ln, font=f, fill=255, anchor="ls")
    shadow = stroke.filter(ImageFilter.GaussianBlur(S(6))).point(lambda v: int(v * 0.35))
    shadow = shadow.transform(shadow.size, Image.AFFINE, (1, 0, 0, 0, 1, -S(2)))
    black = Image.new("RGB", im.size, (0, 0, 0))
    im = Image.composite(black, im, shadow)
    im = Image.composite(black, im, stroke)
    im = Image.composite(Image.new("RGB", im.size, (255, 255, 255)), im, fill)
    im.resize(size, Image.LANCZOS).save(out_path)


# ---------------------------------------------------------------- story
def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    slides = spec["slides"]
    square = spec.get("square", True)  # the account's look: every slide 1320x1320
    chats = [s for s in slides if s["type"] == "chat"]
    header_left = spec.get("header_slides", 1)
    for n, s in enumerate(slides, 1):
        name = os.path.join(out, f"slide-{n:02d}.png")
        if s["type"] == "chat":
            k = chats.index(s)
            nxt = None
            if k + 1 < len(chats):
                nxt = chats[k + 1]["msgs"][0]["sender"]
                if chats[k + 1].get("repeat_first"):
                    nxt = chats[k + 1]["msgs"][1]["sender"] if len(chats[k + 1]["msgs"]) > 1 else None
            hh = header_left > 0
            header_left -= 1
            size = render_chat(s["msgs"], nxt, name, has_header=hh, min_h=W1 if square else 0,
                               wall_top=s.get("wall_top", spec.get("wall_top", WALL_TOP)))
            print(name, size)
        elif s["type"] == "photo":
            render_caption(s["photo"], s["text"], name, size=(W1, W1),
                           fx=s.get("fx", 0.5), fy=s.get("fy", 0.4), zoom=s.get("zoom", 1.0),
                           hook=(n == 1), cy=s.get("cy", 0.5))
            print(name, "photo")
        else:
            print(name, "card (made separately)")


if __name__ == "__main__":
    main()
