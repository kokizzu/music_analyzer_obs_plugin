#!/usr/bin/env bash
# Fetch Ballroom's small versioned beat/bar annotations independently of its
# large audio archive so both public inputs can progress in parallel.
set -euo pipefail

store_root=$1
annotations_url=${2:-https://github.com/CPJKU/BallroomAnnotations.git}
target="$store_root/ballroom_tempo/annotations"

if [ ! -d "$target/.git" ]; then
  mkdir -p "$(dirname "$target")"
  git clone --depth 1 "$annotations_url" "$target"
fi
printf 'ballroom annotations ready: %s\n' "$target"
