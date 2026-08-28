#!/bin/sh
set -eu

attributes=${1:?AG-PT attributes are required}
protected=${2:?protected attributes are required}
report=${3:?report output is required}
state_dir=$(dirname "$attributes")
pidfile="$state_dir/visual_mining.pid"
logfile="$state_dir/visual_mining.log"

if [ -f "$pidfile" ]; then
	pid=$(cat "$pidfile" 2>/dev/null || true)
	if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
		printf 'AG-PT visual miner already running: pid=%s log=%s\n' "$pid" "$logfile"
		exit 0
	fi
	rm -f "$pidfile"
fi

tmp="$report.$$.tmp"
setsid nohup sh -c '
	set -eu
	python3 scripts/find_real_note_attribute_patterns.py "$1" \
		--top-buckets 8 --bucket-status visual_row_confusion --limit 8 \
		--min-positive-samples 20 --max-negative-samples 0 \
		--max-conditions 3 --beam-width 240 --include-row-context \
		--protected-scope all --extra-protected-path "$2" \
		--show-examples 3 --show-near-misses 8 --profile-fields 8 > "$3"
	mv -f "$3" "$4"
' sh "$attributes" "$protected" "$tmp" "$report" >"$logfile" 2>&1 < /dev/null &
pid=$!
printf '%s\n' "$pid" >"$pidfile"
printf 'AG-PT visual miner started: pid=%s log=%s\n' "$pid" "$logfile"
