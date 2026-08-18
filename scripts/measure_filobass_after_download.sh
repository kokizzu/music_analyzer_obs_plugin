#!/bin/sh
# Queue the FiloBass measurement behind the existing detached downloader.
# This intentionally waits for the known job rather than starting a second
# curl against the resumable archive.  It never plays audio.
set -eu

if [ "$#" -ne 2 ]; then
    echo "usage: $0 MAKE_COMMAND BUILD_DIR" >&2
    exit 64
fi

make_command=$1
build_dir=$2
job_dir="$build_dir/corpus-download-jobs"
pid_file="$job_dir/download-filobass.pid"
log_file="$job_dir/download-filobass.log"

if [ ! -s "$pid_file" ]; then
    echo "measure_filobass_after_download: missing active FiloBass downloader" >&2
    exit 1
fi
pid=$(cat "$pid_file")
while kill -0 "$pid" 2>/dev/null; do
    sleep 30
done
if ! tail -n 1 "$log_file" 2>/dev/null | grep -q '^filobass data ready:'; then
    echo "measure_filobass_after_download: FiloBass download did not finish successfully" >&2
    exit 1
fi

"$make_command" -s measure-filobass-bpm
"$make_command" -s update-detection-accuracy-report-cached
printf '%s\n' 'measure_filobass_after_download: measurement and report refresh complete'
