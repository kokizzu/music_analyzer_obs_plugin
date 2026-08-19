#!/bin/sh
# Start one resumable BabySlakh archive worker as a persistent user service.
set -eu

archive_path=${1:?usage: start_babyslakh_background_download.sh ARCHIVE URL MD5}
download_url=${2:?usage: start_babyslakh_background_download.sh ARCHIVE URL MD5}
expected_md5=${3:?usage: start_babyslakh_background_download.sh ARCHIVE URL MD5}
worker_path=${4:?usage: start_babyslakh_background_download.sh ARCHIVE URL MD5 WORKER CONNECTIONS}
download_connections=${5:-8}
unit_name=music-analyzer-babyslakh-download.service

if systemctl --user is-active --quiet "$unit_name"; then
    printf '%s\n' "download_babyslakh_background: already running unit=$unit_name"
    exit 0
fi

# A transient user unit does not automatically inherit the terminal's proxy
# environment.  Preserve only the conventional proxy variables so its curl
# request uses the same network path as the verified foreground downloader.
set -- --user --unit=music-analyzer-babyslakh-download --collect --quiet --same-dir
for proxy_name in http_proxy https_proxy HTTP_PROXY HTTPS_PROXY no_proxy NO_PROXY; do
    eval "proxy_value=\${$proxy_name-}"
    if [ -n "$proxy_value" ]; then
        set -- "$@" "--setenv=$proxy_name=$proxy_value"
    fi
done
systemd-run "$@" sh "$worker_path" "$archive_path" "$download_url" "$expected_md5" "$download_connections"
printf '%s\n' "download_babyslakh_background: started unit=$unit_name"
