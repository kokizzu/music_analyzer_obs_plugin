#!/bin/sh
set -eu

if [ "$#" -lt 2 ]; then
    printf '%s\n' "run_with_lock: usage: run_with_lock.sh LOCK_DIR [--] COMMAND [ARG...]" >&2
    exit 2
fi

lock_dir=$1
shift
if [ "${1:-}" = "--" ]; then
    shift
fi
if [ "$#" -eq 0 ]; then
    printf '%s\n' "run_with_lock: missing command" >&2
    exit 2
fi

timeout_seconds=${MUSIC_ANALYZER_LOCK_TIMEOUT_SECONDS:-3600}
sleep_seconds=${MUSIC_ANALYZER_LOCK_SLEEP_SECONDS:-1}
started_at=$(date +%s)
parent_dir=$(dirname "$lock_dir")
mkdir -p "$parent_dir"

while ! mkdir "$lock_dir" 2>/dev/null; do
    if [ -f "$lock_dir/pid" ]; then
        lock_pid=$(cat "$lock_dir/pid" 2>/dev/null || true)
        case "$lock_pid" in
            ''|*[!0-9]*)
                ;;
            *)
                if ! kill -0 "$lock_pid" 2>/dev/null; then
                    rm -f "$lock_dir/pid"
                    rmdir "$lock_dir" 2>/dev/null || true
                    continue
                fi
                ;;
        esac
    fi

    now=$(date +%s)
    if [ $((now - started_at)) -ge "$timeout_seconds" ]; then
        printf '%s\n' "run_with_lock: timed out waiting for $lock_dir" >&2
        exit 124
    fi
    sleep "$sleep_seconds"
done

cleanup() {
    status=$?
    rm -f "$lock_dir/pid"
    rmdir "$lock_dir" 2>/dev/null || true
    exit "$status"
}
trap cleanup EXIT INT TERM HUP

printf '%s\n' "$$" > "$lock_dir/pid"
"$@"
