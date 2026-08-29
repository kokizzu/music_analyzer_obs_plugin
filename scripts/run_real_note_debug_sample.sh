#!/bin/sh
set -eu

sample_id=$1
exec env \
  MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 \
  MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 \
  MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT=build/real_note_samples \
  MUSIC_ANALYZER_REAL_NOTE_DEBUG_SAMPLE_ID="$sample_id" \
  build/analyzer_real_note_samples
