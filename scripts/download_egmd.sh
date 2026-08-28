#!/bin/sh
# Download the official E-GMD ZIP only into the external sample store.
set -eu

archive_path=${1:?usage: download_egmd.sh ARCHIVE URL MD5}
download_url=${2:?usage: download_egmd.sh ARCHIVE URL MD5}
expected_md5=${3:?usage: download_egmd.sh ARCHIVE URL MD5}
expected_url='https://storage.googleapis.com/magentadata/datasets/e-gmd/v1.0.0/e-gmd-v1.0.0.zip'

if [ "$download_url" != "$expected_url" ]; then
    printf '%s\n' "download_egmd: refusing unverified URL=$download_url" >&2
    exit 2
fi

if [ -s "$archive_path" ] && printf '%s  %s\n' "$expected_md5" "$archive_path" | md5sum -c - >/dev/null 2>&1; then
    printf '%s\n' "download_egmd: reused $archive_path"
    exit 0
fi

mkdir -p "$(dirname "$archive_path")"
partial_path="$archive_path.part"

download_once() {
    if command -v aria2c >/dev/null 2>&1; then
        aria2c --continue=true --max-connection-per-server=4 --split=4 --min-split-size=16M \
            --file-allocation=none --allow-overwrite=true --retry-wait=5 --max-tries=20 \
            --summary-interval=30 --console-log-level=warn --dir "$(dirname "$partial_path")" \
            --out "$(basename "$partial_path")" "$download_url"
    else
        curl -fL -C - -o "$partial_path" "$download_url"
    fi
}

# aria2 resumes a byte-complete .part file without fetching it again.  If that
# file fails the pinned checksum, retrying it would only fail immediately.  A
# single clean retry repairs a corrupted/inconsistent transfer while keeping
# ordinary interrupted downloads resumable and preventing an unbounded cycle.
attempt=1
while :; do
    download_once
    if printf '%s  %s\n' "$expected_md5" "$partial_path" | md5sum -c -; then
        rm -f "$partial_path.aria2"
        mv "$partial_path" "$archive_path"
        printf '%s\n' "download_egmd: downloaded $archive_path"
        exit 0
    fi
    if [ "$attempt" -ge 2 ]; then
        printf '%s\n' "download_egmd: checksum mismatch after clean retry: $partial_path" >&2
        exit 1
    fi
    printf '%s\n' "download_egmd: checksum mismatch; discarding corrupt partial and retrying once" >&2
    rm -f "$partial_path" "$partial_path.aria2"
    attempt=$((attempt + 1))
done
