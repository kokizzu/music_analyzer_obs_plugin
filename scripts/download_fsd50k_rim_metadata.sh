#!/bin/sh
# Download only the checksum-pinned FSD50K label and clip-metadata archives.
# Audio is deliberately not transferred until the rimshot preflight identifies
# a licence-compatible, single-event evaluation subset.
set -eu

if [ "$#" -ne 2 ]; then
    printf '%s\n' "download_fsd50k_rim_metadata: usage: DIRECTORY PYTHON" >&2
    exit 2
fi

directory=$1
python=$2
mkdir -p "$directory"

download() {
    name=$1
    url=$2
    expected_md5=$3
    archive="$directory/$name"
    partial="$archive.part"
    if [ -s "$archive" ] && printf '%s  %s\n' "$expected_md5" "$archive" | md5sum -c - >/dev/null 2>&1; then
        "$python" -m zipfile -t "$archive" >/dev/null
        printf '%s\n' "download_fsd50k_rim_metadata: reused $archive"
        return
    fi
    if [ -s "$archive" ]; then
        mv -f "$archive" "$partial"
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
    printf '%s\n' "download_fsd50k_rim_metadata: downloaded $archive"
}

download FSD50K.ground_truth.zip \
    'https://zenodo.org/record/4060432/files/FSD50K.ground_truth.zip?download=1' \
    ca27382c195e37d2269c4c866dd73485
download FSD50K.metadata.zip \
    'https://zenodo.org/record/4060432/files/FSD50K.metadata.zip?download=1' \
    b9ea0c829a411c1d42adb9da539ed237
