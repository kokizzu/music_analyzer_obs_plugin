#!/bin/sh
# Atomically combine matching tab-separated-value shard files.
set -eu

if [ "$#" -lt 2 ]; then
	printf '%s\n' "usage: merge_tsv_parts.sh TARGET PART [PART...]" >&2
	exit 2
fi

target=$1
shift
tmp="${target}.$$.tmp"

cleanup() {
	rm -f "$tmp"
}
trap cleanup EXIT INT TERM

awk 'FNR == 1 && NR != 1 { next } { print }' "$@" > "$tmp"
mv "$tmp" "$target"
