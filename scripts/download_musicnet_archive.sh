#!/bin/sh
# Download an official MusicNet archive safely into the external sample store.
set -eu

if [ "$#" -ne 4 ]; then
	echo "usage: $0 ARCHIVE URL CONNECTIONS ARIA2C" >&2
	exit 2
fi

archive=$1
url=$2
connections=$3
aria2c=$4
partial="${archive}.part"

mkdir -p "$(dirname "$archive")"

if [ -s "$archive" ] && tar -tzf "$archive" >/dev/null 2>&1; then
	echo "download_musicnet_archive: verified existing $archive"
	exit 0
fi

if [ -s "$archive" ]; then
	mv -f "$archive" "$partial"
fi

if command -v "$aria2c" >/dev/null 2>&1; then
	"$aria2c" -c -x "$connections" -s "$connections" -k 1M --file-allocation=none \
		--allow-overwrite=true --auto-file-renaming=false --dir "$(dirname "$archive")" \
		--out "$(basename "$partial")" "$url"
else
	curl -fL -C - -o "$partial" "$url"
fi
tar -tzf "$partial" >/dev/null
mv -f "$partial" "$archive"
echo "download_musicnet_archive: verified $archive"
