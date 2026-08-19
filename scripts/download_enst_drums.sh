#!/bin/sh
# Download the published ENST-Drums 16 kHz archive into external sample storage.
set -eu

archive_path=${1:?usage: download_enst_drums.sh ARCHIVE URL MD5 LICENSE_ACCEPTED}
download_url=${2:?usage: download_enst_drums.sh ARCHIVE URL MD5 LICENSE_ACCEPTED}
expected_md5=${3:?usage: download_enst_drums.sh ARCHIVE URL MD5 LICENSE_ACCEPTED}
license_accepted=${4:-0}

if [ "$license_accepted" != 1 ]; then
    printf '%s\n' "download_enst_drums: refusing download until ENST_DRUMS_LICENSE_ACCEPTED=1 confirms the research-use licence" >&2
    exit 2
fi

if [ -s "$archive_path" ] && printf '%s  %s\n' "$expected_md5" "$archive_path" | md5sum -c - >/dev/null 2>&1; then
    printf '%s\n' "download_enst_drums: reused $archive_path"
    exit 0
fi

case "$download_url" in
    https://zenodo.org/record/7831843/files/enstdrums_yourmt3_16k.tar.gz\?download=1) ;;
    *)
        printf '%s\n' "download_enst_drums: refusing unverified archive URL=$download_url" >&2
        exit 1
        ;;
esac

mkdir -p "$(dirname "$archive_path")"
temporary_path="$archive_path.part"
if command -v aria2c >/dev/null 2>&1; then
    aria2c --continue=true --max-connection-per-server=4 --split=4 --min-split-size=1M \
        --file-allocation=none --allow-overwrite=true --retry-wait=5 --max-tries=20 \
        --summary-interval=0 --console-log-level=warn --dir "$(dirname "$temporary_path")" \
        --out "$(basename "$temporary_path")" "$download_url"
else
    curl -fL -C - -o "$temporary_path" "$download_url"
fi
printf '%s  %s\n' "$expected_md5" "$temporary_path" | md5sum -c -
rm -f "$temporary_path.aria2"
mv "$temporary_path" "$archive_path"
printf '%s\n' "download_enst_drums: downloaded $archive_path"
