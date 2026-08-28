#!/bin/sh
set -eu

sample_dir=${1:?prepared sample directory is required}
pidfile="$(dirname "$sample_dir")/evaluation.pid"
if [ ! -f "$pidfile" ]; then
	printf '%s\n' 'AG-PT evaluation is not running'
	exit 0
fi

pid=$(cat "$pidfile" 2>/dev/null || true)
if [ -z "$pid" ] || ! kill -0 "$pid" 2>/dev/null; then
	printf 'AG-PT evaluation already stopped: pid=%s\n' "${pid:---}"
	exit 0
fi
command=$(ps -o command= -p "$pid")
case "$command" in
*"$sample_dir/manifest.tsv"*)
	kill "$pid"
	printf 'AG-PT stale evaluation stopped: pid=%s\n' "$pid"
	;;
*)
	printf 'refusing to stop unexpected process for pid=%s\n' "$pid" >&2
	exit 1
	;;
esac
