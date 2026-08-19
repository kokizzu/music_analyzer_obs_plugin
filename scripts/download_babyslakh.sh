#!/bin/sh
# Download the official BabySlakh archive atomically into external sample storage.
set -eu

archive_path=${1:?usage: download_babyslakh.sh ARCHIVE URL MD5}
download_url=${2:?usage: download_babyslakh.sh ARCHIVE URL MD5}
expected_md5=${3:?usage: download_babyslakh.sh ARCHIVE URL MD5}

if [ -s "$archive_path" ] && printf '%s  %s\n' "$expected_md5" "$archive_path" | md5sum -c - >/dev/null 2>&1; then
    printf '%s\n' "download_babyslakh: reused $archive_path"
    exit 0
fi

mkdir -p "$(dirname "$archive_path")"
temporary_path="$archive_path.part"
# Zenodo's legacy record endpoint can answer a ranged resume request with a
# complete response.  Appending that response corrupts the archive, so this
# command deliberately starts a clean stream.  The background target keeps
# that one stream alive beyond the foreground command window.
rm -f "$temporary_path"
curl --fail --location --retry 12 --retry-delay 5 --silent --show-error --output "$temporary_path" "$download_url"
printf '%s  %s\n' "$expected_md5" "$temporary_path" | md5sum -c -
mv "$temporary_path" "$archive_path"
printf '%s\n' "download_babyslakh: downloaded $archive_path"
