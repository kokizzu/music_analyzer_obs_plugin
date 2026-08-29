#!/bin/sh
set -eu

output=build/real_note_vocal_audit.out
env \
  MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 \
  MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 \
  MUSIC_ANALYZER_REAL_NOTE_FAMILY_FILTER=vocals \
  MUSIC_ANALYZER_REAL_NOTE_VERBOSE_MISSES=1 \
  build/analyzer_real_note_samples >"$output" 2>&1
printf '%s\n' "$output"
