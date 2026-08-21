#!/usr/bin/env bash
# Print the authoritative FretSpark SDK metadata, README, and tracked paths.
# Keeping this behind a Make target makes the external protocol audit repeatable.
set -euo pipefail

repo=${1:-FretSpark/fretspark_sdk}
api="https://api.github.com/repos/${repo}"

if [[ $# -gt 1 ]]; then
  shift
  for path in "$@"; do
    printf '%s\n' "--- $path ---"
    curl -fsSL -H 'Accept: application/vnd.github.raw+json' "$api/contents/$path"
  done
  exit 0
fi

curl -fsSL "$api" | jq -r '.full_name, .default_branch, .description, .license.spdx_id'
printf '\n--- README ---\n'
curl -fsSL -H 'Accept: application/vnd.github.raw+json' "$api/readme"
printf '\n--- TRACKED PATHS ---\n'
curl -fsSL "$api/git/trees/HEAD?recursive=1" | jq -r '.tree[] | select(.type == "blob") | .path'

for path in \
  assets/brands_fallback.json \
  lib/src/transport/flutter_blue_transport.dart \
  lib/src/core/commands.dart \
  lib/src/core/packet_codec.dart \
  lib/src/core/batch_transfer.dart \
  lib/src/api/fret_led.dart \
  lib/src/models/fret_note.dart; do
  printf '\n--- %s ---\n' "$path"
  curl -fsSL -H 'Accept: application/vnd.github.raw+json' "$api/contents/$path"
done
