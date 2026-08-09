#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || -z $1 ]]; then
	echo "usage: $0 SAMPLE_ID" >&2
	exit 2
fi

awk -F '\t' -v sample_id="$1" '$1 == "AUDIO" && $2 == sample_id' \
	build/gaps_guitar_samples_full/manifest.tsv
