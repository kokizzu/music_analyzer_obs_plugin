#!/bin/sh
# Download the official BabySlakh archive atomically into external sample storage.
set -eu

archive_path=${1:?usage: download_babyslakh.sh ARCHIVE URL MD5}
download_url=${2:?usage: download_babyslakh.sh ARCHIVE URL MD5}
expected_md5=${3:?usage: download_babyslakh.sh ARCHIVE URL MD5}
download_connections=${4:-8}

if [ -s "$archive_path" ] && printf '%s  %s\n' "$expected_md5" "$archive_path" | md5sum -c - >/dev/null 2>&1; then
    printf '%s\n' "download_babyslakh: reused $archive_path"
    exit 0
fi

mkdir -p "$(dirname "$archive_path")"
temporary_path="$archive_path.part"
# The current API endpoint has been verified to return 206 plus an exact
# Content-Range.  Do not use the legacy /record endpoint: it can append a full
# response to a resume request.  aria2 keeps independently ranged chunks in a
# control file and the publisher MD5 below remains the acceptance gate.
case "$download_url" in
    https://zenodo.org/api/records/*/files/*/content) ;;
    *)
        printf '%s\n' "download_babyslakh: refusing unverified range endpoint=$download_url" >&2
        exit 1
        ;;
esac
aria2c --continue=true --max-connection-per-server="$download_connections" --split="$download_connections" --min-split-size=1M \
    --file-allocation=none --allow-overwrite=true --retry-wait=5 --max-tries=20 \
    --summary-interval=0 --console-log-level=warn --dir "$(dirname "$temporary_path")" \
    --out "$(basename "$temporary_path")" "$download_url"
printf '%s  %s\n' "$expected_md5" "$temporary_path" | md5sum -c -
mv "$temporary_path" "$archive_path"
printf '%s\n' "download_babyslakh: downloaded $archive_path"
