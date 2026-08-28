#!/bin/sh
set -eu

printf '%s\n' '== concrete real-note attribute targets =='
rg -n -C 4 '^analyze-real-note-attributes:|^test-real-note-samples-full-mix:|^test-real-note-sample.*attribute|^evaluate-real-note-display-shadow:' Makefile
printf '%s\n' '== reusable full-mix runner variables =='
sed -n '1888,2020p' Makefile
printf '%s\n' '== analyzer attribute environment =='
rg -n -C 3 'MUSIC_ANALYZER_REAL_NOTE.*(ATTRIBUTE|FULL_MIX|MANIFEST|ROOT)' Makefile tests/analyzer_real_note_samples.cpp
printf '%s\n' '== fail-fast expected-note path =='
rg -n -C 14 'expected detected note' tests/analyzer_real_note_samples.cpp
printf '%s\n' '== runner failure policy =='
rg -n -C 8 'class Runner|struct Runner|void expect\(|max_failures|MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES' tests/analyzer_real_note_samples.cpp
printf '%s\n' '== duration wrapper =='
sed -n '1,180p' scripts/run_with_duration.sh
