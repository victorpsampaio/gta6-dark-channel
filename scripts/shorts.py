#!/usr/bin/env python3
"""Corta Shorts 9:16 (1080x1920) do vídeo longo, com fundo desfocado e
legenda grande recortada do captions.srt.

Uso:
  python scripts/shorts.py episodes/<slug> 00:01:10-00:01:52 00:04:03-00:04:50
  python scripts/shorts.py episodes/<slug> 70-112 --hook "GTA 6 HAS A SECRET?"
"""
import argparse
import re
from pathlib import Path
import subprocess


def secs(t: str) -> float:
    parts = [float(p) for p in t.split(":")]
    s = 0.0
    for p in parts:
        s = s * 60 + p
    return s


def srt_to_ass(srt: Path, start: float, end: float, ass: Path, hook: str | None):
    def ts(t):
        cs = int(round(max(0, t) * 100))
        return f"{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}"

    rows = []
    for block in (srt.read_text().strip().split("\n\n") if srt.exists() else []):
        lines = block.splitlines()
        if len(lines) < 3:
            continue
        m = re.findall(r"(\d+):(\d+):(\d+),(\d+)", lines[1])
        s, e = [int(h) * 3600 + int(mi) * 60 + int(se) + int(ms) / 1000 for h, mi, se, ms in m]
        if e > start and s < end:
            rows.append(f"Dialogue: 0,{ts(s-start)},{ts(e-start)},Cap,,0,0,0,,{' '.join(lines[2:]).upper()}\n")
    if hook:
        rows.append(f"Dialogue: 1,{ts(0)},{ts(3)},Hook,,0,0,0,,{hook.upper()}\n")
    ass.write_text(f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,DejaVu Sans,82,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,2,60,60,520,1
Style: Hook,DejaVu Sans,88,&H0000D4FF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,2,8,60,60,260,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "".join(rows))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("ranges", nargs="+", help="inicio-fim (seg ou hh:mm:ss)")
    ap.add_argument("--video", default=None, help="padrão: out/video.mp4")
    ap.add_argument("--hook", action="append", default=[], help="texto no topo nos 3s iniciais (1 por short)")
    a = ap.parse_args()

    ep = Path(a.episode)
    video = Path(a.video) if a.video else ep / "out" / "video.mp4"
    srt = ep / "out" / "captions.srt"
    (ep / "out").mkdir(exist_ok=True)
    for i, r in enumerate(a.ranges, 1):
        s, e = (secs(x) for x in r.split("-"))
        if e - s > 59:
            print(f"  ! short {i} tem {e-s:.0f}s; Shorts ideais têm até 59s")
        ass = ep / "build" / f"short_{i}.ass"
        ass.parent.mkdir(exist_ok=True)
        hook = a.hook[i - 1] if i - 1 < len(a.hook) else None
        srt_to_ass(srt, s, e, ass, hook)
        # o vídeo longo já tem legenda queimada embaixo: cortamos a faixa de baixo (15%)
        fc = ("[0:v]split[a][b];"
              "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.15[bg];"
              "[b]crop=iw:ih*0.85:0:0,scale=1080:-2[fg];"
              f"[bg][fg]overlay=(W-w)/2:(H-h)/2-80,subtitles='{ass.resolve()}'[v]")
        out = ep / "out" / f"short_{i}.mp4"
        subprocess.run(["ffmpeg", "-y", "-ss", str(s), "-to", str(e), "-i", str(video), "-filter_complex", fc,
                        "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)],
                       check=True, capture_output=True)
        print(f"[shorts] ok -> {out}  ({e-s:.0f}s)")


if __name__ == "__main__":
    main()
