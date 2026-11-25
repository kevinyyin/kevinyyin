#!/bin/sh
# One-off, run locally (needs ffmpeg): turn the artwork video into the sprite
# sheet the banner animates. The video is 5x-upscaled pixel art with a 4px
# offset, so crop to whole art pixels, shrink 5x by averaging, reduce to a
# small palette, and tile the frames into a COLSxROWS grid.
#   scripts/make_art_strip.sh <video> <out.png> [cols] [rows] [colors]
set -eu
VIDEO="$1"; OUT="$2"; COLS="${3:-12}"; ROWS="${4:-10}"; COLORS="${5:-64}"
ffmpeg -v error -y -i "$VIDEO" -filter_complex \
  "[0:v]crop=1570:1035:4:4,scale=314:207:flags=area,tile=${COLS}x${ROWS}[t];[t]split[a][b];[a]palettegen=max_colors=${COLORS}:stats_mode=single[p];[b][p]paletteuse=dither=none" \
  -frames:v 1 "$OUT"
