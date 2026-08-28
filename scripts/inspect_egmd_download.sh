#!/bin/sh
# Summarize the resumable E-GMD download without accessing sample audio.
set -eu

archive_path=${1:?usage: inspect_egmd_download.sh ARCHIVE LOG PID}
log_path=${2:?usage: inspect_egmd_download.sh ARCHIVE LOG PID}
pid_path=${3:?usage: inspect_egmd_download.sh ARCHIVE LOG PID}

if [ -f "$archive_path" ]; then
    bytes=$(wc -c < "$archive_path" | tr -d ' ')
    printf 'archive_bytes=%s\n' "$bytes"
elif [ -f "$archive_path.part" ]; then
    bytes=$(wc -c < "$archive_path.part" | tr -d ' ')
    allocated_bytes=$(du -B1 "$archive_path.part" | awk '{print $1}')
    printf 'partial_logical_bytes=%s\n' "$bytes"
    printf 'partial_allocated_bytes=%s\n' "$allocated_bytes"
else
    printf '%s\n' 'download_bytes=0'
fi
if [ -s "$pid_path" ]; then
    pid=$(cat "$pid_path" 2>/dev/null || true)
    case "$pid" in
        ''|*[!0-9]*) printf '%s\n' 'download_state=unknown' ;;
        *) if kill -0 "$pid" 2>/dev/null; then printf 'download_state=running pid=%s\n' "$pid"; else printf 'download_state=stopped pid=%s\n' "$pid"; fi ;;
    esac
else
    printf '%s\n' 'download_state=not-started'
fi
if [ -f "$log_path" ]; then
    printf '%s\n' 'log_tail:'
    tail -n 8 "$log_path"
fi
