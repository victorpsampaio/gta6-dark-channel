---
name: cortes-youtube
description: Faz cortes verticais (Shorts/TikTok/Reels) de um vídeo do YouTube ou arquivo local, achando os melhores momentos pela transcrição e pelos picos de empolgação. Use para "faz cortes desse vídeo", "clips", "cortes do YouTube", ou quando o usuário colar um link do YouTube pedindo cortes.
---
# Cortes de vídeo do YouTube

Pipeline local e grátis: `scripts/clipper.py` (yt-dlp + faster-whisper + YuNet + FFmpeg).

1. **Preparar** (pasta `clips/<id-ou-slug>`):
   `python scripts/clipper.py prep "<URL>" --out clips/<slug>`
   VOD muito longa? Use `--section 0:30:00-1:30:00`. Precisa de acesso ao YouTube (rode no PC do usuário).
2. **Escolher os momentos** (o trabalho do Claude). Leia só o necessário:
   - `clips/<slug>/candidates.md` (picos de volume com contexto)
   - `grep -n -i "<palavras fortes>" clips/<slug>/transcript.txt` e `head -c 12000` por partes
   Escolha **3–6 cortes de 20–55s** que funcionem sozinhos: começam numa afirmação forte, numa pergunta ou no meio da ação
   (nada de "então, pessoal..."), têm virada ou revelação e terminam na punchline. Corte 0,3s antes da 1ª palavra.
3. Escreva `clips/<slug>/clips.json`:
   ```json
   [{"start": "12:31.5", "end": "13:05", "hook": "HE DIDN'T SEE IT COMING", "title": "…", "layout": "auto"}]
   ```
   `hook` = 2–5 palavras na língua do vídeo, aparece no topo nos 3,5s iniciais. `layout`: auto | face | split | fit | center.
4. **Cortar**: `python scripts/clipper.py cut clips/<slug>` → `clips/<slug>/out/clip_N.mp4` + `.srt`.
   Refazer só um: `--only 2`. Mudar layout de todos: `--layout split`.
5. Entregue uma tabela: arquivo | tempo | título sugerido (≤40 chars + #shorts) | por que funciona.

## Regras (direitos autorais)
- Só corte vídeos **do próprio usuário**, de criadores que **liberam cortes** (muitos streamers têm programa de cortes) ou com **permissão**.
  Pergunte se não estiver claro. Cortar vídeo de terceiros sem permissão = strike/reused content.
- O crédito (`Credit: <canal>`) entra automático no canto; coloque também o link original na descrição.
