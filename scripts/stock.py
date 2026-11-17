#!/usr/bin/env python3
"""Vídeos de banco GRÁTIS com pessoas reais (Mixkit — licença livre para uso
em vídeos monetizados, sem atribuição obrigatória). Sem API key.

1) Buscar e ver miniaturas:
   python scripts/stock.py search gamer party miami --out stock_preview
   -> stock_preview/sheet_N.jpg (miniaturas numeradas) + stock_preview/index.tsv

2) Baixar os escolhidos para o episódio (pelos números da folha):
   python scripts/stock.py get episodes/<ep> stock_preview 0 13 42
   -> media/mk000.mp4, media/mk013.mp4, ... (1080p quando existir)
"""
import argparse
import re
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

UA = {"User-Agent": "Mozilla/5.0"}


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()


def search(terms, out: Path):
    from PIL import Image, ImageDraw, ImageFont

    out.mkdir(parents=True, exist_ok=True)
    ids = []
    for t in terms:
        html = fetch(f"https://mixkit.co/free-stock-video/{t.strip().replace(' ', '-')}/").decode("utf8", "ignore")
        for vid in re.findall(r"assets\.mixkit\.co/videos/(\d+)/\1-360\.mp4", html):
            if vid not in ids:
                ids.append(vid)
    print(f"[stock] {len(ids)} vídeos encontrados")
    prev = out / "prev"
    prev.mkdir(exist_ok=True)

    def dl(vid):
        p = prev / f"{vid}.mp4"
        if not p.exists():
            p.write_bytes(fetch(f"https://assets.mixkit.co/videos/{vid}/{vid}-360.mp4"))
        return p

    with ThreadPoolExecutor(8) as ex:
        files = list(ex.map(dl, ids))
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 24) if Path(font_path).exists() else ImageFont.load_default()
    thumbs = []
    for i, (vid, f) in enumerate(zip(ids, files)):
        png = prev / f"{vid}.png"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", "2", "-i", str(f), "-frames:v", "1",
                        "-vf", "scale=240:135:force_original_aspect_ratio=increase,crop=240:135", str(png)])
        thumbs.append(png)
    (out / "index.tsv").write_text("".join(f"{i}\t{v}\n" for i, v in enumerate(ids)))
    for s in range(0, len(thumbs), 64):
        chunk = thumbs[s:s + 64]
        sheet = Image.new("RGB", (8 * 240, ((len(chunk) + 7) // 8) * 135))
        d = ImageDraw.Draw(sheet)
        for k, png in enumerate(chunk):
            x, y = (k % 8) * 240, (k // 8) * 135
            if png.exists():
                sheet.paste(Image.open(png), (x, y))
            d.text((x + 4, y + 2), str(s + k), font=font, fill="yellow", stroke_width=3, stroke_fill="black")
        sheet.save(out / f"sheet_{s // 64}.jpg", quality=80)
    print(f"[stock] miniaturas em {out}/sheet_*.jpg — escolha os números e rode 'get'")


def get(ep: Path, preview: Path, nums):
    idx = dict(l.split("\t") for l in (preview / "index.tsv").read_text().split("\n") if l)
    media = ep / "media"
    media.mkdir(parents=True, exist_ok=True)
    for n in nums:
        vid = idx[str(n)].strip()
        out = media / f"mk{int(n):03d}.mp4"
        for res in ("1080", "720"):
            try:
                out.write_bytes(fetch(f"https://assets.mixkit.co/videos/{vid}/{vid}-{res}.mp4"))
                break
            except Exception:
                continue
        with open(media / "CREDITS_mixkit.txt", "a") as f:
            f.write(f"{out.name}\tMixkit #{vid}\t{res}p\thttps://mixkit.co\n")
        print(f"[stock] ok -> {out} ({res}p)")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("terms", nargs="+")
    s.add_argument("--out", default="stock_preview")
    g = sub.add_parser("get")
    g.add_argument("episode")
    g.add_argument("preview")
    g.add_argument("nums", nargs="+")
    a = ap.parse_args()
    if a.cmd == "search":
        search(a.terms, Path(a.out))
    else:
        get(Path(a.episode), Path(a.preview), a.nums)


if __name__ == "__main__":
    sys.exit(main())
