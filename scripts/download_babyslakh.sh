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
curl --fail --location --retry 3 --retry-delay 2 --continue-at - --silent --show-error --output "$temporary_path" "$download_url"
printf '%s  %s\n' "$expected_md5" "$temporary_path" | md5sum -c -
mv "$temporary_path" "$archive_path"
printf '%s\n' "download_babyslakh: downloaded $archive_path"
