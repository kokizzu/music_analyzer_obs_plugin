#!/bin/sh
# Wait for the resumable Candombe transfer, then run its offline BPM harness.
# No audio is played and no OBS files are touched.
set -eu

if [ "$#" -ne 2 ]; then
    echo "usage: $0 MAKE_COMMAND BUILD_DIR" >&2
    exit 64
fi

make_command=$1
build_dir=$2
job_dir="$build_dir/corpus-download-jobs"
pid_file="$job_dir/download-candombe.pid"
log_file="$job_dir/download-candombe.log"

if [ ! -s "$pid_file" ]; then
    echo "measure_candombe_after_download: missing active Candombe downloader" >&2
    exit 1
fi
pid=$(cat "$pid_file")
while kill -0 "$pid" 2>/dev/null; do
    sleep 30
done
if ! tail -n 1 "$log_file" 2>/dev/null | grep -q '^candombe data ready:'; then
    echo "measure_candombe_after_download: Candombe download did not finish successfully" >&2
    exit 1
fi

"$make_command" -s measure-candombe-bpm
"$make_command" -s update-detection-accuracy-report-cached
printf '%s\n' 'measure_candombe_after_download: measurement and report refresh complete'
