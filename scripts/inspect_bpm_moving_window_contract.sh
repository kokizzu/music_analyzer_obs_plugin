#!/bin/sh
set -eu

printf '%s\n' '== source-window estimator =='
sed -n '30157,30340p' src/analyzer.cpp
printf '%s\n' '== final display assignment =='
sed -n '35288,35365p' src/analyzer.cpp
printf '%s\n' '== fallback feature flags =='
rg -n 'kEnable(PermissiveBeatTrackerFallback|PhaseBeatTrackerConsensus|HighTempoBeatTrackerFallback|UseHighTempoPermissiveTracker)' src
printf '%s\n' '== existing BPM regression wiring =='
rg -n -C 2 'test-bpm-regression|bpm_regression|BPM regression' Makefile tests scripts
printf '%s\n' '== makefile structural-test target =='
rg -n -C 2 'test_measure_analyzer_patterns_makefile.py' Makefile
printf '%s\n' '== accuracy-report BPM statements =='
rg -n -C 1 'BPM|moving window|moving-window|three-second|3-second' docs/detection_accuracy_report.md
printf '%s\n' '== BPM makefile test tail =='
tail -n 75 tests/test_measure_analyzer_patterns_makefile.py
printf '%s\n' '== BPM makefile test head =='
head -n 55 tests/test_measure_analyzer_patterns_makefile.py
