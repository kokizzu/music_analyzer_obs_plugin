#!/bin/sh
# Print only the local state of the resumable MusicNet archive download.
set -eu

archive=${1:?missing MusicNet archive path}
partial="$archive.part"

if [ -f "$archive" ]; then
    bytes=$(wc -c < "$archive")
    echo "MusicNet archive ready: $archive ($bytes bytes)"
    exit 0
fi

if [ -f "$partial" ]; then
    bytes=$(wc -c < "$partial")
    echo "MusicNet download in progress: $partial ($bytes bytes)"
    exit 0
fi

echo "MusicNet archive has not started: $archive"
