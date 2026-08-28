#!/bin/sh
# Start the long AG-PT extraction independently of the interactive command timeout.
set -eu

if [ "$#" -ne 3 ]; then
	echo "usage: $0 EXTRACT_SCRIPT ARCHIVE DESTINATION" >&2
	exit 2
fi

extract_script=$1
archive=$2
destination=$3
state_dir=$(dirname "$archive")
pid_file="$state_dir/extract.pid"
log_file="$state_dir/extract.log"

if [ -f "$pid_file" ]; then
	pid=$(cat "$pid_file")
	if kill -0 "$pid" 2>/dev/null; then
		printf 'AG-PT extraction already running: pid=%s log=%s\n' "$pid" "$log_file"
		exit 0
	fi
	rm -f "$pid_file"
fi

mkdir -p "$destination"
nohup /bin/sh "$extract_script" "$archive" "$destination" >"$log_file" 2>&1 < /dev/null &
pid=$!
printf '%s\n' "$pid" > "$pid_file"
printf 'AG-PT extraction started: pid=%s log=%s\n' "$pid" "$log_file"
