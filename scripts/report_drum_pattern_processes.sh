#!/usr/bin/env sh
set -eu

if pgrep -af "analyzer_drum_samples"; then
    exit 0
fi
printf '%s\n' "drum_pattern_analysis: no running process"
