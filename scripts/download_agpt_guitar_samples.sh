#!/bin/sh
# Download the official AG-PT-set archive into the external InstrumentSamples
# store.  The archive is resumable and never occupies build/ with large data.
set -eu

if [ "$#" -ne 3 ]; then
	printf '%s\n' 'usage: download_agpt_guitar_samples.sh ARCHIVE URL EXPECTED_MD5' >&2
	exit 2
fi

archive=$1
url=$2
expected_md5=$3
part="$archive.part"

validate() {
	actual_md5=$(md5sum "$1" | awk '{print $1}')
	if [ "$actual_md5" != "$expected_md5" ]; then
		printf '%s\n' "AG-PT-set archive: checksum mismatch for $1 (got $actual_md5)" >&2
		return 1
	fi
	unzip -tqq "$1"
}

if [ -s "$archive" ]; then
	validate "$archive"
	printf '%s\n' "AG-PT-set archive: reusing $archive"
	exit 0
fi

# An interrupted manager can leave aria2c with a complete .part file after it
# exits. Validate and promote it before asking aria2c to attach again.
if [ -s "$part" ] && validate "$part"; then
	mv -f "$part" "$archive"
	printf '%s\n' "AG-PT-set archive: promoted verified $archive"
	exit 0
fi

mkdir -p "$(dirname "$archive")"
if command -v aria2c >/dev/null 2>&1; then
	aria2c -c -x 8 -s 8 -k 1M --file-allocation=none --allow-overwrite=true \
		--dir "$(dirname "$part")" --out "$(basename "$part")" "$url"
else
	curl -fL --retry 5 --retry-delay 3 -C - -o "$part" "$url"
fi
validate "$part"
mv -f "$part" "$archive"
printf '%s\n' "AG-PT-set archive: downloaded to $archive"
