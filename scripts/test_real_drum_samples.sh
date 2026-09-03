#!/bin/sh
set -eu

binary="build/analyzer_real_drum_samples"

if [ ! -x "$binary" ]; then
	echo "missing $binary; build/analyzer_real_drum_samples must be a prerequisite" >&2
	exit 1
fi

MUSIC_ANALYZER_REAL_DRUM_SOURCE="Speaker Monitor" \
	MUSIC_ANALYZER_REAL_DRUM_MIN_KICK=90 \
	MUSIC_ANALYZER_REAL_DRUM_MIN_SNARE=70 \
	MUSIC_ANALYZER_REAL_DRUM_MIN_HIHAT=65 \
	"$binary"

MUSIC_ANALYZER_REAL_DRUM_SOURCE="IDMT Drum One Shot" \
	MUSIC_ANALYZER_REAL_DRUM_MIN_KICK=95 \
	MUSIC_ANALYZER_REAL_DRUM_MIN_SNARE=60 \
	MUSIC_ANALYZER_REAL_DRUM_MIN_HIHAT=85 \
	"$binary"
