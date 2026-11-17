# GTA 6 Dark Channel — pipeline de produção com Claude Code

Pipeline para um canal faceless sobre GTA 6, em inglês, voltado para os EUA. O Claude Code escreve
pauta, roteiro, cenas e SEO usando **skills**. Voz, transcrição, edição, thumbnail e Shorts rodam em
**scripts locais grátis**. Fora o plano Claude Pro, o custo é **zero**: nenhuma API paga.

## Construído sobre projetos consolidados (nada reinventado)

| Etapa | Projeto | Por quê |
|---|---|---|
| Baixar áudio / clipes oficiais | [yt-dlp](https://github.com/yt-dlp/yt-dlp) | padrão da indústria, atualizado toda semana |
| Transcrição local | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Whisper da OpenAI até 4x mais rápido, roda em CPU |
| Voz neural grátis | [edge-tts](https://github.com/rany2/edge-tts) | vozes neurais da Microsoft, com marcação de tempo por palavra |
| Edição / render | [FFmpeg](https://ffmpeg.org) | Ken Burns, legendas (libass), ducking, loudnorm |
| Vídeos com pessoas reais | [Mixkit](https://mixkit.co) | banco grátis, licença libera uso monetizado |
| Thumbnail | [Pillow](https://github.com/python-pillow/Pillow) | |
| Voz offline (opcional) | [Kokoro-82M](https://github.com/hexgrad/kokoro) | open source, qualidade top, sem internet |

Referências de pipelines parecidos, se quiser comparar:
[MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) (gerador de vídeos curtos com UI) e
[ShortGPT](https://github.com/RayVentura/ShortGPT). Este repositório é mais enxuto e feito para o Claude Code dirigir.

## Instalação (no seu PC)

Requisitos: Python 3.10+, FFmpeg no PATH ([Windows](https://www.gyan.dev/ffmpeg/builds/): baixe e adicione ao PATH;
macOS: `brew install ffmpeg`; Linux: `apt install ffmpeg`) e [Claude Code](https://claude.com/claude-code),
que já vem incluso no plano Pro.

```bash
git clone https://github.com/victorpsampaio/gta6-dark-channel.git
```

```bash
cd gta6-dark-channel && python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

Coloque uma música de fundo em `assets/music/bg.mp3` (use a Biblioteca de áudio do YouTube, que é grátis e sem copyright).

## Uso no Claude Code

```bash
claude
```

Depois, no chat:

- `/video-completo` faz um vídeo inteiro, parando só quando precisa de você.
- Também dá para chamar cada etapa: `/gta6-pauta`, `/fonte-para-roteiro`, `/gta6-roteiro`, `/plano-de-edicao`,
  `/narracao`, `/gta6-render`, `/titulo-thumb-seo`, `/gta6-shorts`, `/checklist-publicacao`.

## Fluxo

```
pauta → transcribe.py (vídeos gringos = só pesquisa) → brief.md (fatos + ângulo próprio)
      → script.md (EN-US, 8–12 min) → scenes.json + SHOTLIST.md → você coloca as mídias em media/
      → tts.py → render.py → thumbnail.py + meta.md → shorts.py → checklist
```

## Scripts (também funcionam sem o Claude)

```bash
python scripts/trending.py "GTA 6"                 # vídeos gringos em alta agora (recentes x views)
./scripts/new_episode.sh gta6-map-size
python scripts/stock.py search gamer party miami --out stock_preview   # vídeos grátis com pessoas reais
python scripts/stock.py get episodes/... stock_preview 3 42 84
python scripts/fetch_clip.py episodes/... "https://youtube.com/watch?v=..." 1:12-1:19 --name trailer2
python scripts/transcribe.py episodes/2026-11-17-gta6-map-size "https://youtube.com/watch?v=..."
python scripts/tts.py episodes/2026-11-17-gta6-map-size
python scripts/render.py episodes/2026-11-17-gta6-map-size --preview
python scripts/render.py episodes/2026-11-17-gta6-map-size
python scripts/thumbnail.py episodes/.../media/01.jpg "THE MAP IS HUGE" -o episodes/.../out/thumb.png
python scripts/shorts.py episodes/... 70-112 205-250 --hook "NOBODY NOTICED" --hook "WAIT WHAT"
```

O formato do `scenes.json` está em [`examples/scenes.example.json`](examples/scenes.example.json).

## Como economizar o limite do plano Pro

- O `CLAUDE.md` proíbe o Claude de abrir mídias e transcrições inteiras.
- Use `/model sonnet` no dia a dia e guarde o Opus para revisar roteiro.
- `tts.py --only N` regrava uma cena só.
- Rode `/clear` entre um vídeo e outro.
- Opcional: para o Claude não pedir permissão a cada script, crie `.claude/settings.local.json` com:
  ```json
  { "permissions": { "allow": ["Bash(python scripts/*)", "Bash(./scripts/new_episode.sh *)", "Bash(ffprobe *)", "Bash(yt-dlp *)"] } }
  ```

## ⚠️ Regras para não perder o canal

- **Não reenvie vídeos de outros canais.** Isso dá *reused content* (sem monetização) e strikes de copyright.
  Aqui, vídeos gringos são só **fonte de informação**: a transcrição vira fatos, e o roteiro é sempre original.
- Imagens: trailers e screenshots oficiais da Rockstar, seu gameplay, artes de IA. Trechos de terceiros só curtos,
  com comentário por cima e crédito.
- Voz de IA: declare na descrição. Imagens de IA realistas: marque "Altered or synthetic content" no YouTube Studio.
- Rumor é rumor: diga "reportedly" ou "according to leaks".
