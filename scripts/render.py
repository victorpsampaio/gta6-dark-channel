#!/usr/bin/env python3
"""Monta o vídeo final só com FFmpeg (grátis, roda local).

Entrada: episodes/<slug>/scenes.json + audio/manifest.json (gerado por tts.py)
Saída:   out/video.mp4 (legendado, com música abaixada sob a voz) + out/captions.srt

Cada cena pode ter 1 ou várias mídias (imagem ou vídeo). O tempo da cena é
dividido igualmente entre elas -> troca de imagem a cada poucos segundos
(retenção). Imagens ganham movimento (Ken Burns); vídeos são cortados/loopados.

Uso:
  python scripts/render.py episodes/<slug>
  python scripts/render.py episodes/<slug> --preview      # 480p rápido p/ conferir

Opções no scenes.json (todas opcionais):
  "captions": "karaoke" | "plain"     (karaoke = palavra falada destacada, padrão)
  "transition": "flash" | "none"      (flash branco curto na troca de cena, padrão)
  "video_zoom": true | false          (zoom lento nos clipes de vídeo, padrão true)
Segmentos ficam em cache (build/cache): mudar só texto/legenda re-renderiza rápido.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions as C  # noqa: E402

FPS = 30
GAP = 0.25  # respiro entre cenas (s)
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
MOTIONS = ["zoom_in", "pan_right", "zoom_out", "pan_left"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"ffmpeg falhou:\n{' '.join(map(str, cmd))}\n{r.stderr[-2000:]}")


def resolve(ep: Path, p: str) -> Path:
    for base in (ep, Path.cwd()):
        if (base / p).exists():
            return base / p
    return ep / p


def zoompan(motion: str, n: int, w: int, h: int) -> str:
    z, x, y = "1", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    if motion == "zoom_in":
        z = f"1+0.15*on/{n}"
    elif motion == "zoom_out":
        z = f"1.15-0.15*on/{n}"
    elif motion == "pan_right":
        z, x = "1.15", f"(iw-iw/zoom)*on/{n}"
    elif motion == "pan_left":
        z, x = "1.15", f"(iw-iw/zoom)*(1-on/{n})"
    return (f"scale={w*2}:{h*2}:force_original_aspect_ratio=increase,crop={w*2}:{h*2},"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={w}x{h}:fps={FPS},setsar=1")


def render_segment(src: Path, frames: int, out: Path, w: int, h: int, motion: str, clip_start: float, crf: str,
                   flash: bool = False, video_zoom: bool = True):
    enc = ["-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", crf, "-pix_fmt", "yuv420p",
           "-frames:v", str(frames), str(out)]
    dur = frames / FPS
    fx = ",fade=t=in:st=0:d=0.12:color=white" if flash else ""
    cover = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={FPS},setsar=1"
    if not src.exists():
        print(f"  ! mídia não encontrada: {src} (usando tela escura)")
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x111111:s={w}x{h}:r={FPS}", "-t", f"{dur}", *enc])
    elif src.suffix.lower() in IMG_EXT:
        if motion == "none":
            run(["ffmpeg", "-y", "-loop", "1", "-i", str(src), "-vf", cover + fx, *enc])
        else:
            run(["ffmpeg", "-y", "-i", str(src), "-vf", zoompan(motion, frames, w, h) + fx, *enc])
    else:
        vf = cover
        if video_zoom:  # zoom lento (punch-in) também nos clipes de vídeo
            vf += (f",zoompan=z='min(1+0.10*on/{max(frames, 1)},1.10)':d=1:"
                   f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={w}x{h}:fps={FPS},setsar=1")
        run(["ffmpeg", "-y", "-stream_loop", "-1", "-ss", f"{clip_start}", "-i", str(src),
             "-t", f"{dur + 1}", "-vf", vf + fx, *enc])


def cached_segment(cache: Path, src: Path, *args, **kw) -> Path:
    """Reaproveita o segmento se mídia e parâmetros não mudaram."""
    mt = src.stat().st_mtime if src.exists() else 0
    key = hashlib.sha1(json.dumps([str(src), mt, args, kw], sort_keys=True).encode()).hexdigest()[:16]
    out = cache / f"{key}.mp4"
    if not out.exists():
        render_segment(src, args[0], out, *args[1:], **kw)
    return out


# ---------- legendas ----------
def write_subs(groups_with_offset, lower_thirds, w, h, ass_path: Path, srt_path: Path, mode="karaoke"):
    fs = int(h * 0.065)
    lines = [C.ass_header(w, h, [C.style("Cap", fs, 2, int(h * 0.08)),
                                 C.style("Src", int(h * 0.028), 7, 40, border=3, outline=4, bold=0,
                                         back="&HA0000000")])]
    srt_groups = []
    for g, off in groups_with_offset:
        lines += (C.karaoke_events if mode == "karaoke" else C.plain_events)([g], off)
        srt_groups.append([{**x, "start": x["start"] + off, "end": x["end"] + off} for x in g])
    for s, e, t in lower_thirds:
        lines.append(f"Dialogue: 1,{C.ts_ass(s)},{C.ts_ass(e)},Src,,0,0,0,,{t}\n")
    ass_path.write_text("".join(lines))
    srt_path.write_text(C.srt_from_groups(srt_groups))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--preview", action="store_true", help="480p rápido")
    ap.add_argument("--no-subs", action="store_true")
    a = ap.parse_args()

    ep = Path(a.episode)
    cfg = json.loads((ep / "scenes.json").read_text())
    man = json.loads((ep / "audio" / "manifest.json").read_text())
    w, h = (854, 480) if a.preview else tuple(cfg.get("resolution", [1920, 1080]))
    crf = "28" if a.preview else "20"

    work = ep / "build"
    cache = work / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    flash_on = cfg.get("transition", "flash") == "flash"
    vzoom = cfg.get("video_zoom", True)
    (ep / "out").mkdir(exist_ok=True)

    seg_list, cues, lowers, narr_inputs = [], [], [], []
    t0 = 0.0
    total_frames = 0
    seg_i = 0
    for i, scene in enumerate(cfg["scenes"], 1):
        info = man[f"scene_{i:02d}"]
        dur = info["duration"] + GAP
        scene_end_frame = round((t0 + dur) * FPS)
        media = scene.get("media") or []
        media = [media] if isinstance(media, str) else media
        media = media or [""]
        # divide frames da cena entre as mídias
        start_f = total_frames
        for j, m in enumerate(media):
            end_f = start_f + round((scene_end_frame - start_f) / (len(media) - j))
            frames = end_f - start_f
            seg_i += 1
            motion = scene.get("motion") or MOTIONS[seg_i % len(MOTIONS)]
            src = resolve(ep, m) if m else Path("/nonexistent")
            seg = cached_segment(cache, src, frames, w, h, motion, float(scene.get("clip_start", 0)), crf,
                                 flash=flash_on and j == 0 and i > 1, video_zoom=vzoom)
            seg_list.append(seg)
            start_f = end_f
        total_frames = scene_end_frame

        for g in C.group_words(C.restore_punctuation(info["words"], scene["text"]),
                               max_words=4 if cfg.get("captions", "karaoke") == "karaoke" else 5):
            cues.append((g, t0))
        if scene.get("lower_third"):
            lowers.append((t0, t0 + min(dur, 5), scene["lower_third"]))
        narr_inputs.append((ep / "audio" / info["file"], dur))
        print(f"[render] cena {i}/{len(cfg['scenes'])}  {dur:.1f}s  {len(media)} mídia(s)")
        t0 = total_frames / FPS

    # 1) junta os segmentos de vídeo
    lst = work / "list.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in seg_list))
    visual = work / "visual.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(visual)])

    # 2) narração contínua (cada cena com padding até sua duração)
    cmd = ["ffmpeg", "-y"]
    for f, _ in narr_inputs:
        cmd += ["-i", str(f)]
    filt = "".join(f"[{k}:a]aresample=48000,apad=whole_dur={d:.3f}[a{k}];" for k, (_, d) in enumerate(narr_inputs))
    filt += "".join(f"[a{k}]" for k in range(len(narr_inputs))) + f"concat=n={len(narr_inputs)}:v=0:a=1[out]"
    narr = work / "narration.wav"
    run(cmd + ["-filter_complex", filt, "-map", "[out]", str(narr)])

    # 3) legendas
    ass, srt = work / "subs.ass", ep / "out" / "captions.srt"
    write_subs(cues, lowers, w, h, ass, srt, cfg.get("captions", "karaoke"))

    # 4) mix final: música com ducking + legendas queimadas
    out = ep / "out" / ("preview.mp4" if a.preview else "video.mp4")
    cmd = ["ffmpeg", "-y", "-i", str(visual), "-i", str(narr)]
    music = cfg.get("music")
    vf = "null" if a.no_subs else f"subtitles='{ass.resolve()}'"
    if music and resolve(ep, music).exists():
        vol = cfg.get("music_volume", 0.18)
        cmd += ["-stream_loop", "-1", "-i", str(resolve(ep, music))]
        fc = (f"[0:v]{vf}[v];[1:a]asplit=2[n1][n2];[2:a]volume={vol}[m];"
              f"[m][n1]sidechaincompress=threshold=0.02:ratio=10:attack=20:release=400[md];"
              f"[n2][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    else:
        fc = f"[0:v]{vf}[v];[1:a]loudnorm=I=-14:TP=-1.5[a]"
    run(cmd + ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset",
               "veryfast" if a.preview else "medium", "-crf", crf, "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)])
    print(f"[render] ok -> {out}  ({t0/60:.1f} min)  legendas: {srt}")


if __name__ == "__main__":
    main()
