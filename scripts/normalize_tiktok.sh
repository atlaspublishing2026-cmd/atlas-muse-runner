#!/usr/bin/env bash
set -euo pipefail

IN="${1:?usage: normalize_tiktok.sh <input> <output>}"
OUT="${2:?usage: normalize_tiktok.sh <input> <output>}"

ffmpeg -y -i "$IN" \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart "$OUT"

bash scripts/video_preflight.sh "$OUT"
