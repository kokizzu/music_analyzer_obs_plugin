#!/usr/bin/env bash
# Download GTZAN audio plus GTZAN-Rhythm beat/downbeat annotations into the
# external sample store. This is offline benchmark evidence only: no audio is
# played and the OBS installation is never touched.
set -euo pipefail

if [ "$#" -ne 4 ]; then
  printf '%s\n' "usage: $0 STORE_ROOT CURL AUDIO_URL ANNOTATIONS_URL" >&2
  exit 64
fi

store_root=$1
curl_bin=$2
audio_url=$3
annotations_url=$4

target="$store_root/gtzan_rhythm"
audio_archive="$target/gtzan-dataset-music-genre-classification.zip"
annotations_archive="$target/GTZAN-Rhythm_v2_ismir2015_lbd_2015-10-28.tar_.gz"
audio_root="$target/audio"
annotations_root="$target/annotations"
mkdir -p "$target"

download_resume() {
  local url=$1
  local path=$2
  "$curl_bin" -fL --retry 8 --retry-all-errors --continue-at - -o "$path" "$url"
}

if [ ! -s "$audio_archive" ]; then
  download_resume "$audio_url" "$audio_archive"
fi
python3 -m zipfile -t "$audio_archive" >/dev/null
if [ ! -d "$audio_root" ]; then
  mkdir -p "$audio_root"
  python3 -m zipfile -e "$audio_archive" "$audio_root" >/dev/null
fi

if [ ! -s "$annotations_archive" ]; then
  download_resume "$annotations_url" "$annotations_archive"
fi
tar -tzf "$annotations_archive" >/dev/null
if [ ! -d "$annotations_root" ]; then
  mkdir -p "$annotations_root"
  tar -xzf "$annotations_archive" -C "$annotations_root"
fi

printf 'gtzan rhythm data ready: %s\n' "$target"
