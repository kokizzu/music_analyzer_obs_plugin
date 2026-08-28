#!/bin/sh
# Count unique samples and successful sample rows in an analyzer TSV.
set -eu

file=${1:?usage: count_tsv_samples.sh <attributes.tsv>}
awk -F '\t' '
NR == 1 {
  for (i = 1; i <= NF; ++i) {
    if ($i == "sample_id") sample = i
    if ($i == "status") status = i
  }
  if (!sample || !status) {
    print "missing sample_id or status column" > "/dev/stderr"
    exit 2
  }
  next
}
!seen[$sample]++ { total += 1; if ($status == "hit") hits += 1 }
END {
  if (NR > 1) printf "samples=%d hit_samples=%d\n", total, hits
}
' "$file"
