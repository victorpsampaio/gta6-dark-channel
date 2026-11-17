#!/usr/bin/env python3
"""Acha vídeos gringos em alta sobre um tema (YouTube, via yt-dlp, sem API key).

Busca os N vídeos MAIS RECENTES para o termo e ordena por visualizações,
então o topo da lista = o que está bombando agora.

Uso:
  python scripts/trending.py "GTA 6"
  python scripts/trending.py "GTA 6 launch" --n 80 --min-min 4      # só vídeos com 4+ min
  python scripts/trending.py "GTA 6 leak" --shorts                 # só Shorts

Depois: python scripts/transcribe.py <ep> <URL do vídeo escolhido>
(o vídeo é só FONTE de informação — nunca reupar)
"""
import argparse

from yt_dlp import YoutubeDL


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--n", type=int, default=60, help="quantos vídeos recentes analisar")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--min-min", type=float, default=3, help="duração mínima em minutos (ignora Shorts)")
    ap.add_argument("--shorts", action="store_true", help="mostrar só Shorts (<=60s)")
    a = ap.parse_args()

    with YoutubeDL({"quiet": True, "extract_flat": True, "skip_download": True}) as y:
        res = y.extract_info(f"ytsearchdate{a.n}:{a.query}", download=False)

    rows = []
    for e in res.get("entries") or []:
        dur = e.get("duration") or 0
        if a.shorts and not (0 < dur <= 60):
            continue
        if not a.shorts and dur < a.min_min * 60:
            continue
        rows.append((e.get("view_count") or 0, dur, e.get("channel") or e.get("uploader") or "?",
                     e.get("title") or "?", e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}"))
    rows.sort(reverse=True)

    print(f"{'views':>10}  {'dur':>5}  {'canal':22}  título")
    for v, d, ch, t, u in rows[: a.top]:
        print(f"{v:>10,}  {int(d//60):>2}:{int(d%60):02d}  {ch[:22]:22}  {t[:70]}\n{'':>20}{u}")
    if not rows:
        print("nada encontrado — tente outro termo ou aumente --n")


if __name__ == "__main__":
    main()
