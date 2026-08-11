#!/bin/sh
# Print only the local state of the resumable URMP archive download.
set -eu

archive=${1:?missing URMP archive path}
partial="$archive.part"

if [ -f "$archive" ]; then
	bytes=$(wc -c < "$archive")
	echo "URMP archive ready: $archive ($bytes bytes)"
	exit 0
fi

if [ -f "$partial" ]; then
	bytes=$(wc -c < "$partial")
	echo "URMP download in progress: $partial ($bytes bytes)"
	exit 0
fi

echo "URMP archive has not started: $archive"
