#!/usr/bin/env python3
"""Baixa SÓ um trecho curto de um vídeo do YouTube para usar como B-roll.

Uso (no seu PC — precisa de acesso ao YouTube):
  python scripts/fetch_clip.py <ep> <URL> 1:12-1:19 --name trailer2_lucia
  python scripts/fetch_clip.py <ep> <URL> 30-36 40-45          # vários trechos

Gera media/<name>_N.mp4 (sem áudio, até 1080p) e anota em media/CREDITS.txt
canal + título + URL + trecho, para colocar no lower_third e na descrição.

REGRAS DO CANAL:
- Prefira material oficial (canal Rockstar Games) e notícias.
- Trechos de outros criadores: curtos (padrão máx. 8s), sempre com sua narração
  por cima e crédito na tela. Nunca use sequências longas nem o áudio original.
"""
import argparse
import json
import subprocess
from pathlib import Path


def secs(t: str) -> float:
    s = 0.0
    for p in t.split(":"):
        s = s * 60 + float(p)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("url")
    ap.add_argument("ranges", nargs="+", help="inicio-fim (seg ou m:ss)")
    ap.add_argument("--name", default="yt")
    ap.add_argument("--max", type=float, default=8, help="duração máxima por trecho (s)")
    a = ap.parse_args()

    media = Path(a.episode) / "media"
    media.mkdir(parents=True, exist_ok=True)
    info = json.loads(subprocess.run(["yt-dlp", "-J", "--no-playlist", a.url],
                                     capture_output=True, text=True, check=True).stdout)
    channel, title = info.get("channel") or info.get("uploader"), info.get("title")

    for i, r in enumerate(a.ranges, 1):
        s, e = (secs(x) for x in r.split("-"))
        if e - s > a.max:
            print(f"  ! trecho {r} tem {e-s:.0f}s; cortando para {a.max:.0f}s (use --max para mudar)")
            e = s + a.max
        out = media / f"{a.name}_{i}.mp4"
        tmp = media / f".{a.name}_{i}.tmp.%(ext)s"
        subprocess.run(["yt-dlp", "-f", "bv*[height<=1080][ext=mp4]/bv*[height<=1080]", "--no-playlist",
                        "--download-sections", f"*{s}-{e}", "--force-keyframes-at-cuts",
                        "-o", str(tmp), a.url], check=True)
        got = next(media.glob(f".{a.name}_{i}.tmp.*"))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(got), "-an", "-c:v", "libx264",
                        "-crf", "18", "-pix_fmt", "yuv420p", str(out)], check=True)
        got.unlink()
        with open(media / "CREDITS.txt", "a") as f:
            f.write(f"{out.name}\t{channel}\t{title}\t{a.url}\t{r}\n")
        print(f"[clip] ok -> {out}  (crédito: {channel})")
    print(f'Use no scenes.json: "media": ["media/{a.name}_1.mp4"], "lower_third": "Footage: {channel}"')


if __name__ == "__main__":
    main()
