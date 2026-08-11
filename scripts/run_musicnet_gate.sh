#!/bin/sh
# Run a local MusicNet analyzer gate and retain its complete summary externally.
set -eu

binary=${1:?missing analyzer binary}
root=${2:?missing extracted MusicNet root}
output=${3:?missing measurement output path}
recordings=${4:-}
windows=${5:-}

case "$output" in
    */*) mkdir -p "${output%/*}" ;;
esac
temporary="$output.tmp"
set +e
if [ -n "$recordings" ] && [ -n "$windows" ]; then
    env MUSIC_ANALYZER_MUSICNET_ROOT="$root" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 \
        MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS="$recordings" \
        MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS="$windows" \
        "$binary" > "$temporary" 2>&1
else
    env MUSIC_ANALYZER_MUSICNET_ROOT="$root" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 \
        "$binary" > "$temporary" 2>&1
fi
status=$?
set -e
mv -f "$temporary" "$output"
cat "$output"
exit "$status"
