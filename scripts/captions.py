"""Legendas compartilhadas (render.py e clipper.py).

- restore_punctuation: recupera pontuação do roteiro nas palavras do TTS/Whisper
- group_words: agrupa palavras em blocos curtos (quebra no fim da frase)
- karaoke_events: estilo "Shorts/Hormozi" — bloco na tela e a palavra falada
  destacada (cor + leve pop), evento por palavra.
"""
import re


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def restore_punctuation(words, text):
    tokens, j, out = text.split(), 0, []
    for wd in words:
        w = dict(wd)
        nw = _norm(w["w"])
        for k in range(j, min(j + 4, len(tokens))):
            if nw and _norm(tokens[k]) == nw:
                w["w"], j = tokens[k], k + 1
                break
        out.append(w)
    return out


def group_words(words, max_words=5, max_len=2.4):
    """Retorna lista de grupos (listas de palavras)."""
    cues, cur = [], []
    for wd in words:
        cur.append(wd)
        end = re.search(r"[.!?]$", wd["w"]) or (re.search(r"[,;:]$", wd["w"]) and len(cur) >= 2)
        if len(cur) >= max_words or end or cur[-1]["end"] - cur[0]["start"] > max_len:
            cues.append(cur)
            cur = []
    if cur:
        cues.append(cur)
    return cues


def ts_ass(t):
    cs = int(round(max(0.0, t) * 100))
    return f"{cs//360000}:{cs//6000%60:02d}:{cs//100%60:02d}.{cs%100:02d}"


def ts_srt(t):
    ms = int(round(max(0.0, t) * 1000))
    return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"


def _esc(s):
    return s.replace("{", "(").replace("}", ")").replace("\n", " ")


def ass_header(w, h, styles):
    head = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {w}\nPlayResY: {h}\nWrapStyle: 0\n\n"
            "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
            "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, "
            "Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
    return head + "".join(f"Style: {s}\n" for s in styles) + \
        "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"


def style(name, size, align=2, margin_v=80, primary="&H00FFFFFF", outline=None, border=1, back="&H80000000",
          bold=-1, font="DejaVu Sans"):
    outline = outline if outline is not None else max(2, size // 12)
    return (f"{name},{font},{size},{primary},&H000000FF,&H00000000,{back},{bold},0,0,0,100,100,0,0,"
            f"{border},{outline},2,{align},60,60,{margin_v},1")


def karaoke_events(groups, offset=0.0, style_name="Cap", hl="&H0000D4FF&", upper=True, pop=112):
    """Um evento por palavra: o bloco inteiro aparece e a palavra atual fica destacada."""
    ev = []
    for g in groups:
        txt = [(_esc(x["w"].upper() if upper else x["w"])) for x in g]
        for i, wd in enumerate(g):
            s = wd["start"] if i else g[0]["start"]
            e = g[i + 1]["start"] if i + 1 < len(g) else g[-1]["end"]
            if e - s < 0.04:
                continue
            parts = [f"{{\\c{hl}\\fscx{pop}\\fscy{pop}}}{t}{{\\r}}" if k == i else t for k, t in enumerate(txt)]
            ev.append(f"Dialogue: 0,{ts_ass(s + offset)},{ts_ass(e + offset)},{style_name},,0,0,0,,"
                      f"{' '.join(parts)}\n")
    return ev


def plain_events(groups, offset=0.0, style_name="Cap", upper=True):
    return [f"Dialogue: 0,{ts_ass(g[0]['start'] + offset)},{ts_ass(g[-1]['end'] + offset)},{style_name},,0,0,0,,"
            f"{_esc(' '.join(x['w'] for x in g).upper() if upper else ' '.join(x['w'] for x in g))}\n"
            for g in groups]


def srt_from_groups(groups, offset=0.0):
    return "\n".join(f"{i}\n{ts_srt(g[0]['start'] + offset)} --> {ts_srt(g[-1]['end'] + offset)}\n"
                     f"{' '.join(x['w'] for x in g)}\n" for i, g in enumerate(groups, 1))
