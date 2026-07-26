#!/bin/sh
set -eu

if [ "$#" -lt 4 ]; then
	printf '%s\n' "usage: build_sharded_tsv.sh TARGET MAKE MAKE_JOBS PART [PART...]" >&2
	exit 2
fi

target=$1
make_cmd=$2
make_jobs=$3
shift 3

lock="${target}.lock"
tmp="${target}.$$.tmp"

while ! mkdir "$lock" 2>/dev/null; do
	sleep 0.1
done

cleanup() {
	rm -f "$tmp"
	rmdir "$lock" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

if [ -n "$make_jobs" ]; then
	"$make_cmd" $make_jobs "$@"
else
	"$make_cmd" "$@"
fi

awk 'FNR == 1 && NR != 1 { next } { print }' "$@" > "$tmp"
mv "$tmp" "$target"
