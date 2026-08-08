#!/bin/sh
set -eu

if [ "$#" -ne 5 ]; then
    printf '%s\n' "download_idmt_drums_archive: usage: ARCHIVE URL CONNECTIONS ARIA2C PYTHON" >&2
    exit 2
fi

archive=$1
url=$2
connections=$3
aria2c=$4
python=$5
source_dir=$(dirname "$archive")
archive_name=$(basename "$archive")
partial_archive="$archive.part"

mkdir -p "$source_dir"

if [ -s "$archive" ] && ! "$python" -m zipfile -t "$archive" >/dev/null 2>&1; then
    mv -f "$archive" "$partial_archive"
fi
if [ ! -s "$archive" ] && [ -s "$partial_archive" ] && "$python" -m zipfile -t "$partial_archive" >/dev/null 2>&1; then
    mv "$partial_archive" "$archive"
fi
if [ ! -s "$archive" ]; then
    if command -v "$aria2c" >/dev/null 2>&1; then
        "$aria2c" -c -x "$connections" -s "$connections" -k 1M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir "$source_dir" --out "$archive_name.part" "$url"
    else
        curl -fL -C - -o "$partial_archive" "$url"
    fi
fi
if [ -s "$partial_archive" ]; then
    "$python" -m zipfile -t "$partial_archive" >/dev/null
    mv "$partial_archive" "$archive"
fi
"$python" -m zipfile -t "$archive" >/dev/null
