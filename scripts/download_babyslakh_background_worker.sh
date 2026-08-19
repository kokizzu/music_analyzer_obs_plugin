#!/bin/sh
# Download the official BabySlakh archive outside the short foreground command window.
set -eu

archive_path=${1:?usage: download_babyslakh_background_worker.sh ARCHIVE URL MD5}
download_url=${2:?usage: download_babyslakh_background_worker.sh ARCHIVE URL MD5}
expected_md5=${3:?usage: download_babyslakh_background_worker.sh ARCHIVE URL MD5}
temporary_path="$archive_path.part"

mkdir -p "$(dirname "$archive_path")"
# The legacy Zenodo endpoint can ignore a byte-range resume and return a whole
# file, which would append a second archive to the partial.  Always begin one
# clean persistent transfer instead; retry only transient failures within it.
rm -f "$temporary_path"
curl --fail --location --retry 12 --retry-delay 5 --silent --show-error --output "$temporary_path" "$download_url"
printf '%s  %s\n' "$expected_md5" "$temporary_path" | md5sum -c -
mv "$temporary_path" "$archive_path"
printf '%s\n' "download_babyslakh_background: downloaded $archive_path"
