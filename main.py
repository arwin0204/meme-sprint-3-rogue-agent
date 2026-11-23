#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws one original meme image (1024x1024 PNG) with PIL only: no network,
no randomness, no external assets besides the bundled DejaVu Sans Bold
subset shipped in this repository.

The joke: you ask your AI agent to book a flight; the agent goes rogue
and books itself a one-way ticket to the Bahamas instead.

Usage:
    python3 main.py            # writes to $OUTPUT_PATH or /output/entry.png
"""

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = Path(__file__).resolve().parent


def load_font(size):
    """Bold meme font: the subset shipped in this repo, else system DejaVu."""
    candidates = [
        HERE / "DejaVuSans-Bold.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(str(path), size)
        except Exception:
            continue
    return ImageFont.load_default(size)


def fit_font(text, start_size, max_width):
    """Largest bold font size (<= start_size) whose text fits max_width."""
    size = start_size
    while size > 10:
        font = load_font(size)
        bbox = font.getbbox(text)
        if bbox[2] - bbox[0] <= max_width:
            return font
        size -= 2
    return load_font(10)


def draw_meme_text(draw, lines, y_top, start_size, max_width):
    """Classic meme text: white, bold, thick black outline, centred."""
    size = start_size
    fonts = []
    while size > 10:
        fonts = [load_font(size) for _ in lines]
        widths = [f.getbbox(t)[2] - f.getbbox(t)[0] for f, t in zip(fonts, lines)]
        if max(widths) <= max_width:
            break
        size -= 2
    else:
        fonts = [load_font(10) for _ in lines]
    stroke = max(3, size // 13)
    y = y_top
    for font, text in zip(fonts, lines):
        bbox = font.getbbox(text)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (W - tw) // 2 - bbox[0]
        draw.text((x, y), text, font=font, fill=(255, 255, 255),
                  stroke_width=stroke, stroke_fill=(0, 0, 0))
        y += th + 8
    return y  # bottom edge of the last line


def text_height(lines, size):
    font = load_font(size)
    total = 0
    for text in lines:
        bbox = font.getbbox(text)
        total += bbox[3] - bbox[1] + 8
    return total - 8


def draw_sky_sea_sand(draw):
    # Sky gradient.
    top = (126, 203, 234)
    bottom = (198, 236, 247)
    for y in range(0, 560):
        t = y / 560
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (W, y)], fill=c)
    # Sun with rays.
    cx, cy, r = 872, 252, 56
    for k in range(12):
        import math
        a = math.radians(k * 30)
        x1 = cx + int(math.cos(a) * (r + 8))
        y1 = cy + int(math.sin(a) * (r + 8))
        x2 = cx + int(math.cos(a) * (r + 30))
        y2 = cy + int(math.sin(a) * (r + 30))
        draw.line([(x1, y1), (x2, y2)], fill=(255, 200, 40), width=7)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 fill=(255, 213, 74), outline=(238, 178, 18), width=4)
    # Clouds.
    for (x, y, s) in [(120, 238, 1.0), (640, 300, 0.8)]:
        draw.ellipse([x, y, x + int(150 * s), y + int(52 * s)], fill=(255, 255, 255))
        draw.ellipse([x + int(30 * s), y - int(22 * s), x + int(120 * s), y + int(30 * s)],
                     fill=(255, 255, 255))
    # Birds.
    for (x, y) in [(300, 262), (352, 232)]:
        draw.arc([x, y, x + 26, y + 16], 200, 340, fill=(60, 70, 80), width=4)
        draw.arc([x + 26, y, x + 52, y + 16], 200, 340, fill=(60, 70, 80), width=4)
    # Sea.
    draw.rectangle([0, 560, W, 690], fill=(38, 132, 198))
    draw.rectangle([0, 560, W, 572], fill=(86, 172, 220))
    for y in (592, 628, 664):
        for x in range(10, W, 130):
            draw.arc([x, y, x + 84, y + 26], 180, 360, fill=(235, 245, 250), width=5)
    # Sand.
    draw.rectangle([0, 690, W, H], fill=(243, 214, 148))
    draw.rectangle([0, 690, W, 700], fill=(232, 200, 128))


def draw_palm(draw):
    # Curved trunk: stacked circles along a quadratic curve.
    import math
    pts = []
    for t in range(0, 101, 5):
        u = t / 100
        x = (1 - u) ** 2 * 92 + 2 * (1 - u) * u * 96 + u * u * 172
        y = (1 - u) ** 2 * 780 + 2 * (1 - u) * u * 560 + u * u * 392
        pts.append((x, y))
    for i, (x, y) in enumerate(pts):
        r = max(10, 26 - i * 0.55)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(139, 94, 52))
    # Coconuts.
    draw.ellipse([150, 396, 178, 424], fill=(96, 64, 32))
    draw.ellipse([176, 404, 202, 430], fill=(112, 76, 40))
    # Fronds: thick arcs fanning out from the crown.
    cx, cy = 172, 392
    for (dx, dy, sweep) in [(-150, -70, 1), (-120, 30, 1), (-40, -110, 1),
                            (70, -100, 1), (150, -50, 1), (130, 40, 1)]:
        ex, ey = cx + dx, cy + dy
        midx, midy = (cx + ex) // 2, min(cy, ey) - 46
        for t in range(0, 101, 4):
            u = t / 100
            x = (1 - u) ** 2 * cx + 2 * (1 - u) * u * midx + u * u * ex
            y = (1 - u) ** 2 * cy + 2 * (1 - u) * u * midy + u * u * ey
            draw.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(46, 139, 66))
        draw.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], fill=(46, 139, 66))


def draw_towel(draw):
    # Striped beach towel.
    x0, y0, x1, y1 = 330, 700, 694, 800
    draw.rectangle([x0, y0, x1, y1], fill=(255, 255, 255),
                   outline=(200, 60, 60), width=4)
    for i, x in enumerate(range(x0 + 14, x1 - 10, 52)):
        draw.rectangle([x, y0 + 4, x + 26, y1 - 4], fill=(224, 62, 62))


def draw_robot(draw):
    silver = (192, 200, 208)
    dark = (88, 98, 110)
    # Raised right arm (holding the cocktail).
    draw.line([(612, 566), (686, 486), (730, 436)], fill=dark, width=34)
    draw.line([(612, 566), (686, 486), (730, 436)], fill=silver, width=24)
    draw.ellipse([716, 422, 744, 450], fill=silver, outline=dark, width=3)
    # Resting left arm.
    draw.line([(408, 566), (360, 640), (352, 690)], fill=dark, width=34)
    draw.line([(408, 566), (360, 640), (352, 690)], fill=silver, width=24)
    draw.ellipse([338, 676, 366, 704], fill=silver, outline=dark, width=3)
    # Body.
    draw.rounded_rectangle([400, 520, 624, 700], radius=28,
                           fill=silver, outline=dark, width=5)
    # Chest panel: MODE: ROGUE.
    draw.rounded_rectangle([440, 552, 584, 648], radius=12,
                           fill=(32, 48, 74), outline=dark, width=3)
    for i, col in enumerate([(90, 220, 90), (255, 210, 60), (235, 70, 70)]):
        draw.ellipse([462 + i * 30, 566, 478 + i * 30, 582], fill=col)
    small = load_font(24)
    for j, line in enumerate(("MODE:", "ROGUE")):
        bbox = small.getbbox(line)
        tw = bbox[2] - bbox[0]
        draw.text(((512 - tw // 2) - bbox[0], 590 + j * 28), line,
                  font=small, fill=(255, 90, 90) if j == 1 else (255, 255, 255))
    # Feet on the towel.
    draw.rounded_rectangle([420, 686, 482, 716], radius=10,
                           fill=silver, outline=dark, width=4)
    draw.rounded_rectangle([542, 686, 604, 716], radius=10,
                           fill=silver, outline=dark, width=4)
    # Antenna.
    draw.line([(512, 330), (512, 276)], fill=dark, width=8)
    draw.ellipse([498, 252, 526, 280], fill=(235, 70, 70), outline=dark, width=3)
    # Ears.
    draw.rectangle([352, 396, 372, 448], fill=silver, outline=dark, width=3)
    draw.rectangle([652, 396, 672, 448], fill=silver, outline=dark, width=3)
    # Head.
    draw.rounded_rectangle([372, 330, 652, 520], radius=42,
                           fill=silver, outline=dark, width=5)
    # Sunglasses.
    draw.rounded_rectangle([402, 388, 494, 436], radius=12, fill=(20, 20, 24))
    draw.rounded_rectangle([530, 388, 622, 436], radius=12, fill=(20, 20, 24))
    draw.rectangle([494, 406, 530, 414], fill=(20, 20, 24))
    draw.line([(416, 430), (452, 396)], fill=(255, 255, 255), width=5)
    draw.line([(544, 430), (580, 396)], fill=(255, 255, 255), width=5)
    # Smug grin.
    draw.arc([448, 436, 576, 502], 15, 165, fill=(40, 40, 44), width=7)
    # Blush.
    draw.ellipse([396, 452, 424, 468], fill=(240, 150, 160))
    draw.ellipse([600, 452, 628, 468], fill=(240, 150, 160))


def draw_cocktail(draw):
    # Little umbrella.
    draw.polygon([(694, 384), (776, 384), (735, 334)], fill=(235, 80, 110))
    draw.polygon([(694, 384), (735, 384), (735, 334)], fill=(245, 140, 160))
    draw.line([(735, 384), (735, 334)], fill=(120, 70, 40), width=4)
    # Glass with orange juice.
    draw.polygon([(712, 384), (758, 384), (750, 422), (720, 422)],
                 fill=(255, 140, 40), outline=(90, 50, 20), width=3)
    draw.line([(712, 384), (758, 384)], fill=(255, 255, 255), width=4)
    # Straw.
    draw.line([(748, 386), (764, 348)], fill=(60, 180, 90), width=5)


def draw_laptop(draw):
    # Laptop showing the rogue booking.
    draw.rounded_rectangle([700, 636, 910, 752], radius=10,
                           fill=(24, 34, 54), outline=(10, 16, 28), width=4)
    f1 = load_font(19)
    f2 = load_font(18)
    for text, font, y, col in [
        ("BOARDING PASS", f1, 652, (255, 255, 255)),
        ("1 PASSENGER: ME", f2, 682, (110, 230, 120)),
        ("DEST: BAHAMAS", f2, 710, (255, 215, 90)),
    ]:
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        draw.text(((805 - tw // 2) - bbox[0], y), text, font=font, fill=col)
    draw.polygon([(678, 752), (928, 752), (948, 774), (658, 774)],
                 fill=(150, 158, 168), outline=(88, 98, 110))


def draw_beach_ball(draw):
    cx, cy, r = 255, 792, 46
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255),
                 outline=(200, 60, 60), width=4)
    draw.pieslice([cx - r, cy - r, cx + r, cy + r], 270, 330, fill=(235, 70, 70))
    draw.pieslice([cx - r, cy - r, cx + r, cy + r], 30, 90, fill=(60, 120, 220))
    draw.pieslice([cx - r, cy - r, cx + r, cy + r], 150, 210, fill=(255, 210, 60))
    draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(255, 255, 255),
                 outline=(200, 60, 60), width=3)


def build_image():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw_sky_sea_sand(draw)
    draw_palm(draw)
    draw_towel(draw)
    draw_robot(draw)
    draw_cocktail(draw)
    draw_laptop(draw)
    draw_beach_ball(draw)
    draw_meme_text(draw, ["I TOLD MY AI AGENT", "TO BOOK A FLIGHT"],
                   22, 84, 970)
    bottom = ["IT BOOKED ITSELF", "A ONE-WAY TO THE BAHAMAS"]
    # Bottom text: same size for both lines, anchored 20 px above the edge.
    size = 72
    while size > 10:
        if max(load_font(size).getbbox(t)[2] - load_font(size).getbbox(t)[0]
               for t in bottom) <= 970:
            break
        size -= 2
    y_top = H - 20 - text_height(bottom, size)
    draw_meme_text(draw, bottom, y_top, size, 970)
    return img


def main():
    out = os.environ.get("OUTPUT_PATH", "/output/entry.png")
    img = build_image()
    parent = os.path.dirname(os.path.abspath(out))
    if parent:
        os.makedirs(parent, exist_ok=True)
    img.save(out, format="PNG")
    print(f"wrote {out} ({img.width}x{img.height})")


if __name__ == "__main__":
    main()
