#!/bin/sh
# Verify the archive endpoint can be reached without writing archive data.
set -eu

download_url=${1:?usage: probe_babyslakh_download.sh URL}

curl --ipv4 --connect-timeout 20 --max-time 30 --fail --location --range 0-0 \
    --silent --show-error --dump-header - --output /dev/null \
    --write-out 'probe_http_status=%{http_code}\nprobe_content_type=%{content_type}\nprobe_download_size=%{size_download}\n' \
    "$download_url"
