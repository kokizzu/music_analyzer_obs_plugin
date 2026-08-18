#!/usr/bin/env bash
# Fetch the official FiloBass archive into the external sample store only.
# It contains real jazz bass stems plus aligned MIDI/downbeat information for
# the bass-led tempo validation path; no audio is played by this script.
set -euo pipefail

store_root=$1
curl_bin=$2
archive_url=${3:-https://zenodo.org/records/10069709/files/FiloBass_v1.0.0.zip?download=1}
expected_md5=${4:-ea1f52ffd492bf3654d720529f15bd9b}

target="$store_root/filobass"
archive="$target/FiloBass_v1.0.0.zip"
extract_root="$target/extracted"
mkdir -p "$target"

actual_md5=""
if [ -s "$archive" ]; then
  actual_md5=$(md5sum "$archive" | awk '{print $1}')
fi
if [ "$actual_md5" != "$expected_md5" ]; then
  "$curl_bin" -fL --retry 8 --retry-all-errors --continue-at - -o "$archive" "$archive_url"
fi
actual_md5=$(md5sum "$archive" | awk '{print $1}')
if [ "$actual_md5" != "$expected_md5" ]; then
  echo "FiloBass archive checksum mismatch: expected $expected_md5, got $actual_md5" >&2
  exit 1
fi
python3 -m zipfile -t "$archive" >/dev/null
if [ ! -d "$extract_root" ]; then
  mkdir -p "$extract_root"
  python3 -m zipfile -e "$archive" "$extract_root" >/dev/null
fi
printf 'filobass data ready: %s\n' "$target"
