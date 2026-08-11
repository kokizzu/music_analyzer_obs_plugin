#!/bin/sh
# Extract a verified URMP ZIP into the external sample store without replacing it.
set -eu

if [ "$#" -ne 2 ]; then
	printf '%s\n' "usage: $0 ARCHIVE DESTINATION" >&2
	exit 2
fi

archive=$1
destination=$2

if [ ! -s "$archive" ]; then
	printf '%s\n' "extract_urmp_archive: missing archive $archive" >&2
	exit 1
fi
unzip -tqq "$archive"

if [ -d "$destination" ]; then
	if find "$destination" -type f -name 'AuMix_*.wav' -print -quit | grep -q .; then
		echo "extract_urmp_archive: reused $destination"
		exit 0
	fi
	if [ "$(find "$destination" -mindepth 1 -maxdepth 1 -print -quit)" ]; then
		printf '%s\n' "extract_urmp_archive: refusing non-empty destination $destination" >&2
		exit 1
	fi
else
	mkdir -p "$destination"
fi

unzip -q "$archive" -d "$destination"
if ! find "$destination" -type f -name 'AuMix_*.wav' -print -quit | grep -q .; then
	printf '%s\n' "extract_urmp_archive: extracted archive has no URMP AuMix WAV files" >&2
	exit 1
fi
echo "extract_urmp_archive: extracted $destination"
