#!/bin/sh
# Capture the full real-URMP miss stream for offline trait mining.
set -eu

analyzer=${1:?missing analyzer path}
root=${2:?missing URMP root}
output=${3:?missing output path}

mkdir -p "$(dirname "$output")"
temporary_output="${output}.tmp.$$"
trap 'rm -f "$temporary_output"' EXIT HUP INT TERM
set +e
MUSIC_ANALYZER_URMP_ROOT="$root" MUSIC_ANALYZER_URMP_REQUIRED=1 "$analyzer" >"$temporary_output" 2>&1
status=$?
set -e
mv "$temporary_output" "$output"
trap - EXIT HUP INT TERM
echo "capture_urmp_measurement: analyzer exit=$status output=$output"
exit 0
