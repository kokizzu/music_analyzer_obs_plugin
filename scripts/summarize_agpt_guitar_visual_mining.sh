#!/bin/sh
set -eu

report=${1:?usage: summarize_agpt_guitar_visual_mining.sh build/report.txt}
[ -f "$report" ] || { printf 'missing report: %s\n' "$report" >&2; exit 2; }

# Keep the durable full report for examples, but print only the action verdict
# from each bucket for a quick cross-corpus deployment decision.
awk '
  /^visual_row_confusion:/ {
    count += 1
    print
    next
  }
  /^  low-false candidate rules:$/ || /^  highest-coverage candidate rules:$/ {
    label = $0
    getline
    sub(/^  /, "", $0)
    print label " " $0
  }
  END { print "agpt_visual_mining: buckets=" count }
' "$report"
