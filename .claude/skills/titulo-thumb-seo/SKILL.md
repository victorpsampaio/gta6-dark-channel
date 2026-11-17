---
name: titulo-thumb-seo
description: Cria títulos, texto e imagem de thumbnail, descrição com capítulos e tags para YouTube EUA, e gera a thumb com thumbnail.py. Use para "título", "thumbnail", "SEO", "descrição".
---
# Título, thumb e SEO

Leia `$EP/script.md` (e `$EP/brief.md` → Sources). Escreva `$EP/meta.md`:

1. **5 títulos** (≤60 caracteres, EN-US): curiosidade + palavra-chave "GTA 6" no começo quando natural. Marque o favorito.
   Ex.: "GTA 6: 27 Details You Completely Missed", "GTA 6's Map Is Bigger Than You Think".
2. **Texto da thumb**: 2–4 palavras, complementa o título (não repete). 3 opções.
3. **Imagem de fundo**: qual arquivo de `media/` usar, ou prompt para gerador grátis (Bing Image Creator/Ideogram).
4. **Descrição**: 2 linhas de gancho com palavra-chave, parágrafo resumo, **capítulos** (`00:00 Intro` …
   tempos a partir de `audio/manifest.json`: some `duration`+0.25 de cada cena), Sources do brief, aviso
   "Narration uses AI voice. Footage © Rockstar Games, used for commentary/news under fair use.", 3 hashtags.
5. **Tags**: 15 tags separadas por vírgula (≤500 caracteres).

Depois gere a thumb:
`python scripts/thumbnail.py $EP/media/<bg> "<TEXTO>" -o $EP/out/thumb.png --side left --color "#FFD400"`
