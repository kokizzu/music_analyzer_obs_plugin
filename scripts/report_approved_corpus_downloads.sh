#!/bin/sh
# Report Make-managed background corpus downloads without launching anything.
set -eu

if [ "$#" -lt 2 ]; then
    echo "usage: $0 BUILD_DIR TARGET..." >&2
    exit 64
fi

build_dir=$1
shift
for target in "$@"; do
    safe_target=$(printf '%s' "$target" | tr '/:' '__')
    pid_file="$build_dir/corpus-download-jobs/$safe_target.pid"
    log_file="$build_dir/corpus-download-jobs/$safe_target.log"
    if [ ! -s "$pid_file" ]; then
        printf 'NOT_STARTED target=%s log=%s\n' "$target" "$log_file"
        continue
    fi
    pid=$(cat "$pid_file")
    if kill -0 "$pid" 2>/dev/null; then
        printf 'RUNNING target=%s pid=%s log=%s\n' "$target" "$pid" "$log_file"
    else
        last_line=$(tail -n 1 "$log_file" 2>/dev/null || true)
        printf 'FINISHED target=%s pid=%s log=%s last=%s\n' "$target" "$pid" "$log_file" "$last_line"
    fi
done
