---
name: cortes-live
description: Faz cortes de LIVES do YouTube (ao vivo ou já encerradas/VOD), com layout de streamer (câmera em cima, jogo embaixo) e detecção de momentos de reação/hype. Use para "corta a live", "clips da live", "melhores momentos da stream", "cortes ao vivo".
---
# Cortes de live

Igual à skill `cortes-youtube`, com estas diferenças:

1. **Baixar só o que importa** (lives são longas):
   - Live **acontecendo agora**: `python scripts/clipper.py prep "<URL da live>" --live-last 30 --out clips/live-<data>`
     (últimos 30 min; repita a cada meia hora para acompanhar a live).
   - Live **encerrada (VOD)**: `--section 1:10:00-1:50:00` para um bloco, ou sem `--section` se tiver ≤ 1h.
2. **Achar momentos**: em live, o melhor sinal é o **pico de volume** (grito, risada, reação a clutch/fail) →
   comece por `candidates.md`. Confirme na transcrição ±30s em volta de cada pico. Bom corte de live = contexto curto
   (5–10s antes) + reação + 2–3s depois.
3. **Layout**: `"layout": "split"` quando houver facecam (rosto em cima 40%, jogo embaixo 60%); `face` para just chatting;
   `fit` se não houver câmera. O `auto` escolhe `face` quando acha rosto — para streams de jogo prefira `split`.
4. Hooks curtos em CAIXA ALTA e títulos com o nome do streamer/jogo (ex.: "xQc reacts to GTA 6 map #shorts").

Regras de direitos: as mesmas da `cortes-youtube` — corte lives suas, de streamers com programa de cortes, ou com permissão,
sempre com crédito.
