---
name: gta6-render
description: Renderiza o vídeo final (FFmpeg) com Ken Burns, legendas queimadas, música com ducking e loudness de YouTube. Use para "renderiza", "monta o vídeo", "gera o mp4", "preview".
---
# Render

1. Checar mídias faltando sem abrir arquivos:
   `python -c "import json,os;c=json.load(open('$EP/scenes.json'));[print('FALTA',m) for s in c['scenes'] for m in ([s['media']] if isinstance(s.get('media'),str) else s.get('media',[])) if not os.path.exists('$EP/'+m)]"`
   Se faltar, avise (vira tela escura) e pergunte se segue.
2. Preview (opcional, rápido): `python scripts/render.py $EP --preview`
3. Final: `python scripts/render.py $EP` → `$EP/out/video.mp4` + `captions.srt` (subir também como legenda no YouTube).
   Sem legenda queimada: `--no-subs`.

Ajustes comuns: música alta/baixa → `music_volume` no scenes.json; trocar imagem → substitua o arquivo e re-renderize.
Não leia arquivos de `build/`. Erros do ffmpeg aparecem resumidos no output.
