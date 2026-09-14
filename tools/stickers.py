#!/usr/bin/env python3
"""Generate img/stickers.svg — the app's kiss-cut game and object stickers,
ported from ios/Bord/Prototypes/BordNew/BNGameStickers.swift (bord repo).

Every symbol lives in a 128-unit box (viewBox -64 -64 128 128) where the
sticker's `size` is 100 units, so a symbol placed at CSS width 1.28 × size
renders the sticker at `size` with room for the kiss-cut and the overhang.

The kiss-cut is the app's trick verbatim: every hull shape is drawn twice —
a white twin underneath, stroked at 2 × 0.05 × size with round joins and
filled white, then the coloured art on top. Adjacent twins fuse, so a tower
or a train reads as one die-cut piece. No backing plate.
"""
import colorsys, math, os

PAPER, INK, COVER, COVER_DEEP = "#FCFAF5", "#3D2F21", "#DAC7A5", "#BDA784"
BLUSH, BUTTER, MATCHA, SKY = "#ECBFBF", "#F6E19C", "#C4D5B1", "#BAD0E1"
TERRA, TARO, LILAC, GOLD = "#E6B496", "#CFC4E0", "#DDCFDD", "#E0BF73"
BERRY, JADE, ACCENT = "#B24438", "#3E7351", "#7C5CC4"
WHITE = "#FFFFFF"
KISS = 10  # 2 × 0.05 × 100

def hexrgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
def rgbhex(r, g, b):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(c * 255))) for c in (r, g, b))
def darkened(h, x):   # Color.bnDarkened — HSB: s + 0.35x, b - x
    hh, s, v = colorsys.rgb_to_hsv(*hexrgb(h))
    return rgbhex(*colorsys.hsv_to_rgb(hh, min(1, s + 0.35 * x), max(0, v - x)))
def lightened(h, x):  # Color.bnLightened — HSB: s - 0.55x, b + x
    hh, s, v = colorsys.rgb_to_hsv(*hexrgb(h))
    return rgbhex(*colorsys.hsv_to_rgb(hh, max(0, s - 0.55 * x), min(1, v + x)))

def f(x): return ("%.2f" % x).rstrip("0").rstrip(".")

# --- primitives, all returning path data centred at (cx, cy) ---------------
def rrect(cx, cy, w, h, r):
    x, y = cx - w / 2, cy - h / 2
    r = min(r, w / 2, h / 2)
    return (f"M{f(x+r)} {f(y)}H{f(x+w-r)}A{f(r)} {f(r)} 0 0 1 {f(x+w)} {f(y+r)}V{f(y+h-r)}"
            f"A{f(r)} {f(r)} 0 0 1 {f(x+w-r)} {f(y+h)}H{f(x+r)}A{f(r)} {f(r)} 0 0 1 {f(x)} {f(y+h-r)}"
            f"V{f(y+r)}A{f(r)} {f(r)} 0 0 1 {f(x+r)} {f(y)}Z")
def capsule(cx, cy, w, h): return rrect(cx, cy, w, h, min(w, h) / 2)
def ellipse(cx, cy, w, h):
    rx, ry = w / 2, h / 2
    return (f"M{f(cx-rx)} {f(cy)}A{f(rx)} {f(ry)} 0 1 0 {f(cx+rx)} {f(cy)}"
            f"A{f(rx)} {f(ry)} 0 1 0 {f(cx-rx)} {f(cy)}Z")
def circle(cx, cy, d): return ellipse(cx, cy, d, d)
def tri(cx, cy, w, h):  # PTriangle: apex up, base down
    return f"M{f(cx)} {f(cy-h/2)}L{f(cx+w/2)} {f(cy+h/2)}L{f(cx-w/2)} {f(cy+h/2)}Z"
def rhex(cx, cy, w, h, corner=0.21):
    """BNRoundedHex: pointy-top, R = min(w/2/0.866, h/2), each corner cut back by
    corner·R along both edges and re-joined with a quad through the corner."""
    R = min(w / 2 / 0.8660254, h / 2)
    pts = [(cx + R * math.cos(math.radians(i * 60 - 90)), cy + R * math.sin(math.radians(i * 60 - 90))) for i in range(6)]
    cut = corner * R
    d = ""
    for i, p in enumerate(pts):
        prev, nxt = pts[i - 1], pts[(i + 1) % 6]
        def toward(a, b, dist):
            L = math.hypot(b[0] - a[0], b[1] - a[1]); return (a[0] + (b[0] - a[0]) / L * dist, a[1] + (b[1] - a[1]) / L * dist)
        a, b = toward(p, prev, cut), toward(p, nxt, cut)
        d += (f"M{f(a[0])} {f(a[1])}" if i == 0 else f"L{f(a[0])} {f(a[1])}") + f"Q{f(p[0])} {f(p[1])} {f(b[0])} {f(b[1])}"
    return d + "Z"
def star(cx, cy, d):  # BNStarShape5: rIn = 0.4 rOut, first point at -90°
    ro, ri = d / 2, d / 2 * 0.4
    pts = []
    for i in range(10):
        r = ro if i % 2 == 0 else ri
        a = math.radians(-90 + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts) + "Z"
def meeple(cx, cy, w, h):  # PMeeple, verbatim
    x0, y0 = cx - w / 2, cy - h / 2
    X = lambda k: f(x0 + w * k); Y = lambda k: f(y0 + h * k)
    head = ellipse(x0 + w * 0.50, y0 + h * 0.18, w * 0.40, h * 0.36)
    body = (f"M{X(.36)} {Y(.34)}Q{X(.10)} {Y(.36)} {X(.04)} {Y(.58)}Q{X(.06)} {Y(.70)} {X(.22)} {Y(.66)}"
            f"L{X(.12)} {Y(1)}L{X(.42)} {Y(1)}Q{X(.50)} {Y(.86)} {X(.58)} {Y(1)}L{X(.88)} {Y(1)}"
            f"L{X(.78)} {Y(.66)}Q{X(.94)} {Y(.70)} {X(.96)} {Y(.58)}Q{X(.90)} {Y(.36)} {X(.64)} {Y(.34)}Z")
    return head + body
def smile(cx, cy, w, h):  # BNSmile, the digitised mouth polyline
    pts = [(0,.28),(.07,.48),(.16,.66),(.28,.82),(.41,.93),(.50,.96),(.59,.94),(.72,.84),(.84,.68),(.93,.49),(1,.30)]
    return "M" + "L".join(f"{f(cx - w/2 + px*w)} {f(cy - h/2 + py*h)}" for px, py in pts)

def P(d, fill=None, stroke=None, sw=None, op=None, extra=""):
    a = [f'd="{d}"']
    a.append(f'fill="{fill}"' if fill else 'fill="none"')
    if stroke: a.append(f'stroke="{stroke}"')
    if sw: a.append(f'stroke-width="{f(sw)}"')
    if op is not None: a.append(f'opacity="{f(op)}"')
    if extra: a.append(extra)
    return "<path " + " ".join(a) + "/>"
def hull(*ds):  # the white twin pass
    return "".join(P(d, WHITE, WHITE, KISS, extra='stroke-linejoin="round"') for d in ds)
def glint(x, y, size, op=1.0):
    """BNJellyGlint: glossy objects only. Anchored top-leading of the object box."""
    return (P(circle(x + .20 * size, y + .16 * size, .20 * size), WHITE, op=.85 * op)
            + P(circle(x + .40 * size, y + .38 * size, .08 * size), WHITE, op=.68 * op))
def rot(deg, cx=0, cy=0): return f'transform="rotate({f(deg)} {f(cx)} {f(cy)})"'
def G(inner, extra=""): return f"<g {extra}>{inner}</g>"

S = 100
symbols = {}

# 1 Catan — the hex island (house sits at (−0.30, −0.22))
hexd = rhex(0, 0, .72 * S, .72 * S)
roof = tri(-30, -27, 17, 10); body = rrect(-30, -17, 13, 10, 0)
symbols["catan"] = (hull(hexd, roof, body)
    + P(hexd, TERRA, INK, 1, extra='stroke-opacity=".25"')
    + "".join(P(capsule(0, 10 + (i - 1) * 8.2, w * S, 3.2), GOLD, op=.85) for i, w in enumerate((.26, .22, .18)))
    + P(body, PAPER, INK, .8, extra='stroke-opacity=".3"') + P(circle(-30, -17, 3.5), SKY, op=.8)
    + P(roof, BLUSH, INK, .8, extra='stroke-opacity=".3" stroke-linejoin="round"'))

# 2 Wingspan — the bird
bodyd = ellipse(-4, -2, 54, 46); headd = circle(16, -18, 30)
taild = tri(-31, 0, 18, 14); wingd = ellipse(-8, 2, 28, 17)
egg = ellipse(24, 20, 15, 18.5)
symbols["wingspan"] = (hull(bodyd, headd, egg) + G(hull(taild), rot(-115, -31, 0))
    + G(P(taild, darkened(SKY, .10)), rot(-115, -31, 0))
    + P(bodyd, SKY) + P(headd, SKY)
    + G(P(wingd, darkened(SKY, .13), WHITE, 1.4, extra='stroke-opacity=".5"'), rot(-14, -8, 2))
    + G(P(tri(33, -16, 9, 11), GOLD), rot(90, 33, -16))
    + P(circle(20, -21, 8.5), INK) + glint(15.75, -25.25, 8.5)
    + P(ellipse(25, -11, 7.5, 5), BLUSH, op=.7)
    + P(egg, PAPER, INK, .8, extra='stroke-opacity=".22"')
    + P(circle(22, 17, 2), COVER_DEEP, op=.5) + P(circle(26.5, 23, 1.6), COVER_DEEP, op=.5))

# 3 Jenga — the block tower (five rows; one pulled pair, the pulled block blush)
rows = []; y = -29.8
long_w, blk_h, gap = 56, 10.8, 1.4
for r in range(5):
    cy = y + blk_h / 2
    if r % 2 == 0: rows.append([(0, cy, long_w, False)])
    else:
        w = (long_w - gap) / 2
        rows.append([(-(w / 2 + gap / 2) + (-3 if r == 1 else 0), cy, w, r == 1), ((w / 2 + gap / 2), cy, w, False)])
    y += blk_h + gap
blocks = [(rrect(cx, cy, w, blk_h, blk_h * .3), pulled) for row in rows for cx, cy, w, pulled in row]
symbols["jenga"] = (hull(*[d for d, _ in blocks])
    + "".join(P(d, BLUSH if pulled else COVER, INK, .8, extra='stroke-opacity=".25"') for d, pulled in blocks))

# 4 Uno — the card fan (two cards, ∓11° about the bottom, sky and blush)
def card(dx, ang, fill):
    d = rrect(dx, 0, 36, 52, 5.5); e = ellipse(dx, 0, 20, 32)
    return (G(hull(d), rot(ang, dx, 26)),
            G(P(d, fill, WHITE, 2.6) + G(P(e, WHITE, WHITE, 2.4, op=.9), rot(28, dx, 0)), rot(ang, dx, 26)))
c1, c2 = card(-7.5, -11, SKY), card(7.5, 11, BLUSH)
symbols["uno"] = c1[0] + c2[0] + c1[1] + c2[1]

# 5 Codenames — the word card wearing glasses
cardd = rrect(0, 4, 66, 44, 6)
lensL, lensR = circle(-11, -16, 18), circle(11, -16, 18)
symbols["codenames"] = (hull(cardd, lensL, lensR)
    + P(cardd, PAPER, INK, 1, extra='stroke-opacity=".3"')
    + P(capsule(0, 13.5, 34, 7), INK, op=.72)
    + P(ellipse(-21, 6, 9, 5.5), BLUSH, op=.75) + P(ellipse(21, 6, 9, 5.5), BLUSH, op=.75)
    + P(lensL, SKY, INK, 2.8, extra='fill-opacity=".45"') + P(lensR, SKY, INK, 2.8, extra='fill-opacity=".45"')
    + P(rrect(0, -16, 5, 2.4, 0), INK))

# 6 Ticket to Ride — the train
cab = rrect(-20, -4, 22, 34, 5); boiler = capsule(8, 4, 46, 22); dome = circle(8, -10, 10)
wL, wR = circle(-14, 18, 16), circle(14, 18, 16); steam = circle(-22, -30, 9)
symbols["ticket"] = (hull(cab, boiler, dome, wL, wR, steam)
    + P(steam, WHITE, op=.9)
    + P(cab, TARO) + P(rrect(-20, -9, 11.5, 11.5, 1.5), SKY, op=.65)
    + P(boiler, BLUSH) + P(capsule(8, 4, 40, 16), None, WHITE, 1.4, extra='stroke-opacity=".55"')
    + P(dome, GOLD)
    + "".join(P(w, GOLD, INK, 1.2, extra='stroke-opacity=".4"') + P(rrect(cx, 18, 1.5, 12, .7), INK, op=.4) + glint(cx - 8, 10, 16, .7)
              for w, cx in ((wL, -14), (wR, 14))))

# 7 Sushi Go — the nigiri
rice = rrect(0, 6, 54, 28, 11); salmon = rrect(0, -6, 60, 20, 10); nori = rrect(0, 0, 13, 37, 2)
symbols["sushi"] = (hull(rice, salmon, nori)
    + P(rice, PAPER, INK, .8, extra='stroke-opacity=".2"')
    + G(P(capsule(-14, 12, 3, 1.5), COVER_DEEP, op=.55), rot(20, -14, 12)) + G(P(capsule(16, 13, 3, 1.5), COVER_DEEP, op=.55), rot(-15, 16, 13))
    + P(salmon, BLUSH) + P(rrect(0, -9, 34, 1.8, .9), WHITE, op=.6) + P(rrect(0, -3, 34, 1.8, .9), WHITE, op=.6)
    + glint(-30, -16, 32, .8) + P(nori, INK, op=.82))

# 8 Azul — the azulejo
tile = rrect(0, 0, 60, 60, 7)
symbols["azul"] = (hull(tile) + P(tile, TARO, INK, 1, extra='stroke-opacity=".25"')
    + G(P(rrect(0, 0, 34, 34, 3), PAPER), rot(45)) + P(circle(0, 0, 10), BLUSH)
    + "".join(P(circle(23.5 * math.cos(math.radians(a)), 23.5 * math.sin(math.radians(a)), 4.5), PAPER, op=.9) for a in (45, 135, 225, 315))
    + glint(-30, -30, 55, .45))

# 9 Exploding Kittens — the kitten
loaf = rrect(0, 4, 56, 42, 17); earL, earR = tri(-18, -22, 17, 15), tri(18, -22, 17, 15)
symbols["kittens"] = (G(hull(earL), rot(-8, -18, -22)) + G(hull(earR), rot(8, 18, -22)) + hull(loaf)
    + G(P(earL, TARO) + P(tri(-18, -20, 9, 8), BLUSH, op=.6), rot(-8, -18, -22))
    + G(P(earR, TARO) + P(tri(18, -20, 9, 8), BLUSH, op=.6), rot(8, 18, -22))
    + P(loaf, TARO)
    + P(smile(-10, 0, 10, 4), None, INK, 2.4, extra='stroke-linecap="round" stroke-linejoin="round"')
    + P(smile(10, 0, 10, 4), None, INK, 2.4, extra='stroke-linecap="round" stroke-linejoin="round"')
    + P(ellipse(-17, 7, 9, 5.5), BLUSH, op=.8) + P(ellipse(17, 7, 9, 5.5), BLUSH, op=.8)
    + G(P(tri(0, 7, 5, 4), BERRY, op=.85), rot(180, 0, 7))
    + "".join(G(P(capsule(sx * 26, y, 12, 1.4), INK, op=.45), rot(sx * -8 * (1 if y == 4 else -1), sx * 26, y)) for sx in (-1, 1) for y in (4, 10)))

# 10 Chess — the pawn
head = circle(0, -19.5, 20); pbody = tri(0, 2, 28, 28); collar = capsule(0, 6, 24, 4.5); base = capsule(0, 20, 38, 8.5)
symbols["chess"] = (hull(head, pbody, collar, base) + P(pbody, TARO) + P(collar, darkened(TARO, .08))
    + P(base, darkened(TARO, .06)) + P(head, TARO) + glint(-10, -29.5, 20, .55))

# Objects ----------------------------------------------------------------
# Meeple (glossy plastic: one glint dot on the head)
mp = meeple(0, 0, 60, 68)
symbols["meeple"] = hull(mp) + P(mp, MATCHA) + P(circle(-4, -17, 7.8), WHITE, op=.8)
for name, col in (("meeple-sky", SKY), ("meeple-blush", BLUSH), ("meeple-taro", TARO), ("meeple-accent", ACCENT)):
    symbols[name] = hull(mp) + P(mp, col) + P(circle(-4, -17, 7.8), WHITE, op=.8)

# Star — earned things only
sd = star(0, 0, 76)
symbols["star"] = (hull(sd) + P(sd, GOLD, WHITE, .8, extra='stroke-opacity=".45" stroke-linejoin="round"')
    + P(circle(22, 16, 10.6), WHITE, op=.75))

# Trophy
cup = (f"M-26 -22 Q-26 -28 -20 -28 H20 Q26 -28 26 -22 V-2 Q26 22 0 22 Q-26 22 -26 -2 Z")
hL, hR = circle(-34, -6, 26), circle(34, -6, 26)
stem = rrect(0, 28, 10, 12, 0); tbase = rrect(0, 39, 38, 10, 2)
symbols["trophy"] = (P(hL, "none", WHITE, 16) + P(hR, "none", WHITE, 16) + hull(cup, stem, tbase)
    + P(hL, "none", GOLD, 7) + P(hR, "none", GOLD, 7)
    + P(cup, GOLD) + glint(-26, -28, 52, .6) + P(stem, darkened(GOLD, .10)) + P(tbase, COVER_DEEP))

# Ticket — ADMIT 1
stock = rrect(0, 0, 94, 52, 6)
symbols["ticket-admit"] = (hull(stock) + P(stock, BUTTER, INK, 1, extra='stroke-opacity=".25"')
    + P(circle(-47, 0, 14), WHITE) + P(circle(47, 0, 14), WHITE)
    + "".join(P(circle(-28 + i * 4.5, 14, 2.8), INK, op=.35) for i in range(5))
    + '<text x="0" y="-4" text-anchor="middle" font-family="Inter, -apple-system, sans-serif" font-weight="700" font-size="14" letter-spacing="0.6" fill="#3D2F21" fill-opacity=".7">ADMIT 1</text>')

# Camera
cbody = rrect(0, 4, 86, 56, 10); finder = rrect(-22, -28, 30, 20, 6)
symbols["camera"] = (hull(cbody, finder) + P(finder, darkened(SKY, .06)) + P(cbody, SKY)
    + P(circle(0, 6, 34), PAPER) + P(circle(0, 6, 34), "none", INK, 3.5, extra='stroke-opacity=".6"')
    + P(circle(0, 6, 22), INK, op=.75) + glint(-11, -5, 22, .9)
    + P(circle(28, -22, 10), BLUSH))

# Pencil (rotated −24° as a whole)
pb = rrect(-8, 0, 62, 20, 0)
tip = "M23 -10 L45 0 L23 10 Z"; graphite = "M36 -4.1 L45 0 L36 4.1 Z"
ferrule = rrect(-43, 0, 7, 20, 0); eraser = rrect(-52, 0, 14, 20, 5)
symbols["pencil"] = G(hull(capsule(0, 0, 110, 34))
    + P(pb, BUTTER) + P(rrect(-8, -7, 62, 6, 0), INK, op=.10)
    + P(tip, COVER) + P(graphite, INK) + P(ferrule, darkened(GOLD, .05)) + P(eraser, BLUSH), rot(-24))

# Postage — perforated, our hex, the 6, three cancellation lines
def perforated(w, h, teeth=7):
    r = min(w, h) / (2 * teeth + 2) * .55
    d = rrect(0, 0, w, h, 0)
    for i in range(teeth):
        t = -w / 2 + w * (i + .5) / teeth; d += circle(t, -h / 2, r * 2) + circle(t, h / 2, r * 2)
        s = -h / 2 + h * (i + .5) / teeth; d += circle(-w / 2, s, r * 2) + circle(w / 2, s, r * 2)
    return d
sheet = perforated(88, 104)
symbols["postage"] = (P(sheet, WHITE, extra='fill-rule="evenodd"') + P(rrect(0, 0, 68, 84, 0), SKY, op=.75)
    + P(rhex(-6, 6, 34, 34), lightened(GOLD, .08))
    + '<text x="24" y="-22" text-anchor="middle" font-family="Inter, -apple-system, sans-serif" font-weight="700" font-size="20" fill="#3D2F21" fill-opacity=".75">6</text>'
    + G("".join(P(f"M-35 {f(-20 + i*9)} C-22 {f(-26 + i*9)} -10 {f(-14 + i*9)} 0 {f(-19 + i*9)} S24 {f(-24 + i*9)} 35 {f(-21 + i*9)}", None, INK, 1, op=.3, extra='stroke-linecap="round"') for i in range(3)), rot(-8)))

# Die — pencil-drawn, matte: no glint. Faces 1–6 as separate symbols.
def die(pips):
    d = rrect(0, 0, 100, 100, 22)
    pos = {1: [(0, 0)], 2: [(-24, -24), (24, 24)], 3: [(-24, -24), (0, 0), (24, 24)],
           4: [(-24, -24), (24, -24), (-24, 24), (24, 24)], 5: [(-24, -24), (24, -24), (0, 0), (-24, 24), (24, 24)],
           6: [(-24, -24), (24, -24), (-24, 0), (24, 0), (-24, 24), (24, 24)]}[pips]
    return P(d, PAPER, INK, 1.3) + "".join(P(circle(x, y, 17), INK) for x, y in pos)
for n in range(1, 7): symbols[f"die{n}"] = die(n)

# Pushpin head — the flat sticker-language pin: disc + hairline + jelly glint + contact whisper
for name, col in (("pin-red", "#D23B2F"), ("pin-yellow", "#F2B714"), ("pin-green", "#439856"), ("pin-white", "#F8F6F2")):
    symbols[name] = (P(ellipse(0, 52, 80, 26), INK, op=.10)
        + P(circle(0, 0, 100), col) + P(circle(0, 0, 99.2), "none", INK, .8, extra='stroke-opacity=".15"')
        + glint(-50, -50, 100))

# Map die pin — 25 head on a 2.8 × 16 steel needle; numeral set by the page
for name, col, num in (("mappin-red", "#D23B2F", WHITE), ("mappin-yellow", "#F2B714", INK), ("mappin-green", "#439856", WHITE), ("mappin-white", "#F8F6F2", INK)):
    # box 0..48 × 0..52, tip at (24, 52)
    needle = "M22.6 24 H25.4 L24.28 51.04 L24 52 L23.72 51.04 Z"
    symbols[name] = (f'<g transform="translate(-24 -26)">'
        + P(ellipse(24, 51, 10, 3.4), INK, op=.12) + P(needle, "#999694")
        + P(circle(24, 24, 25), col) + P(circle(24, 24, 24.2), "none", INK, .8, extra='stroke-opacity=".15"')
        + glint(11.5, 11.5, 25) + "</g>")

# Bord's own sticker cut — the white rounded-hex backing the real face sits on
symbols["bord-cut"] = P(rhex(0, 0, 122, 130), WHITE)

out = ['<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">']
for name, body in symbols.items():
    vb = "0 0 48 52" if name.startswith("mappin") else "-64 -64 128 128"
    if name.startswith("mappin"): body = f'<g transform="translate(24 26)">{body}</g>'
    out.append(f'<symbol id="s-{name}" viewBox="{vb}">{body}</symbol>')
out.append("</svg>")
path = os.path.join(os.path.dirname(__file__), "..", "img", "stickers.svg")
open(path, "w").write("\n".join(out) + "\n")
print("wrote", path, len(symbols), "symbols")
