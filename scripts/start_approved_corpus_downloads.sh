#!/bin/sh
# Start explicitly approved external corpus downloads independently of the
# interactive session.  Archive paths, resume handling, and validation remain
# in their Makefile targets.
set -eu

if [ "$#" -lt 3 ]; then
    echo "usage: $0 MAKE_COMMAND BUILD_DIR TARGET..." >&2
    exit 64
fi

make_command=$1
build_dir=$2
shift 2
mkdir -p "$build_dir/corpus-download-jobs"

for target in "$@"; do
    safe_target=$(printf '%s' "$target" | tr '/:' '__')
    pid_file="$build_dir/corpus-download-jobs/$safe_target.pid"
    log_file="$build_dir/corpus-download-jobs/$safe_target.log"
    if [ -s "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            printf 'RUNNING target=%s pid=%s log=%s\n' "$target" "$pid" "$log_file"
            continue
        fi
        rm -f "$pid_file"
    fi
    # A separate session prevents an interactive runner from reaping the
    # acquisition with the invoking shell's process group.
    setsid nohup "$make_command" "$target" >"$log_file" 2>&1 < /dev/null &
    pid=$!
    printf '%s\n' "$pid" >"$pid_file"
    printf 'STARTED target=%s pid=%s log=%s\n' "$target" "$pid" "$log_file"
done
