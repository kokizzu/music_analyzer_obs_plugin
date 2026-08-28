#!/bin/sh
# Fetch the official CC0 Unruly Drums release resumably into the shared sample
# store. This never writes the multi-gigabyte archive under build/.
set -eu

if [ "$#" -ne 3 ]; then
    printf '%s\n' "usage: download_unruly_drums_samples.sh ARCHIVE URL CHUNKS" >&2
    exit 2
fi
archive=$1
url=$2
chunks=$3
max_partial_bytes=800000000
chunk_bytes=16777216

case "$chunks" in
    *[!0-9]*|'')
        printf '%s\n' "Unruly Drums CC0 archive: CHUNKS must be a positive integer" >&2
        exit 2
        ;;
esac
if [ "$chunks" -le 0 ]; then
    printf '%s\n' "Unruly Drums CC0 archive: CHUNKS must be a positive integer" >&2
    exit 2
fi

if [ -s "$archive" ]; then
    if unzip -tqq "$archive"; then
        printf '%s\n' "Unruly Drums CC0 archive: reusing $archive"
        exit 0
    fi
    printf '%s\n' "Unruly Drums CC0 archive: existing archive is invalid: $archive" >&2
    exit 1
fi

mkdir -p "$(dirname "$archive")"
part="$archive.part"
lock="$part.lock"
if ! mkdir "$lock" 2>/dev/null; then
    printf '%s\n' "Unruly Drums CC0 archive: another downloader already owns $part" >&2
    exit 1
fi
trap 'rmdir "$lock"' EXIT HUP INT TERM
if [ -f "$part" ] && [ "$(wc -c < "$part")" -gt "$max_partial_bytes" ]; then
    quarantine="$archive.corrupt.$(date +%Y%m%d%H%M%S)"
    mv "$part" "$quarantine"
    printf '%s\n' "Unruly Drums CC0 archive: quarantined oversized partial at $quarantine" >&2
fi
batch=1
while [ "$batch" -le "$chunks" ]; do
    if [ -f "$part" ]; then
        offset=$(wc -c < "$part")
    else
        offset=0
    fi
    end=$((offset + chunk_bytes - 1))
    chunk="$part.chunk"
    rm -f "$chunk"
    curl -fsSL --range "$offset-$end" --retry 4 --retry-delay 3 -o "$chunk" "$url"
    chunk_size=$(wc -c < "$chunk")
    if [ "$chunk_size" -eq 0 ] || [ "$chunk_size" -gt "$chunk_bytes" ]; then
        quarantine="$archive.response.$(date +%Y%m%d%H%M%S)"
        mv "$chunk" "$quarantine"
        printf '%s\n' "Unruly Drums CC0 archive: rejected invalid range response at $quarantine" >&2
        exit 1
    fi
    cat "$chunk" >> "$part"
    rm -f "$chunk"
    if [ "$chunk_size" -lt "$chunk_bytes" ]; then
        break
    fi
    batch=$((batch + 1))
done

if [ "$chunk_size" -eq "$chunk_bytes" ]; then
    printf '%s\n' "Unruly Drums CC0 archive: downloaded through byte $end ($chunks bounded chunks this run)"
    exit 0
fi
if ! unzip -tqq "$part"; then
    quarantine="$archive.corrupt.$(date +%Y%m%d%H%M%S)"
    mv "$part" "$quarantine"
    printf '%s\n' "Unruly Drums CC0 archive: quarantined invalid download at $quarantine" >&2
    exit 1
fi
mv -f "$part" "$archive"
printf '%s\n' "Unruly Drums CC0 archive: downloaded to $archive"
