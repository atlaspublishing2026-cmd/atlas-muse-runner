#!/usr/bin/env bash
set -euo pipefail

FILE="${1:?usage: video_preflight.sh <video.mp4>}"

codec=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=nw=1:nk=1 "$FILE")
pix=$(ffprobe -v error -select_streams v:0 -show_entries stream=pix_fmt -of default=nw=1:nk=1 "$FILE")
fps=$(ffprobe -v error -select_streams v:0 -show_entries stream=avg_frame_rate -of default=nw=1:nk=1 "$FILE")
width=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of default=nw=1:nk=1 "$FILE")
height=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of default=nw=1:nk=1 "$FILE")
duration=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$FILE")

printf 'codec=%s pix_fmt=%s fps=%s size=%sx%s duration=%s\n' "$codec" "$pix" "$fps" "$width" "$height" "$duration"

[[ "$codec" == "h264" ]]
[[ "$pix" == "yuv420p" ]]
[[ "$fps" == "30/1" ]]
[[ "$width" == "1080" ]]
[[ "$height" == "1920" ]]
awk -v d="$duration" 'BEGIN { exit !(d > 0) }'

echo "ATLAS_PREFLIGHT=PASS"
