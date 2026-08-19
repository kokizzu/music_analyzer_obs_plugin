#!/usr/bin/env bash
# Download the public Candombe beat/downbeat corpus into InstrumentSamples.
# This is benchmark evidence only: it never opens an audio device or changes OBS.
set -euo pipefail

if [ "$#" -ne 4 ]; then
  printf '%s\n' "usage: $0 STORE_ROOT CURL AUDIO_URL ANNOTATIONS_URL" >&2
  exit 64
fi

store_root=$1
curl_bin=$2
audio_url=$3
annotations_url=$4
target="$store_root/candombe"
audio_archive="$target/candombe_audio.zip"
annotations_archive="$target/candombe_annotations.zip"
audio_root="$target/audio"
annotations_root="$target/annotations"
mkdir -p "$target"

download_resume() {
  local url=$1 path=$2
  "$curl_bin" -fL --retry 8 --retry-all-errors --continue-at - -o "$path" "$url"
}

valid_zip() { [ -s "$1" ] && python3 -m zipfile -t "$1" >/dev/null 2>&1; }

# An interrupted resumable transfer is nonempty but not yet a valid ZIP. Keep
# resuming it instead of treating its size as evidence of completion.
if ! valid_zip "$audio_archive"; then download_resume "$audio_url" "$audio_archive"; fi
valid_zip "$audio_archive"
if [ ! -d "$audio_root" ]; then mkdir -p "$audio_root"; python3 -m zipfile -e "$audio_archive" "$audio_root" >/dev/null; fi

if ! valid_zip "$annotations_archive"; then download_resume "$annotations_url" "$annotations_archive"; fi
valid_zip "$annotations_archive"
if [ ! -d "$annotations_root" ]; then mkdir -p "$annotations_root"; python3 -m zipfile -e "$annotations_archive" "$annotations_root" >/dev/null; fi

printf 'candombe data ready: %s\n' "$target"
