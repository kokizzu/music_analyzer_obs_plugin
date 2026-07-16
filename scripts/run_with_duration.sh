#!/bin/sh
set -u

if [ "$#" -lt 2 ]; then
	printf '%s\n' "usage: run_with_duration.sh LABEL COMMAND [ARG...]" >&2
	exit 2
fi

label=$1
shift

start_ns=$(date +%s%N 2>/dev/null || date +%s000000000)
"$@"
status=$?
end_ns=$(date +%s%N 2>/dev/null || date +%s000000000)

elapsed=$(
	awk "BEGIN {
		delta = ($end_ns - $start_ns) / 1000000000;
		if (delta < 0) delta = 0;
		printf \"%.2f\", delta;
	}"
)

if [ "$status" -eq 0 ]; then
	printf '%s: duration %ss\n' "$label" "$elapsed"
else
	printf '%s: duration %ss (exit %d)\n' "$label" "$elapsed" "$status" >&2
fi
exit "$status"
