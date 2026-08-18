#!/bin/sh
# Show a bounded Make-managed corpus job log for diagnosis and progress checks.
set -eu

if [ "$#" -ne 2 ]; then
    echo "usage: $0 BUILD_DIR TARGET" >&2
    exit 64
fi

build_dir=$1
target=$2
safe_target=$(printf '%s' "$target" | tr '/:' '__')
log_file="$build_dir/corpus-download-jobs/$safe_target.log"

if [ ! -f "$log_file" ]; then
    echo "missing log: $log_file" >&2
    exit 2
fi

# curl redraws its meter with carriage returns. Read a bounded tail then turn
# those redraws into lines, so monitoring a slow large download stays useful
# instead of replaying the full transfer history.
tail -c 16384 "$log_file" | tr '\r' '\n' | tail -n 24
