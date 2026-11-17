---
name: video-completo
description: Produz um vídeo inteiro do canal GTA 6 do zero (pauta → pesquisa → roteiro → cenas → voz → render → thumb → SEO → shorts → checklist). Use quando o usuário pedir "faz um vídeo sobre X", "novo vídeo", "/video-completo".
---
# Vídeo completo

Execute as etapas em ordem, pausando SÓ onde marcado ⏸ (precisa do usuário).

1. Se não houver tema: rode a skill `gta6-pauta` e peça ao usuário escolher ⏸.
2. `./scripts/new_episode.sh <slug>` → guarde o caminho `EP`.
3. Peça 1–3 URLs de vídeos-fonte (gringos) ⏸ e rode `python scripts/transcribe.py $EP <urls>`.
4. Skill `fonte-para-roteiro` → `$EP/brief.md`.
5. Skill `gta6-roteiro` → `$EP/script.md`. Mostre só o gancho (primeiras 3 frases) e pergunte se aprova ⏸.
6. Skill `plano-de-edicao` → `$EP/scenes.json` + `$EP/media/SHOTLIST.md`.
7. ⏸ Usuário coloca as mídias em `$EP/media/` seguindo o SHOTLIST (pode deixar faltando; vira tela escura).
8. Skill `narracao` (tts.py) → skill `gta6-render`.
9. Skill `titulo-thumb-seo` → `$EP/meta.md` + `$EP/out/thumb.png`.
10. Skill `gta6-shorts` → `$EP/out/short_N.mp4`.
11. Skill `checklist-publicacao` e entregue o resumo final (arquivos + o que falta fazer no YouTube Studio).

Mantenha o chat enxuto: escreva nos arquivos, informe só caminhos e decisões.
