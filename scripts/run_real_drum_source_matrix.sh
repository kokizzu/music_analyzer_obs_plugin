#!/bin/sh
set -eu

binary="build/analyzer_real_drum_samples"

if [ ! -x "$binary" ]; then
	echo "missing $binary; build/analyzer_real_drum_samples must be a prerequisite" >&2
	exit 1
fi

for source in "Speaker Monitor" "IDMT Drum One Shot" "IDMT Real Drum Track" "IDMT Drum Track"; do
	echo "real-drums source-mode=$source"
	MUSIC_ANALYZER_REAL_DRUM_SOURCE="$source" "$binary"
done
