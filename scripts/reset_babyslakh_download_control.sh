#!/bin/sh
# Discard only aria2's stale resume-control sidecar; retain the partial archive.
set -eu

archive_path=${1:?usage: reset_babyslakh_download_control.sh ARCHIVE}
control_path="$archive_path.part.aria2"
rm -f "$control_path"
printf '%s\n' "download_babyslakh_background: reset control=$control_path"
