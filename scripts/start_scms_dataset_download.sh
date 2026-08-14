#!/bin/sh
# Launch or report the resumable SCMS Make download outside a foreground TTY.
set -eu

status=0
pid_file=
log_file=
workdir=
archive_part=
while [ "$#" -gt 0 ]; do
    case "$1" in
        --status) status=1 ;;
        --pid-file) pid_file=$2; shift ;;
        --log-file) log_file=$2; shift ;;
        --workdir) workdir=$2; shift ;;
        --archive-part) archive_part=$2; shift ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
    shift
done

[ -n "$pid_file" ] && [ -n "$log_file" ] || { echo "pid and log paths are required" >&2; exit 2; }

report_archive_part() {
    # aria2 may reserve a sparse logical file. Report allocated bytes as the
    # actual transferred storage, separately from its apparent length.
    if [ -n "$archive_part" ] && [ -f "$archive_part" ]; then
        logical_bytes=$(wc -c < "$archive_part" | tr -d ' ')
        allocated_bytes=$(du -B1 "$archive_part" | awk 'NR == 1 { print $1 }')
        echo "scms_download: archive_part logical_bytes=$logical_bytes allocated_bytes=$allocated_bytes"
    fi
}

if [ -s "$pid_file" ]; then
    pid=$(cat "$pid_file")
    if kill -0 "$pid" 2>/dev/null; then
        echo "scms_download: running pid=$pid log=$log_file"
		report_archive_part
        exit 0
    fi
fi
rm -f "$pid_file"
if [ "$status" -eq 1 ]; then
    echo "scms_download: not running log=$log_file"
	report_archive_part
    exit 0
fi
[ -n "$workdir" ] || { echo "workdir is required to start download" >&2; exit 2; }
mkdir -p "$(dirname "$pid_file")" "$(dirname "$log_file")"
nohup setsid make -C "$workdir" download-scms-dataset >> "$log_file" 2>&1 < /dev/null &
echo "$!" > "$pid_file"
echo "scms_download: started pid=$(cat "$pid_file") log=$log_file"
