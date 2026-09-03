#!/bin/sh
set -eu

binary="build/analyzer_real_drum_samples"

if [ ! -x "$binary" ]; then
	echo "missing $binary; build analyzer_real_drum_samples first" >&2
	exit 1
fi

MUSIC_ANALYZER_REAL_DRUM_SOURCE="IDMT Drum One Shot" \
MUSIC_ANALYZER_REAL_DRUM_MIN_KICK=95 \
MUSIC_ANALYZER_REAL_DRUM_MIN_SNARE=85 \
MUSIC_ANALYZER_REAL_DRUM_MIN_HIHAT=90 \
"$binary"
