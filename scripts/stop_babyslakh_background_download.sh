#!/bin/sh
# Stop only the dedicated BabySlakh transfer before a resumable restart.
set -eu

unit_name=music-analyzer-babyslakh-download.service
if systemctl --user is-active --quiet "$unit_name"; then
    systemctl --user stop "$unit_name"
    printf '%s\n' "download_babyslakh_background: stopped unit=$unit_name"
else
    printf '%s\n' "download_babyslakh_background: not running unit=$unit_name"
fi
