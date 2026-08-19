#!/bin/sh
# Extract the verified archive outside the short foreground command window.
set -eu

archive_path=${1:?usage: extract_babyslakh_background_worker.sh ARCHIVE DESTINATION PYTHON EXTRACTOR}
destination=${2:?usage: extract_babyslakh_background_worker.sh ARCHIVE DESTINATION PYTHON EXTRACTOR}
python=${3:?usage: extract_babyslakh_background_worker.sh ARCHIVE DESTINATION PYTHON EXTRACTOR}
extractor=${4:?usage: extract_babyslakh_background_worker.sh ARCHIVE DESTINATION PYTHON EXTRACTOR}

exec "$python" "$extractor" "$archive_path" "$destination"
