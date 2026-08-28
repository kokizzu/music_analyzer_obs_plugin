#!/bin/sh
set -eu

report=build/agpt_guitar_visual_pattern_report.txt
test -s "$report"
printf 'report_lines=%s\n' "$(wc -l < "$report" | tr -d '[:space:]')"
sed -n '1,180p' "$report"
