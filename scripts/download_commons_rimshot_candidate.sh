#!/bin/sh
# Download the small, checksum-addressable Wikimedia Commons Rimshot candidate
# into external instrument storage.  This is a discovery fixture, not a claim
# of event-level ground truth.
set -eu

if [ "$#" -ne 3 ]; then
    printf '%s\n' "download_commons_rimshot_candidate: usage: PATH URL SHA1" >&2
    exit 2
fi

audio_path=$1
download_url=$2
expected_sha1=$3

case "$download_url" in
    https://upload.wikimedia.org/wikipedia/commons/c/cb/Kevin_MacLeod_assorted_rimshots_-_13-second_roll.wav) ;;
    *)
        printf '%s\n' "download_commons_rimshot_candidate: refusing unverified URL=$download_url" >&2
        exit 1
        ;;
esac

if [ -s "$audio_path" ] && printf '%s  %s\n' "$expected_sha1" "$audio_path" | sha1sum -c - >/dev/null 2>&1; then
    printf '%s\n' "download_commons_rimshot_candidate: reused $audio_path"
    exit 0
fi

mkdir -p "$(dirname "$audio_path")"
partial_path="$audio_path.part"
if command -v aria2c >/dev/null 2>&1; then
    aria2c --continue=true --max-connection-per-server=4 --split=4 --min-split-size=1M \
        --file-allocation=none --allow-overwrite=true --auto-file-renaming=false \
        --retry-wait=5 --max-tries=20 --summary-interval=0 --console-log-level=warn \
        --dir "$(dirname "$partial_path")" --out "$(basename "$partial_path")" "$download_url"
else
    curl -fL -C - -o "$partial_path" "$download_url"
fi
printf '%s  %s\n' "$expected_sha1" "$partial_path" | sha1sum -c -
rm -f "$partial_path.aria2"
mv "$partial_path" "$audio_path"
printf '%s\n' "download_commons_rimshot_candidate: downloaded $audio_path"
