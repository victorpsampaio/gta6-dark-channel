# Canal dark GTA 6 (EUA) — guia para o Claude Code

Canal faceless em **inglês americano** sobre GTA 6: notícias, análises, segredos, teorias, guias.
Toda a produção pesada roda em **scripts locais grátis** (`scripts/`). O Claude só escreve texto.

## Regras de economia (plano Pro — não estourar limite)
- NUNCA ler arquivos de mídia (mp4/mp3/jpg) nem `build/`. Use `ls`, `ffprobe` se precisar.
- Transcrições: leia com `head -c 12000` ou `grep -n`, não o arquivo inteiro, a menos que seja curto.
- Não reexecutar `tts.py` inteiro para corrigir uma cena: use `--only N`.
- Use `render.py --preview` antes do render final só se o usuário pedir conferência.
- Respostas curtas. Não repetir o roteiro inteiro no chat — escreva no arquivo.

## Regras do canal (obrigatórias)
- **Nunca** reenviar/reaproveitar vídeo de outro criador. Vídeos gringos = só fonte de informação
  (via `scripts/transcribe.py`). Roteiro sempre reescrito, com análise e opinião próprias.
- Imagens/vídeos permitidos em `media/`: material oficial da Rockstar (trailers, screenshots,
  site oficial), gameplay próprio, artes geradas por IA, imagens livres. Trechos de terceiros só
  curtos (<10s), com comentário por cima e crédito em `lower_third`.
- Fonte de toda informação vai para a descrição (`meta.md` → seção Sources).
- Rumor ≠ fato: diga "reportedly", "according to leaks" quando não for oficial.
- Voz é IA: marcar "Altered or synthetic content" no YouTube Studio quando aplicável.

## Estrutura de um episódio
```
episodes/AAAA-MM-DD-slug/
  sources/<id>/transcript.txt, meta.json   # pesquisa (transcribe.py)
  brief.md        # fatos + ângulo (skill fonte-para-roteiro)
  script.md       # roteiro (skill gta6-roteiro)
  scenes.json     # cenas: texto narrado + mídias (skill plano-de-edicao)
  media/          # imagens e clipes (o usuário coloca / baixa)
  audio/          # gerado por tts.py
  out/            # video.mp4, captions.srt, thumb.png, short_N.mp4
  meta.md         # títulos, descrição, tags (skill titulo-thumb-seo)
```

## Comandos
```
python scripts/trending.py "GTA 6"                   # o que está em alta (yt-dlp)
./scripts/new_episode.sh <slug>
python scripts/transcribe.py <ep> <url...>          # yt-dlp + faster-whisper
python scripts/stock.py search gamer party --out stock_preview   # pessoas reais (Mixkit)
python scripts/stock.py get <ep> stock_preview 3 42
python scripts/fetch_clip.py <ep> <URL> 1:12-1:19 --name trailer2  # trecho do YouTube (PC)
python scripts/clipper.py prep "<URL>" --out clips/<slug> [--live-last 30]  # cortes YouTube/live
python scripts/clipper.py cut clips/<slug> [--layout split]
python scripts/tts.py <ep> [--only 3 5]              # edge-tts (cache: só regrava cenas alteradas)
python scripts/render.py <ep> [--preview]            # ffmpeg
python scripts/thumbnail.py <img> "TEXT" -o <ep>/out/thumb.png
python scripts/shorts.py <ep> 70-112 200-245 --hook "TEXT" --hook "TEXT"
```

## Voz e estilo
- Voz padrão: `en-US-AndrewNeural`, rate `+4%`. Alternativas: `en-US-GuyNeural`, `en-US-BrianNeural`.
- Tom: documentário misterioso/empolgado, frases curtas, 2ª pessoa ("you"), sem enrolação.
- Render dinâmico (padrão): legenda karaokê, flash na troca de cena, zoom lento nos clipes.
  Desligar no scenes.json: "captions": "plain", "transition": "none", "video_zoom": false.
- Cortes de vídeo/live: skills `cortes-youtube` e `cortes-live` (só conteúdo próprio, com programa de cortes ou permissão).
- Vídeo longo: 8–12 min (~1.300–1.900 palavras a ~155 wpm).
