#!/bin/sh
set -eu

binary="build/analyzer_real_drum_samples"
source_name="${1:?source name is required}"

if [ ! -x "$binary" ]; then
	echo "missing $binary; build/analyzer_real_drum_samples must be a prerequisite" >&2
	exit 1
fi

MUSIC_ANALYZER_REAL_DRUM_SOURCE="$source_name" "$binary"
