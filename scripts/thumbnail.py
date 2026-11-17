#!/usr/bin/env python3
"""Thumbnail 1280x720 com Pillow: imagem de fundo + texto grande com contorno.

Uso:
  python scripts/thumbnail.py episodes/<slug>/media/bg.jpg "LEONIDA IS HUGE" -o episodes/<slug>/out/thumb.png
  python scripts/thumbnail.py bg.jpg "SECRET ENDING?" --color "#FFD400" --side right
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

FONTS = [
    "assets/fonts/thumb.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/opentype/inter/Inter-Black.otf",
    "C:/Windows/Fonts/impact.ttf",
    "/System/Library/Fonts/Supplemental/Impact.ttf",
]


def font(size):
    for f in FONTS:
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default(size)


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        test = (cur + " " + word).strip()
        if draw.textlength(test, font=fnt) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("text")
    ap.add_argument("-o", "--out", default="thumb.png")
    ap.add_argument("--color", default="#FFFFFF")
    ap.add_argument("--side", choices=["left", "right", "center"], default="left")
    a = ap.parse_args()

    W, H = 1280, 720
    img = ImageOps.fit(Image.open(a.image).convert("RGB"), (W, H))
    img = ImageEnhance.Contrast(ImageEnhance.Color(img).enhance(1.35)).enhance(1.15)

    # degradê escuro do lado do texto
    grad = Image.new("L", (W, 1))
    for x in range(W):
        f = x / W if a.side == "right" else 1 - x / W
        grad.putpixel((x, 0), int(220 * max(0, f - 0.25) / 0.75) if a.side != "center" else 120)
    img = Image.composite(Image.new("RGB", (W, H), "black"), img, grad.resize((W, H)))

    d = ImageDraw.Draw(img)
    text = a.text.upper()
    max_w = W * (0.9 if a.side == "center" else 0.55)
    size = 170
    while size > 40:
        fnt = font(size)
        lines = wrap(d, text, fnt, max_w)
        lh = size * 1.05
        if len(lines) * lh < H * 0.8 and all(d.textlength(l, font=fnt) <= max_w for l in lines):
            break
        size -= 6
    y = (H - len(lines) * lh) / 2
    for line in lines:
        tw = d.textlength(line, font=fnt)
        x = {"left": 50, "right": W - 50 - tw, "center": (W - tw) / 2}[a.side]
        d.text((x, y), line, font=fnt, fill=a.color, stroke_width=max(4, size // 14), stroke_fill="black")
        y += lh

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    img.save(a.out, optimize=True)
    print(f"[thumb] ok -> {a.out}")


if __name__ == "__main__":
    main()
