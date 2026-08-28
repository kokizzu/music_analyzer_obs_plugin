#!/bin/sh
# Verify that the official E-GMD archive remains directly downloadable before
# adding it as an automated external-sample-store acquisition.
set -eu

url=${1:?usage: probe_egmd_download.sh URL}
expected_url='https://storage.googleapis.com/magentadata/datasets/e-gmd/v1.0.0/e-gmd-v1.0.0.zip'

if [ "$url" != "$expected_url" ]; then
    printf '%s\n' "probe_egmd_download: refusing unverified URL=$url" >&2
    exit 2
fi

headers=$(curl -fsIL --max-time 30 "$url")
printf '%s\n' "$headers" | awk 'BEGIN { IGNORECASE = 1 } /^HTTP\// || /^content-type:/ || /^content-length:/ || /^accept-ranges:/ || /^x-goog-hash:/'
