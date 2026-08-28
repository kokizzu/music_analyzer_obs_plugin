#!/bin/sh
set -eu

make_command=${1:?make command is required}
sample_dir=${2:?prepared sample directory is required}
minimum_samples=${3:?minimum samples is required}
state_dir=$(dirname "$sample_dir")
pidfile="$state_dir/evaluation.pid"
logfile="$state_dir/evaluation.log"
manifest="$sample_dir/manifest.tsv"

if [ -f "$pidfile" ]; then
	pid=$(cat "$pidfile" 2>/dev/null || true)
	if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
		printf 'AG-PT evaluation already running: pid=%s log=%s\n' "$pid" "$logfile"
		exit 0
	fi
	rm -f "$pidfile"
fi

mkdir -p "$state_dir"
setsid nohup sh -c '
	while :; do
		if [ -f "$1" ]; then
			prepared=$(awk "END { print (NR > 0 ? NR - 1 : 0) }" "$1")
			if [ "$prepared" -ge "$2" ]; then
				break
			fi
		fi
		sleep 5
	done
	exec "$3" \
		REAL_NOTE_SAMPLE_SHARDS=32 \
		REAL_NOTE_SAMPLE_TAG=agpt_guitar \
		REAL_NOTE_SAMPLE_ROOT="$4" \
		REAL_NOTE_SAMPLE_REQUIRED_SAMPLES="$2" \
		REAL_NOTE_SAMPLE_MIN_BASS=0 \
		REAL_NOTE_SAMPLE_MIN_GUITAR="$2" \
		REAL_NOTE_SAMPLE_MIN_PIANO=0 \
		REAL_NOTE_SAMPLE_MIN_VOCALS=0 \
		REAL_NOTE_SAMPLE_MIN_OTHER=0 \
		REAL_NOTE_SAMPLE_MIN_BASS_HIT_PERCENT=0 \
		REAL_NOTE_SAMPLE_MIN_GUITAR_HIT_PERCENT=0 \
		REAL_NOTE_SAMPLE_MIN_PIANO_HIT_PERCENT=0 \
		REAL_NOTE_SAMPLE_MIN_VOCALS_HIT_PERCENT=0 \
		REAL_NOTE_SAMPLE_MIN_OTHER_HIT_PERCENT=0 \
		REAL_NOTE_SAMPLE_MAX_FAILURES=999999 \
		REAL_NOTE_SAMPLE_MAX_FAILURE_LINES=80 \
		REAL_NOTE_SAMPLE_SHARD_MAX_FAILURES=999999 \
		test-real-note-sample-shards
' sh "$manifest" "$minimum_samples" "$make_command" "$sample_dir" >"$logfile" 2>&1 < /dev/null &
pid=$!
printf '%s\n' "$pid" >"$pidfile"
printf 'AG-PT evaluation queued: pid=%s log=%s\n' "$pid" "$logfile"
