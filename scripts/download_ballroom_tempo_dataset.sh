#!/usr/bin/env bash
# Download the public Ballroom audio and its separately versioned beat labels.
# All sizeable files remain in InstrumentSamples; build/ only receives links
# and regenerated diagnostic reports.
set -euo pipefail

store_root=$1
curl_bin=$2
archive_url=${3:-https://mtg.upf.edu/ismir2004/contest/tempoContest/data1.tar.gz}
annotations_url=${4:-https://github.com/CPJKU/BallroomAnnotations.git}
expected_md5=${5:-2872a3e52070bc342a4510a95e2fa0b8}
aria2c_bin=${6:-}
connections=${7:-8}

target="$store_root/ballroom_tempo"
archive="$target/data1.tar.gz"
audio_root="$target/audio"
annotations_root="$target/annotations"
mkdir -p "$target"

actual_md5=""
if [ -s "$archive" ]; then
  actual_md5=$(md5sum "$archive" | awk '{print $1}')
fi
if [ "$actual_md5" != "$expected_md5" ]; then
  # Preserve the same partial path so either downloader can resume it. aria2
  # uses segmented range requests when available; a failed or unavailable
  # aria2 falls back to curl's single-connection resume without discarding
  # data. The checksum below remains the only promotion gate.
  if [ -n "$aria2c_bin" ] && command -v "$aria2c_bin" >/dev/null 2>&1; then
    if ! "$aria2c_bin" --continue=true --allow-overwrite=true --auto-file-renaming=false \
      --max-tries=5 --retry-wait=5 --max-connection-per-server="$connections" \
      --split="$connections" --min-split-size=8M --file-allocation=none \
      --dir "$target" --out "data1.tar.gz" "$archive_url"; then
      "$curl_bin" -fL --retry 4 --continue-at - -o "$archive" "$archive_url"
    fi
  else
    "$curl_bin" -fL --retry 4 --continue-at - -o "$archive" "$archive_url"
  fi
fi
actual_md5=$(md5sum "$archive" | awk '{print $1}')
if [ "$actual_md5" != "$expected_md5" ]; then
  echo "Ballroom archive checksum mismatch: expected $expected_md5, got $actual_md5" >&2
  exit 1
fi
if [ ! -d "$audio_root" ]; then
  mkdir -p "$audio_root"
  tar -xzf "$archive" -C "$audio_root"
fi
if [ ! -d "$annotations_root/.git" ]; then
  git clone --depth 1 "$annotations_url" "$annotations_root"
fi
printf 'ballroom tempo data ready: %s\n' "$target"
