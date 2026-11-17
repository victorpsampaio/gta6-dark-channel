#!/usr/bin/env python3
"""Cortes verticais (Shorts/TikTok/Reels) de vídeos do YouTube e de LIVES.
Grátis e local: yt-dlp + faster-whisper + OpenCV + FFmpeg.

1) PREPARAR (baixa, transcreve com tempo por palavra, acha picos de empolgação)
   python scripts/clipper.py prep "https://youtu.be/ID" --out clips/meu-corte
   python scripts/clipper.py prep "https://youtube.com/live/ID" --live-last 30 --out clips/live   # últimos 30 min de uma live AO VIVO
   python scripts/clipper.py prep "URL" --section 1:00:00-1:45:00 --out clips/vod                 # só um trecho de uma VOD longa
   python scripts/clipper.py prep arquivo_local.mp4 --out clips/x
   -> <out>/source.mp4, transcript.json, transcript.txt, peaks.tsv, candidates.md

2) ESCOLHER: escreva <out>/clips.json (a skill cortes-youtube/cortes-live faz isso):
   [{"start": "12:31", "end": "13:05", "hook": "HE DID NOT SEE THAT COMING", "title": "..."}]

3) CORTAR
   python scripts/clipper.py cut clips/meu-corte                 # layout auto
   python scripts/clipper.py cut clips/meu-corte --layout split  # câmera do streamer em cima, jogo embaixo
   layouts: auto | face (segue o rosto) | split | fit (fundo desfocado) | center
   -> <out>/out/clip_N.mp4 (1080x1920, legenda karaokê, gancho no topo, áudio normalizado)
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions as C  # noqa: E402

W, H = 1080, 1920


def secs(t) -> float:
    if isinstance(t, (int, float)):
        return float(t)
    s = 0.0
    for p in str(t).split(":"):
        s = s * 60 + float(p)
    return s


def hms(t):
    return f"{int(t//3600)}:{int(t//60%60):02d}:{int(t%60):02d}"


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise SystemExit(f"falhou: {' '.join(map(str, cmd))[:300]}\n{r.stderr[-1500:]}")
    return r


def load_audio(path: Path, sr=16000):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", str(path), "-f", "s16le",
                          "-ac", "1", "-ar", str(sr), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


# ---------------- PREP ----------------
def download(src: str, out: Path, live_last: float | None, section: str | None) -> dict:
    if Path(src).exists():
        dst = out / "source.mp4"
        if not dst.exists():
            dst.symlink_to(Path(src).resolve())
        return {"title": Path(src).name, "channel": None, "webpage_url": None}
    info = json.loads(run(["yt-dlp", "-J", "--no-playlist", src]).stdout)
    cmd = ["yt-dlp", "--no-playlist", "-f", "bv*[height<=1080]+ba/b[height<=1080]/b",
           "--merge-output-format", "mp4", "-o", str(out / "source.%(ext)s")]
    if live_last:  # live em andamento: pega os últimos N minutos
        cmd += ["--live-from-start", "--download-sections", f"*-{int(live_last*60)}-inf"]
    elif section:
        a, b = section.split("-")
        cmd += ["--download-sections", f"*{secs(a)}-{secs(b)}", "--force-keyframes-at-cuts"]
    run(cmd + [src])
    meta = {k: info.get(k) for k in ("id", "title", "channel", "uploader", "webpage_url", "is_live",
                                     "was_live", "duration", "view_count")}
    meta["section_offset"] = secs(section.split("-")[0]) if section and not live_last else 0
    return meta


def transcribe(src: Path, model_name: str) -> list:
    from faster_whisper import WhisperModel
    model = WhisperModel(model_name, device="auto", compute_type="int8")
    segs, _ = model.transcribe(load_audio(src), vad_filter=True, word_timestamps=True)
    out = []
    for s in segs:
        out.append({"start": s.start, "end": s.end, "text": s.text.strip(),
                    "words": [{"w": w.word.strip(), "start": w.start, "end": w.end} for w in (s.words or [])]})
        print(f"\r[whisper] {hms(s.end)}", end="", file=sys.stderr)
    print(file=sys.stderr)
    return out


def loud_peaks(src: Path, top=12, min_gap=45.0):
    """Momentos de empolgação: janelas de 1s com volume muito acima da média (gritos, risadas, reação)."""
    a = load_audio(src, 8000)
    win = 8000
    n = len(a) // win
    if n < 5:
        return []
    rms = np.sqrt((a[: n * win].reshape(n, win) ** 2).mean(1) + 1e-9)
    db = 20 * np.log10(rms)
    smooth = np.convolve(db, np.ones(3) / 3, mode="same")
    z = (smooth - np.median(smooth)) / (smooth.std() + 1e-6)
    peaks = []
    for i in np.argsort(-z):
        if z[i] < 1.0:
            break
        if all(abs(i - p) >= min_gap for p, _ in peaks):
            peaks.append((int(i), float(z[i])))
        if len(peaks) >= top:
            break
    return sorted(peaks)


def cmd_prep(a):
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = download(a.source, out, a.live_last, a.section)
    src = next(p for p in out.glob("source.*") if p.suffix in (".mp4", ".mkv", ".webm"))
    (out / "meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
    print(f"[clipper] fonte: {src} ({float(run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(src)]).stdout):.0f}s)")

    segs = transcribe(src, a.model)
    (out / "transcript.json").write_text(json.dumps(segs))
    (out / "transcript.txt").write_text("\n".join(f"[{hms(s['start'])}] {s['text']}" for s in segs))

    peaks = loud_peaks(src)
    (out / "peaks.tsv").write_text("".join(f"{hms(t)}\t{z:.1f}\n" for t, z in peaks))

    def ctx(t, before=20, after=25):
        return " ".join(s["text"] for s in segs if s["end"] > t - before and s["start"] < t + after)
    md = [f"# Candidatos — {meta.get('title')}\n", f"Canal: {meta.get('channel')}  URL: {meta.get('webpage_url')}\n",
          "\n## Picos de volume (reação/empolgação)\n"]
    for t, z in peaks:
        md.append(f"- **{hms(t)}** (z={z:.1f}): {ctx(t)[:400]}\n")
    md.append("\n(Leia transcript.txt com grep/head para achar falas fortes que não são picos de volume.)\n")
    (out / "candidates.md").write_text("".join(md))
    print(f"[clipper] ok -> {out}/candidates.md  ({len(segs)} trechos falados, {len(peaks)} picos)")


# ---------------- CUT ----------------
MODEL = Path(__file__).resolve().parent.parent / "assets/models/face_detection_yunet_2023mar.onnx"
MODEL_URL = "https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2023mar.onnx"


def faces_in(src: Path, s: float, e: float, step=0.5):
    """Detecta o maior rosto a cada 0.5s com YuNet (rede neural do OpenCV, pega perfil/luz colorida)."""
    import cv2
    if not MODEL.exists():
        import urllib.request
        MODEL.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(MODEL_URL, MODEL)
    cap = cv2.VideoCapture(str(src))
    vw, vh = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    k = 960 / max(vw, 1)
    det = cv2.FaceDetectorYN.create(str(MODEL), "", (int(vw * k), int(vh * k)), 0.5)
    boxes, samples, t = [], 0, s
    while t < e:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, fr = cap.read()
        t += step
        if not ok:
            continue
        samples += 1
        _, f = det.detect(cv2.resize(fr, (int(vw * k), int(vh * k))))
        if f is None:
            continue
        f = [r for r in f if r[3] / k >= vh * 0.035]  # ignora "rostos" minúsculos (falsos positivos)
        if f:
            x, y, w, h = max(f, key=lambda r: r[2] * r[3])[:4]
            boxes.append((x / k, y / k, w / k, h / k))
    cap.release()
    return boxes, samples, vw, vh


def even(v):
    return int(v) // 2 * 2


def layout_filter(layout, boxes, samples, vw, vh):
    fit = (f"[0:v]split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
           f"boxblur=25:5,eq=brightness=-0.15[bg];[b]scale={W}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-120")
    has_face = samples and len(boxes) / samples >= 0.25
    if layout == "auto":
        layout = "face" if has_face else "fit"
    if layout in ("face", "split") and not has_face:
        print("  ! nenhum rosto estável encontrado — usando 'fit'")
        layout = "fit"
    if layout == "fit":
        return fit, layout
    if layout == "center":
        cw = even(min(vw, vh * W / H))
        return f"[0:v]crop={cw}:{even(vh)}:(iw-{cw})/2:0,scale={W}:{H}", layout
    bx = np.median(np.array(boxes), axis=0)
    cx, cy, fw, fh = bx[0] + bx[2] / 2, bx[1] + bx[3] / 2, bx[2], bx[3]
    if layout == "face":  # recorte vertical centrado no rosto (mediana -> sem tremer)
        cw = even(min(vw, vh * W / H))
        x = int(np.clip(cx - cw / 2, 0, vw - cw))
        return f"[0:v]crop={cw}:{even(vh)}:{x}:0,scale={W}:{H}", layout
    # split: câmera (rosto ampliado) em cima 40%, jogo (centro do quadro) embaixo 60%
    top_h, bot_h = int(H * 0.4), H - int(H * 0.4)
    camw = min(vw, fw * 3.2)
    camh = camw * top_h / W
    if camh > vh:
        camh, camw = vh, vh * W / top_h
    camw, camh = even(camw), even(camh)
    x0 = int(np.clip(cx - camw / 2, 0, vw - camw))
    y0 = int(np.clip(cy - camh * 0.45, 0, vh - camh))
    gh = even(vh)
    gw = even(min(vw, gh * W / bot_h))
    return (f"[0:v]split[c][g];[c]crop={camw}:{camh}:{x0}:{y0},scale={W}:{top_h}[top];"
            f"[g]crop={gw}:{gh}:(iw-{gw})/2:0,scale={W}:{bot_h}[bot];[top][bot]vstack"), layout


def cmd_cut(a):
    d = Path(a.dir)
    src = next(p for p in d.glob("source.*") if p.suffix in (".mp4", ".mkv", ".webm"))
    clips = json.loads((d / "clips.json").read_text())
    segs = json.loads((d / "transcript.json").read_text())
    meta = json.loads((d / "meta.json").read_text()) if (d / "meta.json").exists() else {}
    credit = a.credit or (f"Credit: {meta['channel']}" if meta.get("channel") else "")
    (d / "out").mkdir(exist_ok=True)
    words = [w for s in segs for w in s["words"]]
    for i, c in enumerate(clips, 1):
        if a.only and i not in a.only:
            continue
        s, e = secs(c["start"]), secs(c["end"])
        boxes, samples, vw, vh = faces_in(src, s, e)
        vf, used = layout_filter(c.get("layout", a.layout), boxes, samples, vw, vh)
        # legendas karaokê do trecho (tempo relativo ao corte)
        ws = [{**w, "start": w["start"] - s, "end": w["end"] - s} for w in words if w["start"] >= s and w["end"] <= e]
        groups = C.group_words(ws, max_words=3, max_len=1.6)
        cap_y = int(H * 0.30) if used == "split" else int(H * 0.22)
        styles = [C.style("Cap", 86, 2, cap_y), C.style("Hook", 80, 8, 230, primary="&H0000D4FF"),
                  C.style("Cred", 34, 9, 40, border=3, outline=4, bold=0, back="&HA0000000")]
        ev = C.karaoke_events(groups)
        if c.get("hook"):
            ev.append(f"Dialogue: 1,{C.ts_ass(0)},{C.ts_ass(min(3.5, e - s))},Hook,,0,0,0,,{c['hook'].upper()}\n")
        if credit:
            ev.append(f"Dialogue: 1,{C.ts_ass(0)},{C.ts_ass(e - s)},Cred,,0,0,0,,{credit}\n")
        ass = d / "out" / f"clip_{i}.ass"
        ass.write_text(C.ass_header(W, H, styles) + "".join(ev))
        (d / "out" / f"clip_{i}.srt").write_text(C.srt_from_groups(groups))
        out = d / "out" / f"clip_{i}.mp4"
        fc = (f"{vf},fps=30,setsar=1,subtitles='{ass.resolve()}'[v];"
              f"[0:a]loudnorm=I=-14:TP=-1.5,afade=t=out:st={max(0, e - s - 0.4)}:d=0.4[aud]")
        run(["ffmpeg", "-y", "-ss", f"{s}", "-to", f"{e}", "-i", str(src), "-filter_complex", fc,
             "-map", "[v]", "-map", "[aud]", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)])
        print(f"[clipper] clip_{i}: {hms(s)}-{hms(e)} ({e-s:.0f}s) layout={used} -> {out}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prep")
    p.add_argument("source", help="URL do YouTube (vídeo, VOD ou live) ou arquivo local")
    p.add_argument("--out", required=True)
    p.add_argument("--model", default="small")
    p.add_argument("--live-last", type=float, help="live em andamento: baixar os últimos N minutos")
    p.add_argument("--section", help="só um trecho, ex 1:00:00-1:30:00")
    c = sub.add_parser("cut")
    c.add_argument("dir")
    c.add_argument("--layout", default="auto", choices=["auto", "face", "split", "fit", "center"])
    c.add_argument("--only", type=int, nargs="*")
    c.add_argument("--credit", help='texto de crédito no canto (padrão: "Credit: <canal>")')
    a = ap.parse_args()
    cmd_prep(a) if a.cmd == "prep" else cmd_cut(a)


if __name__ == "__main__":
    main()
