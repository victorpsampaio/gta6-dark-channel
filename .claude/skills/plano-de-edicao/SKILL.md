---
name: plano-de-edicao
description: Converte script.md em scenes.json (o formato que render.py lê) e gera a lista de mídias a buscar (SHOTLIST.md). Use após o roteiro aprovado ou para "monta as cenas", "plano de edição".
---
# Plano de edição

Leia `$EP/script.md`. Escreva `$EP/scenes.json`:
```json
{
  "title": "...", "voice": "en-US-AndrewNeural", "rate": "+4%",
  "music": "assets/music/bg.mp3", "music_volume": 0.18,
  "scenes": [
    {"text": "texto narrado exato", "media": ["media/03a.jpg", "media/03b.mp4"],
     "clip_start": 0, "motion": "zoom_in", "lower_third": "Source: Rockstar Games – Trailer 2"}
  ]
}
```
Regras:
- `text`: só o que será falado (sem as linhas [VISUAL]). 1 parágrafo = 1 cena.
- `media`: 1 mídia a cada ~4–6s de fala (≈ 12–15 palavras por mídia). Nomeie `NNx.jpg|mp4` na ordem.
- `motion` opcional (zoom_in, zoom_out, pan_left, pan_right, none); se omitido alterna sozinho.
- `clip_start`: segundo onde começar o clipe de vídeo.
- `lower_third` quando usar material de terceiros (crédito) — ou omita.
- Chaves `music`: só se existir arquivo em assets/music/ (senão remova).

Depois escreva `$EP/media/SHOTLIST.md`: tabela `arquivo | o que mostrar | onde conseguir`
(ex.: "Trailer 2 oficial 1:12 — yt-dlp do canal Rockstar Games", "screenshot oficial rockstargames.com/VI",
"gerar no Bing Image Creator: prompt ..."). Para clipes de trailer oficial, dê o comando:
`yt-dlp -f "bv*[height<=1080]+ba/b" --download-sections "*72-80" -o "$EP/media/05a.%(ext)s" <URL oficial>`.
