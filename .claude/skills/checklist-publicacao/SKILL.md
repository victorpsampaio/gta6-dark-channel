---
name: checklist-publicacao
description: Checklist final antes de publicar (direitos autorais, originalidade, aviso de IA, metadados, arquivos). Use antes de subir no YouTube ou ao pedir "checklist", "posso publicar?".
---
# Checklist de publicação

Verifique (sem abrir mídias) e responda em lista ✅/⚠️/❌:

**Originalidade / monetização**
- Roteiro reescrito? Compare 3–4 frases de `script.md` com `sources/*/transcript.txt` via grep — nenhuma frase igual.
- Narração própria em todo o vídeo; nenhum trecho longo de vídeo de outro criador em `media/` (pergunte ao usuário a origem de clipes .mp4 que não sejam oficiais).
- Trechos de terceiros < 10s cada, com `lower_third` de crédito.

**Arquivos**: `out/video.mp4`, `out/captions.srt`, `out/thumb.png` (1280x720), `out/short_*.mp4`, `meta.md` completo.
Duração: `ffprobe -v error -show_entries format=duration -of csv=p=0 $EP/out/video.mp4`.

**YouTube Studio (lembrar o usuário)**
- Marcar "Altered or synthetic content" = Sim se houver imagens IA realistas; voz IA narrando é ok mas declare na descrição.
- Público: "Not made for kids". Idioma: English. Legenda: subir `captions.srt`.
- Tela final + cards para vídeo anterior. Agendar para 12h–15h ET.
- Rumores marcados como rumor no título/thumbnail? (Evitar clickbait enganoso = strike de spam.)
