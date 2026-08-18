#!/bin/sh
# Stop only the detached corpus-job sessions started by the paired launcher.
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
    status_file="$build_dir/corpus-download-jobs/$safe_target.status"
    if [ ! -s "$pid_file" ]; then
        printf 'NOT_RUNNING target=%s\n' "$target"
        continue
    fi
    pid=$(cat "$pid_file")
    if kill -0 "$pid" 2>/dev/null; then
        # POSIX sh implementations such as dash do not accept `kill --`.
        # Target the detached session's process group directly so descendants
        # (curl/aria2 and the wrapper shell) cannot outlive their Make parent.
        kill -TERM "-$pid" 2>/dev/null || kill -TERM "$pid"
        printf '%s\n' "stopped" >"$status_file"
        printf 'STOPPED target=%s pid=%s\n' "$target" "$pid"
    else
        printf 'NOT_RUNNING target=%s pid=%s\n' "$target" "$pid"
    fi
    rm -f "$pid_file"
done
