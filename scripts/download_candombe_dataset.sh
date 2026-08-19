#!/usr/bin/env bash
# Download the public Candombe beat/downbeat corpus into InstrumentSamples.
# This is benchmark evidence only: it never opens an audio device or changes OBS.
set -euo pipefail

if [ "$#" -lt 4 ] || [ "$#" -gt 5 ]; then
  printf '%s\n' "usage: $0 STORE_ROOT CURL AUDIO_URL ANNOTATIONS_URL [annotations-only]" >&2
  exit 64
fi

store_root=$1
curl_bin=$2
audio_url=$3
annotations_url=$4
mode=${5:-all}
if [ "$mode" != all ] && [ "$mode" != annotations-only ]; then
  printf '%s\n' "unknown Candombe download mode: $mode" >&2
  exit 64
fi
target="$store_root/candombe"
audio_archive="$target/candombe_audio.zip"
annotations_archive="$target/candombe_annotations.zip"
audio_root="$target/audio"
annotations_root="$target/annotations"
audio_marker="$target/.candombe-audio-extraction-complete"
annotations_marker="$target/.candombe-annotations-extraction-complete"
mkdir -p "$target"

download_resume() {
  local url=$1 path=$2
  "$curl_bin" -fL --retry 8 --retry-all-errors --continue-at - -o "$path" "$url"
}

valid_zip() { [ -s "$1" ] && python3 "$(dirname "$0")/validate_zip_archive.py" "$1" >/dev/null 2>&1; }

download_fresh_if_invalid() {
  local url=$1 archive=$2
  if ! valid_zip "$archive"; then
    # The archive is a known incomplete/corrupt transfer. Remove only this
    # exact regenerated corpus archive before fetching a fresh copy.
    rm -f "$archive"
    download_resume "$url" "$archive"
  fi
  valid_zip "$archive"
}

extract_once() {
  local archive=$1 destination=$2 marker=$3
  [ -f "$marker" ] && return
  # A prior interrupted extraction never counts as a corpus. Clear only its
  # exact destination, extract into a sibling staging directory, then publish
  # it atomically with a completion marker.
  rm -rf "$destination" "$destination.partial"
  mkdir -p "$destination.partial"
  python3 -m zipfile -e "$archive" "$destination.partial" >/dev/null
  mv "$destination.partial" "$destination"
  : > "$marker"
}

# An interrupted resumable transfer is nonempty but not yet a valid ZIP. Keep
# resuming it instead of treating its size as evidence of completion.
if [ "$mode" = all ]; then
  download_fresh_if_invalid "$audio_url" "$audio_archive"
  extract_once "$audio_archive" "$audio_root" "$audio_marker"
fi

download_fresh_if_invalid "$annotations_url" "$annotations_archive"
extract_once "$annotations_archive" "$annotations_root" "$annotations_marker"

printf 'candombe data ready: %s\n' "$target"
