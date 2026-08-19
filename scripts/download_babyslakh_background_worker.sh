#!/bin/sh
# Download the official BabySlakh archive outside the short foreground command window.
set -eu

archive_path=${1:?usage: download_babyslakh_background_worker.sh ARCHIVE URL MD5}
download_url=${2:?usage: download_babyslakh_background_worker.sh ARCHIVE URL MD5}
expected_md5=${3:?usage: download_babyslakh_background_worker.sh ARCHIVE URL MD5}
download_connections=${4:-8}
temporary_path="$archive_path.part"

mkdir -p "$(dirname "$archive_path")"
# The current API endpoint has been verified to return 206 plus an exact
# Content-Range.  Do not use the legacy /record endpoint: it can append a full
# response to a resume request.  aria2 keeps independently ranged chunks in a
# control file and the publisher MD5 below remains the acceptance gate.
case "$download_url" in
    https://zenodo.org/api/records/*/files/*/content) ;;
    *)
        printf '%s\n' "download_babyslakh_background: refusing unverified range endpoint=$download_url" >&2
        exit 1
        ;;
esac
if [ "$download_connections" -eq 1 ]; then
    # A single HTTP range stream can continue a valid contiguous tail without
    # aria2's piece map re-downloading already present bytes.
    curl --ipv4 --connect-timeout 20 --fail --location --retry 12 --retry-delay 5 \
        --continue-at - --silent --show-error --output "$temporary_path" "$download_url"
else
    aria2c --continue=true --max-connection-per-server="$download_connections" --split="$download_connections" --min-split-size=1M \
        --file-allocation=none --allow-overwrite=true --retry-wait=5 --max-tries=20 \
        --summary-interval=0 --console-log-level=warn --dir "$(dirname "$temporary_path")" \
        --out "$(basename "$temporary_path")" "$download_url"
fi
printf '%s  %s\n' "$expected_md5" "$temporary_path" | md5sum -c -
rm -f "$temporary_path.aria2"
mv "$temporary_path" "$archive_path"
printf '%s\n' "download_babyslakh_background: downloaded $archive_path"
