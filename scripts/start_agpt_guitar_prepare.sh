#!/bin/sh
set -eu

prepare_script=${1:?prepare script is required}
source_dir=${2:?source directory is required}
output_dir=${3:?output directory is required}
sample_limit=${4:?sample limit is required}
minimum_samples=${5:?minimum samples is required}
ffmpeg_bin=${6:?ffmpeg path is required}

state_dir=$(dirname "$output_dir")
pidfile="$state_dir/prepare.pid"
logfile="$state_dir/prepare.log"
manifest="$output_dir/manifest.tsv"

if [ -f "$manifest" ]; then
	prepared=$(awk 'END { print (NR > 0 ? NR - 1 : 0) }' "$manifest")
	if [ "$prepared" -ge "$minimum_samples" ]; then
		printf 'AG-PT preparation already complete: samples=%s manifest=%s\n' "$prepared" "$manifest"
		exit 0
	fi
fi

if [ -f "$pidfile" ]; then
	pid=$(cat "$pidfile" 2>/dev/null || true)
	if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
		printf 'AG-PT preparation already running: pid=%s log=%s\n' "$pid" "$logfile"
		exit 0
	fi
	rm -f "$pidfile"
fi

mkdir -p "$state_dir"
setsid nohup python3 "$prepare_script" \
	--source "$source_dir" \
	--output "$output_dir" \
	--limit "$sample_limit" \
	--min-samples "$minimum_samples" \
	--ffmpeg "$ffmpeg_bin" >"$logfile" 2>&1 &
pid=$!
printf '%s\n' "$pid" >"$pidfile"
printf 'AG-PT preparation started: pid=%s log=%s\n' "$pid" "$logfile"
