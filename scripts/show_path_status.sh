#!/bin/sh
# Print concise path status through the repository Makefile/script convention.
set -eu

if [ "$#" -eq 0 ]; then
    printf '%s\n' 'show_path_status: provide one or more paths' >&2
    exit 2
fi

for path in "$@"; do
    if [ -L "$path" ]; then
        printf '%s\n' "symlink $path -> $(readlink "$path")"
    elif [ -f "$path" ]; then
        printf '%s\n' "file $path bytes=$(wc -c < "$path")"
    elif [ -d "$path" ]; then
        printf '%s\n' "directory $path"
    else
        printf '%s\n' "missing $path"
    fi
done
