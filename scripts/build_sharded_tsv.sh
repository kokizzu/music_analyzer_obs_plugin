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
owns_lock=0

# A Make recipe may already hold this exact lock through run_with_lock.sh.
# Keep the standalone path synchronized as before, but do not self-deadlock
# when the parent explicitly transfers lock ownership to this invocation.
if [ "${MUSIC_ANALYZER_HELD_LOCK_DIR:-}" != "$lock" ]; then
	while ! mkdir "$lock" 2>/dev/null; do
		sleep 0.1
	done
	owns_lock=1
fi

cleanup() {
	rm -f "$tmp"
	if [ "$owns_lock" -eq 1 ]; then
		rmdir "$lock" 2>/dev/null || true
	fi
}
trap cleanup EXIT INT TERM

rm -f "$@"

if [ -n "$make_jobs" ]; then
	"$make_cmd" $make_jobs "$@"
else
	"$make_cmd" "$@"
fi

awk 'FNR == 1 && NR != 1 { next } { print }' "$@" > "$tmp"
mv "$tmp" "$target"
