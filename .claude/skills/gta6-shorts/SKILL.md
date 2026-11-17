---
name: gta6-shorts
description: Escolhe os 3 melhores trechos do vídeo longo e corta Shorts 9:16 com gancho no topo. Use para "shorts", "cortes", "reels", "tiktok".
---
# Shorts

1. Leia `$EP/out/captions.srt` (com `grep`/`head` se longo). Escolha 3 trechos de 25–55s que funcionem sozinhos:
   começam com afirmação forte/mistério e terminam numa revelação. Evite trechos que dependem de contexto.
2. Para cada um, um hook de 2–4 palavras (EN, caixa alta) diferente do primeiro frase falada.
3. Rode: `python scripts/shorts.py $EP 70-112 205-250 400-447 --hook "HOOK 1" --hook "HOOK 2" --hook "HOOK 3"`
4. Acrescente em `$EP/meta.md` uma seção "Shorts" com título (≤40 chars + #gta6 #shorts) para cada short,
   e "Related video" apontando para o longo.
