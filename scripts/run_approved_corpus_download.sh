#!/bin/sh
# Run one detached Make target and persist its actual exit status for the
# paired corpus-job reporter. stdout/stderr remain owned by the launcher.
set -u

if [ "$#" -ne 4 ]; then
    echo "usage: $0 MAKE_COMMAND BUILD_DIR TARGET STATUS_FILE" >&2
    exit 64
fi

make_command=$1
build_dir=$2
target=$3
status_file=$4

"$make_command" "$target"
status=$?
printf '%s\n' "$status" >"$status_file"
exit "$status"
