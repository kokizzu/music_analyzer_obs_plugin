#!/bin/sh
# Extract a verified AG-PT archive into the external InstrumentSamples store.
set -eu

if [ "$#" -ne 2 ]; then
	echo "usage: $0 ARCHIVE DESTINATION" >&2
	exit 2
fi

archive=$1
destination=$2
marker="$destination/.source_archive_md5"
archive_md5=$(md5sum "$archive" | awk '{print $1}')

if [ -f "$marker" ] && [ "$(cat "$marker")" = "$archive_md5" ]; then
	printf 'AG-PT extraction already matches archive: %s\n' "$destination"
	exit 0
fi

unzip -tqq "$archive"
mkdir -p "$destination"
unzip -qn "$archive" -d "$destination"
find "$destination" -type f -name '*.zip' -print | while IFS= read -r nested_archive; do
	unzip -qn "$nested_archive" -d "$(dirname "$nested_archive")"
done
temporary_marker="$marker.tmp"
printf '%s\n' "$archive_md5" > "$temporary_marker"
mv -f "$temporary_marker" "$marker"
printf 'AG-PT archive extracted to external sample store: %s\n' "$destination"
