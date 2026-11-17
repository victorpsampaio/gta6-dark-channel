---
name: narracao
description: Gera a narração com voz neural grátis (edge-tts) a partir do scenes.json. Use para "gera a voz", "narração", "troca a voz", "regrava a cena N".
---
# Narração

- Tudo: `python scripts/tts.py $EP`
- Só algumas cenas (após editar o texto): `python scripts/tts.py $EP --only 3 7`
- Trocar voz/velocidade: editar `voice`/`rate` no scenes.json ou `--voice en-US-GuyNeural --rate +8%`
- Listar vozes: `python scripts/tts.py --list-voices`

Pronúncia: se uma palavra sair errada, reescreva foneticamente no `text` (ex.: "Leonida" → "Leh-oh-nee-dah" se preciso).
Não abra os mp3. Reporte só o total de minutos que o script imprime.
Erro de rede/403: edge-tts precisa de acesso a speech.platform.bing.com.
