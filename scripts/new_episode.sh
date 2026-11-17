#!/usr/bin/env bash
# Cria a pasta de um episódio novo: ./scripts/new_episode.sh gta6-map-size
set -euo pipefail
slug="${1:?uso: new_episode.sh <slug>}"
dir="episodes/$(date +%Y-%m-%d)-$slug"
mkdir -p "$dir"/{sources,media,audio,out}
cat > "$dir/scenes.json" <<'JSON'
{
  "title": "",
  "voice": "en-US-AndrewNeural",
  "rate": "+4%",
  "music": "assets/music/bg.mp3",
  "music_volume": 0.18,
  "scenes": [
    {"text": "Hook line goes here.", "media": ["media/01.jpg"], "lower_third": "Source: Rockstar Games"}
  ]
}
JSON
echo "$dir"
