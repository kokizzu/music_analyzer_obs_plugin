#!/bin/sh
# Download an official MusicNet archive safely into the external sample store.
set -eu

if [ "$#" -ne 2 ]; then
	echo "usage: $0 ARCHIVE URL" >&2
	exit 2
fi

archive=$1
url=$2
partial="${archive}.part"

mkdir -p "$(dirname "$archive")"

if [ -s "$archive" ] && tar -tzf "$archive" >/dev/null 2>&1; then
	echo "download_musicnet_archive: verified existing $archive"
	exit 0
fi

if [ -s "$archive" ]; then
	mv -f "$archive" "$partial"
fi

curl -fL -C - -o "$partial" "$url"
tar -tzf "$partial" >/dev/null
mv -f "$partial" "$archive"
echo "download_musicnet_archive: verified $archive"
