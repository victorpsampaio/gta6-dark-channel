#!/usr/bin/env python3
"""Baixa SÓ o áudio de um vídeo (yt-dlp) e transcreve local (faster-whisper).

Serve para PESQUISA: extrair fatos de vídeos gringos sem gastar token com
áudio/vídeo. O vídeo dos outros NÃO entra no seu vídeo.

Saída em episodes/<slug>/sources/<id>/:
  transcript.txt  (texto corrido, com marcação de tempo a cada ~30s)
  transcript.srt
  meta.json       (título, canal, url, data -> para dar crédito na descrição)

Uso:
  python scripts/transcribe.py episodes/<slug> URL [URL ...]
  python scripts/transcribe.py episodes/<slug> arquivo_local.mp4 --model small
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def fmt(t):
    return f"{int(t//3600):02d}:{int(t//60%60):02d}:{int(t%60):02d}"


def fetch_audio(url: str, dest: Path) -> tuple[Path, dict]:
    dest.mkdir(parents=True, exist_ok=True)
    info = json.loads(subprocess.run(
        ["yt-dlp", "-J", "--no-playlist", url], capture_output=True, text=True, check=True).stdout)
    vid = info.get("id", "src")
    out = dest / vid
    out.mkdir(exist_ok=True)
    subprocess.run(["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "5", "--no-playlist",
                    "-o", str(out / "audio.%(ext)s"), url], check=True)
    meta = {k: info.get(k) for k in ("id", "title", "channel", "uploader", "upload_date", "webpage_url",
                                     "duration", "view_count")}
    return out / "audio.mp3", meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--model", default="small", help="tiny|base|small|medium|large-v3 (maior = melhor e mais lento)")
    ap.add_argument("--keep-audio", action="store_true")
    a = ap.parse_args()

    from faster_whisper import WhisperModel
    model = WhisperModel(a.model, device="auto", compute_type="int8")
    src_dir = Path(a.episode) / "sources"

    for inp in a.inputs:
        if Path(inp).exists():
            p = Path(inp)
            out = src_dir / p.stem
            out.mkdir(parents=True, exist_ok=True)
            audio, meta = p, {"id": p.stem, "title": p.name, "webpage_url": None}
        else:
            audio, meta = fetch_audio(inp, src_dir)
            out = audio.parent
        print(f"[whisper] transcrevendo {meta.get('title')} ...", file=sys.stderr)
        segments, _ = model.transcribe(str(audio), vad_filter=True)
        txt, srt, last_mark = [], [], -30
        for i, s in enumerate(segments, 1):
            if s.start - last_mark >= 30:
                txt.append(f"\n[{fmt(s.start)}] ")
                last_mark = s.start
            txt.append(s.text.strip() + " ")
            srt.append(f"{i}\n{fmt(s.start)},000 --> {fmt(s.end)},000\n{s.text.strip()}\n")
        (out / "transcript.txt").write_text("".join(txt).strip())
        (out / "transcript.srt").write_text("\n".join(srt))
        (out / "meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
        if not a.keep_audio and audio.parent == out and audio.name == "audio.mp3":
            audio.unlink(missing_ok=True)
        words = len("".join(txt).split())
        print(f"[whisper] ok -> {out}/transcript.txt ({words} palavras)")


if __name__ == "__main__":
    main()
