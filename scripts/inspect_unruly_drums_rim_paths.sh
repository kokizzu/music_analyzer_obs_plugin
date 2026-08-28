#!/bin/sh
# List archive paths which describe an Unruly Drums rim articulation.  Kept as
# a Makefile entry point so corpus inspection stays reproducible.
set -eu

if [ "$#" -ne 1 ]; then
    printf '%s\n' "usage: inspect_unruly_drums_rim_paths.sh ARCHIVE" >&2
    exit 2
fi

archive=$1
if [ ! -f "$archive" ]; then
    printf '%s\n' "Unruly Drums CC0 archive: archive not found: $archive" >&2
    exit 1
fi

unzip -Z1 "$archive" | awk 'BEGIN { IGNORECASE = 1 } /rim|side[ _-]*stick/ { print }'
