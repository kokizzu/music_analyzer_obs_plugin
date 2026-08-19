#!/bin/sh
# Start at most one persistent, traversal-safe BabySlakh extraction service.
set -eu

archive_path=${1:?usage: start_babyslakh_background_extraction.sh ARCHIVE DESTINATION PYTHON EXTRACTOR WORKER}
destination=${2:?usage: start_babyslakh_background_extraction.sh ARCHIVE DESTINATION PYTHON EXTRACTOR WORKER}
python=${3:?usage: start_babyslakh_background_extraction.sh ARCHIVE DESTINATION PYTHON EXTRACTOR WORKER}
extractor=${4:?usage: start_babyslakh_background_extraction.sh ARCHIVE DESTINATION PYTHON EXTRACTOR WORKER}
worker=${5:?usage: start_babyslakh_background_extraction.sh ARCHIVE DESTINATION PYTHON EXTRACTOR WORKER}
unit_name=music-analyzer-babyslakh-extract.service

if [ -d "$destination" ]; then
    printf '%s\n' "extract_babyslakh_background: reused destination=$destination"
    exit 0
fi
if systemctl --user is-active --quiet "$unit_name"; then
    printf '%s\n' "extract_babyslakh_background: already running unit=$unit_name"
    exit 0
fi
systemd-run --user --unit=music-analyzer-babyslakh-extract --collect --quiet \
    sh "$worker" "$archive_path" "$destination" "$python" "$extractor"
printf '%s\n' "extract_babyslakh_background: started unit=$unit_name"
