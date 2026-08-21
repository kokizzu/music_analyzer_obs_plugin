#!/bin/sh
# Discovery only: retrieve a labelled public candidate so its exact delivered
# checksum can be pinned before any derived fixture or analyzer measurement.
set -eu

if [ "$#" -ne 2 ]; then
    printf '%s\n' "discover_pixabay_rimshot_checksum: usage: MP3 URL" >&2
    exit 2
fi

mp3_path=$1
download_url=$2
case "$download_url" in
    https://cdn.pixabay.com/download/audio/*) ;;
    *)
        printf '%s\n' "discover_pixabay_rimshot_checksum: refusing non-Pixabay CDN URL" >&2
        exit 1
        ;;
esac
mkdir -p "$(dirname "$mp3_path")"
if [ ! -s "$mp3_path" ]; then
    curl -fL -C - -o "$mp3_path.part" "$download_url"
    mv "$mp3_path.part" "$mp3_path"
fi
if ! file --brief --mime-type "$mp3_path" | grep -Eq '^audio/|^application/octet-stream$'; then
    printf '%s\n' "discover_pixabay_rimshot_checksum: downloaded file is not an audio payload" >&2
    exit 1
fi
printf 'pixabay_rimshot_checksum_discovery: path=%s sha256=%s\n' "$mp3_path" "$(sha256sum "$mp3_path" | awk '{print $1}')"
