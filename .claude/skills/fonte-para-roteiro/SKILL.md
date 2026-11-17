---
name: fonte-para-roteiro
description: Transforma transcrições de vídeos gringos (sources/*/transcript.txt) num briefing ORIGINAL de fatos + ângulo próprio, sem copiar. Use após transcribe.py ou quando o usuário colar uma transcrição.
---
# Fonte → briefing original

Proteção contra "conteúdo reutilizado" e copyright. Leia as transcrições com `head -c 12000` (ou por partes com grep se maiores).

Escreva `$EP/brief.md` com:
1. **Fatos verificáveis** (bullet, cada um com a fonte: título do vídeo/canal de `meta.json` e minuto `[mm:ss]`).
   Marque cada item: `OFICIAL` (Rockstar/trailer/site), `RUMOR/LEAK`, ou `OPINIÃO DO CRIADOR`.
2. **O que NÃO usar**: frases de efeito, piadas, estrutura e ordem de tópicos dos originais (não copiar).
3. **Nosso ângulo**: 3 opções de abordagem diferente das fontes (ex.: comparação, ranking, teoria própria, contexto real de Miami).
   Recomende uma.
4. **Lacunas**: o que falta checar.
5. **Sources** (lista pronta para a descrição: `Channel – Title – URL`).

Nunca traduza/parafraseie a transcrição em sequência. Reescreva a partir dos fatos.
