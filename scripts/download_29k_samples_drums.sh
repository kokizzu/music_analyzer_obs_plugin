#!/bin/sh
# Download the open 29kSamplesDrumsDataset archive into external sample storage.
set -eu

if [ "$#" -ne 4 ]; then
    printf '%s\n' "download_29k_samples_drums: usage: ARCHIVE URL MD5 PYTHON" >&2
    exit 2
fi

archive=$1
url=$2
expected_md5=$3
python=$4

case "$url" in
    https://zenodo.org/records/4958592/files/29kSamplesDrumsDataset.zip\?download=1) ;;
    *)
        printf '%s\n' "download_29k_samples_drums: refusing unverified archive URL=$url" >&2
        exit 1
        ;;
esac

directory=$(dirname "$archive")
partial="$archive.part"
mkdir -p "$directory"

if [ -s "$archive" ] && printf '%s  %s\n' "$expected_md5" "$archive" | md5sum -c - >/dev/null 2>&1; then
    "$python" -m zipfile -t "$archive" >/dev/null
    printf '%s\n' "download_29k_samples_drums: reused $archive"
    exit 0
fi

if [ -s "$archive" ]; then
    mv -f "$archive" "$partial"
fi
if [ ! -s "$partial" ]; then
    : > "$partial"
fi

if command -v aria2c >/dev/null 2>&1; then
    aria2c --continue=true --max-connection-per-server=4 --split=4 --min-split-size=1M \
        --file-allocation=none --allow-overwrite=true --auto-file-renaming=false \
        --retry-wait=5 --max-tries=20 --summary-interval=0 --console-log-level=warn \
        --dir "$directory" --out "$(basename "$partial")" "$url"
else
    curl -fL -C - -o "$partial" "$url"
fi

printf '%s  %s\n' "$expected_md5" "$partial" | md5sum -c -
"$python" -m zipfile -t "$partial" >/dev/null
rm -f "$partial.aria2"
mv "$partial" "$archive"
printf '%s\n' "download_29k_samples_drums: downloaded $archive"
