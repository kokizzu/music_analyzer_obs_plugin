#!/bin/sh
# Launch or report a long SCMS evidence-expansion measurement through Make.
set -eu

status=0
pid_file=
log_file=
workdir=
limit=
minimum_samples=
target=measure-scms-vocal-mix
while [ "$#" -gt 0 ]; do
    case "$1" in
        --status) status=1 ;;
        --pid-file) pid_file=$2; shift ;;
        --log-file) log_file=$2; shift ;;
        --workdir) workdir=$2; shift ;;
        --limit) limit=$2; shift ;;
        --minimum-samples) minimum_samples=$2; shift ;;
        --target) target=$2; shift ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
    shift
done

[ -n "$pid_file" ] && [ -n "$log_file" ] || { echo "pid and log paths are required" >&2; exit 2; }

if [ -s "$pid_file" ]; then
    pid=$(cat "$pid_file")
    if kill -0 "$pid" 2>/dev/null; then
        echo "scms_vocal_measurement: running pid=$pid log=$log_file"
        exit 0
    fi
fi
rm -f "$pid_file"
if [ "$status" -eq 1 ]; then
    echo "scms_vocal_measurement: not running log=$log_file"
    exit 0
fi

[ -n "$workdir" ] && [ -n "$limit" ] && [ -n "$minimum_samples" ] || {
    echo "workdir, limit, and minimum-samples are required to start measurement" >&2
    exit 2
}
[ "$target" = measure-scms-vocal-mix ] || [ "$target" = measure-scms-vocal-mix-refresh ] || {
    echo "target must be measure-scms-vocal-mix or measure-scms-vocal-mix-refresh" >&2
    exit 2
}
mkdir -p "$(dirname "$pid_file")" "$(dirname "$log_file")"
nohup setsid make -C "$workdir" SCMS_DATASET_SAMPLE_LIMIT="$limit" \
    SCMS_DATASET_MIN_SAMPLES="$minimum_samples" "$target" \
    >> "$log_file" 2>&1 < /dev/null &
echo "$!" > "$pid_file"
echo "scms_vocal_measurement: started pid=$(cat "$pid_file") target=$target limit=$limit minimum_samples=$minimum_samples log=$log_file"
