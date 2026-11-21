#!/usr/bin/env python3
"""VESPERA — a travel poster for a place that isn't there.

Draws a fully procedural travel poster (Pillow only, no network, no
external images) and writes it to /output/entry.png (1024x1024, <=1 MiB).

The place: VESPERA, a lagoon where the sun rests on the water.
Its one landmark: the Sun Ring — a giant natural stone ring standing
in the lagoon, with the setting sun framed exactly inside it.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 1024
OUT = "/output/entry.png"

# ---------------------------------------------------------------- palette
SKY_TOP = (150, 58, 98)       # dusky violet dusk (not generic teal+gold)
SKY_MID = (214, 96, 84)      # rose-coral
SKY_LOW = (247, 183, 88)      # gold near the horizon
SUN_CORE = (255, 224, 130)
SUN_EDGE = (255, 176, 64)
WATER_TOP = (22, 60, 84)      # violet-teal lagoon
WATER_BOT = (10, 26, 48)      # deep violet-indigo
STONE_LIT = (122, 88, 66)     # sunlit rim of the ring
STONE_MID = (74, 52, 40)
STONE_DARK = (38, 26, 20)
SILHOUETTE = (24, 16, 14)
CREAM = (255, 243, 214)
GOLD = (242, 181, 68)

HORIZON_Y = 660
RING_C = (512, 545)
RING_OUT = 238
RING_IN = 168
SUN_C = (512, 592)
SUN_R = 100

rng = random.Random(20261121)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def font(name, size):
    """Bundled DejaVu first (deterministic in the grader sandbox),
    then system paths, then PIL's built-in bitmap font."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "fonts", name),
        os.path.join("/usr/share/fonts/truetype/dejavu", name),
        os.path.join("/usr/share/fonts/truetype/noto", name),
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default(size)


def vgrad(size, stops):
    """Vertical gradient image from a list of (position 0..1, rgb)."""
    w, h = size
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                px[0, y] = lerp(c0, c1, f)
                break
        else:
            px[0, y] = stops[-1][1]
    return img.resize((w, h))


def draw_tracked(draw, cx, y, text, fnt, fill, tracking=0, shadow=None):
    """Centre `text` at x=cx with letter tracking; returns text width."""
    widths = []
    total = 0
    for ch in text:
        w = draw.textlength(ch, font=fnt)
        widths.append(w)
        total += w
    total += tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        if shadow:
            draw.text((x + shadow[0], y + shadow[1]), ch, font=fnt, fill=shadow[2])
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking
    return total


def soft_disc(layer, centre, radius, colour, blur):
    """A soft-edged filled disc on an RGBA layer."""
    d = ImageDraw.Draw(layer)
    d.ellipse(
        [centre[0] - radius, centre[1] - radius,
         centre[0] + radius, centre[1] + radius],
        fill=colour + (255,),
    )
    return layer.filter(ImageFilter.GaussianBlur(blur))


def main():
    img = Image.new("RGB", (W, H))

    # --- sky: coral dusk melting into gold at the horizon ---------------
    sky = vgrad((W, HORIZON_Y + 40), [
        (0.00, SKY_TOP), (0.45, SKY_MID), (0.85, SKY_LOW), (1.00, (250, 205, 110)),
    ])
    img.paste(sky, (0, 0))

    # faint high cloud bands, warm and thin
    clouds = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(clouds)
    for cy, cw, ch, alpha in [
        (150, 560, 16, 26), (205, 700, 13, 20), (255, 420, 12, 22),
        (300, 640, 14, 18), (120, 380, 12, 20), (340, 500, 11, 16),
    ]:
        x0 = 512 - cw // 2 + rng.randint(-90, 90)
        cd.ellipse([x0, cy, x0 + cw, cy + ch], fill=(255, 214, 150, alpha))
    clouds = clouds.filter(ImageFilter.GaussianBlur(9))
    img.paste(clouds, (0, 0), clouds)

    # --- sun: halo, then the disc itself -------------------------------
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for r, alpha in [(300, 26), (230, 40), (170, 60)]:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        gd.ellipse([SUN_C[0] - r, SUN_C[1] - r, SUN_C[0] + r, SUN_C[1] + r],
                   fill=(255, 190, 90, alpha))
        glow = Image.alpha_composite(glow, g.filter(ImageFilter.GaussianBlur(40)))
    img.paste(glow, (0, 0), glow)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([SUN_C[0] - SUN_R, SUN_C[1] - SUN_R,
               SUN_C[0] + SUN_R, SUN_C[1] + SUN_R], fill=SUN_EDGE)
    d.ellipse([SUN_C[0] - SUN_R + 14, SUN_C[1] - SUN_R + 14,
               SUN_C[0] + SUN_R - 14, SUN_C[1] + SUN_R - 14], fill=SUN_CORE)

    # --- distant headlands on the horizon ------------------------------
    d.polygon([(0, HORIZON_Y), (0, HORIZON_Y - 46), (90, HORIZON_Y - 78),
               (190, HORIZON_Y - 40), (260, HORIZON_Y - 58),
               (330, HORIZON_Y - 18), (330, HORIZON_Y)], fill=(94, 52, 44))
    d.polygon([(1024, HORIZON_Y), (1024, HORIZON_Y - 38), (950, HORIZON_Y - 66),
               (860, HORIZON_Y - 30), (800, HORIZON_Y - 48),
               (730, HORIZON_Y - 12), (730, HORIZON_Y)], fill=(94, 52, 44))

    # --- the Sun Ring: stone annulus, sunlit rim, shadowed base --------
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    stone = vgrad((W, H), [(0.0, STONE_LIT), (0.45, STONE_MID), (1.0, STONE_DARK)])
    stone = stone.convert("RGBA")
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([RING_C[0] - RING_OUT, RING_C[1] - RING_OUT,
                RING_C[0] + RING_OUT, RING_C[1] + RING_OUT], fill=255)
    md.ellipse([RING_C[0] - RING_IN, RING_C[1] - RING_IN,
                RING_C[0] + RING_IN, RING_C[1] + RING_IN], fill=0)
    ring.paste(stone, (0, 0), mask)
    # speckle the stone so it reads as rock, not plastic
    speck = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(speck)
    for _ in range(900):
        a = rng.uniform(0, 2 * math.pi)
        r = math.sqrt(rng.uniform(0, 1))
        rr = RING_IN + r * (RING_OUT - RING_IN)
        x = RING_C[0] + rr * math.cos(a)
        y = RING_C[1] + rr * math.sin(a) * 0.98
        c = (255, 220, 170, rng.randint(8, 26)) if rng.random() < 0.5 \
            else (0, 0, 0, rng.randint(10, 30))
        sd.ellipse([x, y, x + rng.randint(1, 3), y + rng.randint(1, 3)], fill=c)
    ring = Image.alpha_composite(ring, speck)
    img.paste(ring, (0, 0), ring)

    # rim light: warm arc along the top of the ring, shadow at its foot
    d = ImageDraw.Draw(img, "RGBA")
    d.arc([RING_C[0] - RING_OUT + 3, RING_C[1] - RING_OUT + 3,
           RING_C[0] + RING_OUT - 3, RING_C[1] + RING_OUT - 3],
          start=195, end=345, fill=(255, 205, 130, 235), width=7)
    d.arc([RING_C[0] - RING_IN - 2, RING_C[1] - RING_IN - 2,
           RING_C[0] + RING_IN + 2, RING_C[1] + RING_IN + 2],
          start=200, end=340, fill=(255, 190, 110, 200), width=4)
    d.arc([RING_C[0] - RING_OUT + 2, RING_C[1] - RING_OUT + 2,
           RING_C[0] + RING_OUT - 2, RING_C[1] + RING_OUT - 2],
          start=15, end=165, fill=(20, 10, 8, 160), width=6)

    # --- lagoon water: dark teal, sun's gold path down to the viewer ---
    water = vgrad((W, H - HORIZON_Y), [(0.0, WATER_TOP), (1.0, WATER_BOT)])
    img.paste(water, (0, HORIZON_Y))
    d = ImageDraw.Draw(img, "RGBA")
    # glassy horizon line
    d.line([(0, HORIZON_Y), (W, HORIZON_Y)], fill=(255, 210, 140, 150), width=2)
    # golden reflection: shimmering dashes widening toward the viewer
    for y in range(HORIZON_Y + 8, 985, 7):
        depth = (y - HORIZON_Y) / (985 - HORIZON_Y)
        half = 26 + depth * 150
        alpha = int(190 * (1 - depth) + 26)
        cx = 512 + rng.randint(-8, 8)
        wdt = rng.randint(14, 66) + int(depth * 60)
        x0 = max(cx - wdt // 2, 512 - half)
        x1 = min(cx + wdt // 2, 512 + half)
        d.line([(x0, y), (x1, y)], fill=(242, 181, 68, alpha), width=3)
    # faint teal ripples away from the reflection
    for _ in range(70):
        x = rng.randint(20, 1004)
        y = rng.randint(HORIZON_Y + 20, 1000)
        ln = rng.randint(12, 60)
        d.line([(x, y), (x + ln, y)], fill=(120, 200, 190, rng.randint(14, 40)),
               width=2)

    # --- foreground: low rocky shores framing the bottom corners -------
    d.polygon([(0, 1024), (0, 950), (70, 905), (150, 930), (215, 968),
               (255, 1024)], fill=SILHOUETTE)
    d.polygon([(1024, 1024), (1024, 958), (965, 912), (895, 938),
               (845, 972), (815, 1024)], fill=SILHOUETTE)
    # a few reeds on the shores, catching the last light
    for bx, bh, tilt in [(48, 58, -8), (66, 44, -3), (84, 66, 3),
                         (952, 52, 6), (970, 40, 1)]:
        d.line([(bx, 985), (bx + tilt, 985 - bh)], fill=(150, 105, 60, 255), width=3)
        d.ellipse([bx + tilt - 4, 985 - bh - 8, bx + tilt + 4, 985 - bh + 2],
                  fill=(198, 130, 70, 255))

    # --- birds: five small silhouettes high in the sky -----------------
    for bx, by, s in [(180, 300, 14), (222, 276, 11), (845, 268, 13),
                      (882, 298, 10), (810, 322, 9)]:
        d.arc([bx - s, by - s // 2, bx, by + s // 2], start=200, end=340,
              fill=(60, 30, 22, 230), width=3)
        d.arc([bx, by - s // 2, bx + s, by + s // 2], start=200, end=340,
              fill=(60, 30, 22, 230), width=3)

    # --- type: VESPERA, then the one-line promise ----------------------
    d = ImageDraw.Draw(img, "RGBA")
    # auto-fit the title inside the frame (max width 940)
    title_size = 132
    while title_size > 60:
        title_font = font("DejaVuSerif-Bold.ttf", title_size)
        w = sum(d.textlength(ch, font=title_font) for ch in "VESPERA") \
            + 18 * (len("VESPERA") - 1)
        if w <= 940:
            break
        title_size -= 6
    draw_tracked(d, 512, 66, "VESPERA", title_font, CREAM,
                 tracking=18, shadow=(3, 5, (40, 16, 10, 170)))
    # thin gold rules flanking the tagline
    tag_font = font("DejaVuSans.ttf", 28)
    tag = "WHERE THE SUN RESTS ON THE WATER"
    tag_w = draw_tracked(d, 512, 240, tag, tag_font, (255, 226, 170),
                         tracking=6, shadow=(2, 2, (40, 16, 10, 160)))
    rule_y = 255
    d.line([(512 - tag_w / 2 - 84, rule_y), (512 - tag_w / 2 - 20, rule_y)],
           fill=GOLD + (220,), width=2)
    d.line([(512 + tag_w / 2 + 20, rule_y), (512 + tag_w / 2 + 84, rule_y)],
           fill=GOLD + (220,), width=2)

    # --- thin double frame, the poster's edge ---------------------------
    d.rectangle([22, 22, 1001, 1001], outline=CREAM + (200,), width=3)
    d.rectangle([32, 32, 991, 991], outline=CREAM + (110,), width=1)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    print(f"wrote {OUT} {img.size} "
          f"{os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
