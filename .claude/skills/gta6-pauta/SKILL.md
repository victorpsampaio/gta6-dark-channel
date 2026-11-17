---
name: gta6-pauta
description: Gera e ranqueia ideias de vídeo sobre GTA 6 para o público dos EUA. Use quando pedir "ideias", "pauta", "sobre o que fazer vídeo", "o que está em alta".
---
# Pauta GTA 6

Entrada: notícias/links/títulos que o usuário colar (se houver), ou conhecimento geral + `episodes/*/meta.md` já feitos (não repetir tema).

Para ver o que está bombando agora nos canais gringos, rode antes:
`python scripts/trending.py "GTA 6" --top 15` (vídeos recentes ordenados por views).
Use só os títulos/temas como sinal de demanda. Os vídeos escolhidos viram fonte via `transcribe.py`.
Para fatos do dia, prefira matérias de notícia (CNN, IGN, Forbes) às transcrições.

Gere 10 ideias numa tabela: `# | Título provisório (EN) | Ângulo | Tipo | Potencial (1-10) | Por quê`.

Tipos que performam em canais dark de games: segredos/easter eggs, "X things you missed", comparações (GTA 5 vs 6),
mapa/tamanho/localizações reais (Vice City ↔ Miami), personagens (Lucia, Jason), teorias, leaks (marcar como rumor),
guias pós-lançamento (dinheiro, carros raros, missões secretas), notícias de vendas/recordes.

Critérios do potencial: curiosidade + urgência + busca alta + dá para ilustrar com material oficial.
Termine com a recomendação nº1 em uma frase. Não escreva roteiro aqui.
