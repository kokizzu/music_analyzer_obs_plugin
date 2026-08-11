#!/bin/sh
# Capture a bounded offline URMP miss sample with candidate traits enabled.
set -eu

analyzer=${1:?missing analyzer path}
root=${2:?missing URMP root}
output=${3:?missing output path}

mkdir -p "$(dirname "$output")"
set +e
MUSIC_ANALYZER_URMP_ROOT="$root" MUSIC_ANALYZER_URMP_REQUIRED=1 \
	MUSIC_ANALYZER_URMP_MAX_WINDOWS_PER_PIECE=3 MUSIC_ANALYZER_URMP_REQUIRED_WINDOWS=60 \
	MUSIC_ANALYZER_URMP_VERBOSE_TRACK_TRAITS=1 "$analyzer" >"$output" 2>&1
status=$?
set -e
echo "capture_urmp_trait_sample: analyzer exit=$status output=$output"
exit 0
