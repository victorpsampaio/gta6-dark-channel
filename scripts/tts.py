#!/usr/bin/env python3
"""Narração grátis com edge-tts (vozes neurais da Microsoft).

Lê episodes/<slug>/scenes.json e gera, para cada cena:
  audio/scene_XX.mp3  +  audio/manifest.json (duração e legendas palavra a palavra)

Uso:
  python scripts/tts.py episodes/<slug>
  python scripts/tts.py episodes/<slug> --voice en-US-AndrewNeural --rate +5%
  python scripts/tts.py --list-voices          # lista vozes en-US
"""
import argparse
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import edge_tts

DEFAULT_VOICE = "en-US-AndrewNeural"  # alternativas: en-US-GuyNeural, en-US-ChristopherNeural, en-US-BrianNeural


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


async def synth(text: str, voice: str, rate: str, pitch: str, out: Path) -> list[dict]:
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary", proxy=proxy)
    words = []
    with out.open("wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 1e7
                words.append({"w": chunk["text"], "start": start, "end": start + chunk["duration"] / 1e7})
    return words


async def list_voices():
    for v in await edge_tts.list_voices():
        if v["Locale"] == "en-US":
            print(f'{v["ShortName"]:32} {v["Gender"]:7} {", ".join(v.get("VoiceTag", {}).get("VoicePersonalities", []))}')


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode", nargs="?")
    ap.add_argument("--voice")
    ap.add_argument("--rate", default=None, help="ex: +5%%")
    ap.add_argument("--pitch", default=None, help="ex: -2Hz")
    ap.add_argument("--only", type=int, nargs="*", help="regera só essas cenas (índice começando em 1)")
    ap.add_argument("--list-voices", action="store_true")
    a = ap.parse_args()

    if a.list_voices:
        return await list_voices()
    if not a.episode:
        ap.error("informe a pasta do episódio")

    ep = Path(a.episode)
    cfg = json.loads((ep / "scenes.json").read_text())
    voice = a.voice or cfg.get("voice", DEFAULT_VOICE)
    rate = a.rate or cfg.get("rate", "+0%")
    pitch = a.pitch or cfg.get("pitch", "+0Hz")

    audio_dir = ep / "audio"
    audio_dir.mkdir(exist_ok=True)
    man_path = audio_dir / "manifest.json"
    manifest = json.loads(man_path.read_text()) if man_path.exists() else {}

    for i, scene in enumerate(cfg["scenes"], 1):
        key = f"scene_{i:02d}"
        if a.only and i not in a.only and key in manifest:
            continue
        out = audio_dir / f"{key}.mp3"
        words = await synth(scene["text"], voice, rate, pitch, out)
        manifest[key] = {"file": out.name, "duration": probe_duration(out), "words": words}
        print(f"[tts] {key}  {manifest[key]['duration']:.1f}s  {scene['text'][:60]}...")

    # remove cenas que não existem mais
    for k in list(manifest):
        if int(k.split("_")[1]) > len(cfg["scenes"]):
            del manifest[k]
    man_path.write_text(json.dumps(manifest, indent=1))
    total = sum(m["duration"] for m in manifest.values())
    print(f"[tts] ok — {len(manifest)} cenas, {total/60:.1f} min de narração")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(1)
