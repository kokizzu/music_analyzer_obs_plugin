#!/bin/sh
# Resume the official BabySlakh download outside the short foreground command window.
set -eu

archive_path=${1:?usage: download_babyslakh_background_worker.sh ARCHIVE URL MD5}
download_url=${2:?usage: download_babyslakh_background_worker.sh ARCHIVE URL MD5}
expected_md5=${3:?usage: download_babyslakh_background_worker.sh ARCHIVE URL MD5}
temporary_path="$archive_path.part"

mkdir -p "$(dirname "$archive_path")"
if command -v aria2c >/dev/null 2>&1; then
    aria2c --allow-overwrite=true --auto-file-renaming=false --continue=true \
        --file-allocation=none --max-connection-per-server=8 --min-split-size=1M \
        --out "$(basename "$temporary_path")" --dir "$(dirname "$temporary_path")" \
        "$download_url"
else
    curl --fail --location --retry 12 --retry-delay 5 --continue-at - --silent --show-error --output "$temporary_path" "$download_url"
fi
printf '%s  %s\n' "$expected_md5" "$temporary_path" | md5sum -c -
mv "$temporary_path" "$archive_path"
printf '%s\n' "download_babyslakh_background: downloaded $archive_path"
