#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || -z $1 ]]; then
	echo "usage: $0 SAMPLE_ID" >&2
	exit 2
fi

attributes=build/gaps_guitar_full_attributes.tsv
head -n 1 "$attributes"
rg --fixed-strings "$1" "$attributes"
