#!/bin/sh
# Remove only a partial archive proven corrupt by the publisher's checksum.
set -eu

archive_path=${1:?usage: discard_babyslakh_corrupt_partial.sh ARCHIVE MD5}
expected_md5=${2:?usage: discard_babyslakh_corrupt_partial.sh ARCHIVE MD5}
partial_path="$archive_path.part"

if [ ! -s "$partial_path" ]; then
    printf '%s\n' "discard_babyslakh_corrupt_partial: missing partial=$partial_path" >&2
    exit 1
fi
if printf '%s  %s\n' "$expected_md5" "$partial_path" | md5sum -c - >/dev/null 2>&1; then
    printf '%s\n' "discard_babyslakh_corrupt_partial: refusing to remove checksum-valid partial" >&2
    exit 1
fi
rm -f "$partial_path" "$partial_path.aria2" "$partial_path.aria2.log"
printf '%s\n' "discard_babyslakh_corrupt_partial: removed checksum-mismatched partial=$partial_path"
