#!/usr/bin/env python3
"""img/fiber.svg (kraft) and img/cardstock.svg (paper) — the app's BNFiber and
BNCardstock grain, same LCG, same stroke parameters, tiled at 360 × 360."""
import os
MASK = (1 << 64) - 1
def lcg(seed):
    s = seed
    while True:
        s = (s * 6364136223846793005 + 1442695040888963407) & MASK
        yield ((s >> 33) & 0xFFFFFF) / 0xFFFFFF
def tile(name, seed, count, length, angle_amp, lw, colours):
    r = lcg(seed); W = H = 360
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" stroke-width="{lw}" stroke-linecap="round">']
    import math
    for i in range(count):
        x, y = next(r) * W, next(r) * H
        L = length[0] + next(r) * length[1]
        a = (next(r) - .5) * angle_amp
        col = colours[i % len(colours)](next(r))
        out.append(f'<path d="M{x:.1f} {y:.1f}L{x + math.cos(a) * L:.1f} {y + math.sin(a) * L:.1f}" stroke="{col}"/>')
    out.append("</svg>")
    p = os.path.join(os.path.dirname(__file__), "..", "img", name)
    open(p, "w").write("\n".join(out)); print("wrote", p, count, "strokes")
# BNFiber: 900 strokes per screen (~393×852 ≈ 335k pt²) → 360² tile ≈ 350
tile("fiber.svg", 0xF1BE2, 350, (4, 14), 0.5, 0.7,
     [lambda v: f"rgba(255,255,255,{0.10 + v * 0.08:.3f})", lambda v: f"rgba(61,47,33,{0.04 + v * 0.04:.3f})"])
# BNCardstock: w·h/260 strokes, ink only
tile("cardstock.svg", 0xCA2D, 360 * 360 // 260, (3, 10), 0.6, 0.6,
     [lambda v: f"rgba(61,47,33,{0.03 + v * 0.035:.3f})"])
