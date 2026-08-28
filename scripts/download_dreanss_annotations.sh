#!/bin/sh
# Download and validate the official DREANSS annotation ZIP in the sample store.
set -eu

if [ "$#" -ne 3 ]; then
	echo "usage: $0 ARCHIVE URL EXPECTED_MD5" >&2
	exit 2
fi

archive=$1
url=$2
expected_md5=$3
partial="$archive.part"

validate() {
	actual_md5=$(md5sum "$1" | awk '{print $1}')
	if [ "$actual_md5" != "$expected_md5" ]; then
		echo "checksum mismatch for $1: got $actual_md5, expected $expected_md5" >&2
		exit 1
	fi
	unzip -tqq "$1"
}

if [ -s "$archive" ]; then
	validate "$archive"
	printf 'DREANSS annotations already verified: %s\n' "$archive"
	exit 0
fi

mkdir -p "$(dirname "$archive")"
curl -fL --retry 5 --retry-delay 3 -C - -o "$partial" "$url"
validate "$partial"
mv -f "$partial" "$archive"
printf 'DREANSS annotations downloaded and verified: %s\n' "$archive"
