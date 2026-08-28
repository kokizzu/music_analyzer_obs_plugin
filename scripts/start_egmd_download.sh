#!/bin/sh
# Start a resumable E-GMD download without tying it to an interactive session.
set -eu

downloader=${1:?usage: start_egmd_download.sh DOWNLOADER ARCHIVE URL MD5 LOG PID}
archive_path=${2:?usage: start_egmd_download.sh DOWNLOADER ARCHIVE URL MD5 LOG PID}
download_url=${3:?usage: start_egmd_download.sh DOWNLOADER ARCHIVE URL MD5 LOG PID}
expected_md5=${4:?usage: start_egmd_download.sh DOWNLOADER ARCHIVE URL MD5 LOG PID}
log_path=${5:?usage: start_egmd_download.sh DOWNLOADER ARCHIVE URL MD5 LOG PID}
pid_path=${6:?usage: start_egmd_download.sh DOWNLOADER ARCHIVE URL MD5 LOG PID}

mkdir -p "$(dirname "$archive_path")" "$(dirname "$log_path")"
if [ -s "$pid_path" ]; then
    old_pid=$(cat "$pid_path" 2>/dev/null || true)
    case "$old_pid" in
        ''|*[!0-9]*) ;;
        *)
            if kill -0 "$old_pid" 2>/dev/null; then
                printf 'egmd_download=running pid=%s log=%s\n' "$old_pid" "$log_path"
                exit 0
            fi
            ;;
    esac
fi
# A separate session prevents the interactive command runner from reaping the
# large transfer as soon as this Make target completes. `setsid` may fork, so
# the new session records its own PID rather than its short-lived parent.
rm -f "$pid_path"
setsid sh -c '
    pid_path=$1
    shift
    printf "%s\\n" "$$" > "$pid_path"
    exec "$@"
' sh "$pid_path" sh "$downloader" "$archive_path" "$download_url" "$expected_md5" > "$log_path" 2>&1 < /dev/null &

attempts=0
while [ ! -s "$pid_path" ] && [ "$attempts" -lt 20 ]; do
    sleep 1
    attempts=$((attempts + 1))
done
if [ ! -s "$pid_path" ]; then
    printf '%s\n' "egmd_download=failed_to_start log=$log_path" >&2
    exit 1
fi
pid=$(cat "$pid_path")
printf 'egmd_download=started pid=%s archive=%s log=%s\n' "$pid" "$archive_path" "$log_path"
