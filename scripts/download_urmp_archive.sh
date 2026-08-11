#!/bin/sh
# Download the public URMP mirror into the external sample store, resumably.
set -eu

if [ "$#" -ne 4 ]; then
	printf '%s\n' "usage: $0 ARCHIVE URL CONNECTIONS ARIA2C" >&2
	exit 2
fi

archive=$1
url=$2
connections=$3
aria2c=$4
partial="${archive}.part"

mkdir -p "$(dirname "$archive")"

if [ -s "$archive" ] && unzip -tqq "$archive" >/dev/null 2>&1; then
	echo "download_urmp_archive: verified existing $archive"
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

unzip -tqq "$partial"
mv -f "$partial" "$archive"
echo "download_urmp_archive: verified $archive"
