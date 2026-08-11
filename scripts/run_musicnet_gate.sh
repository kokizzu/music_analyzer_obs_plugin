#!/bin/sh
# Run a local MusicNet analyzer gate and retain its complete summary externally.
set -eu

binary=${1:?missing analyzer binary}
root=${2:?missing extracted MusicNet root}
output=${3:?missing measurement output path}
recordings=${4:-}
windows=${5:-}
attributes=${6:-}

case "$output" in
    */*) mkdir -p "${output%/*}" ;;
esac
temporary="$output.tmp"
set +e
if [ -n "$recordings" ] && [ -n "$windows" ]; then
	max_windows_per_recording=$((windows / recordings))
	if [ -n "$attributes" ]; then
        env MUSIC_ANALYZER_MUSICNET_ROOT="$root" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 \
            MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS="$recordings" \
            MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS="$windows" \
			MUSIC_ANALYZER_MUSICNET_MAX_RECORDINGS="$recordings" \
			MUSIC_ANALYZER_MUSICNET_MAX_WINDOWS_PER_RECORDING="$max_windows_per_recording" \
			MUSIC_ANALYZER_MUSICNET_ATTRIBUTE_TSV="$attributes" \
            "$binary" > "$temporary" 2>&1
	else
        env MUSIC_ANALYZER_MUSICNET_ROOT="$root" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 \
            MUSIC_ANALYZER_MUSICNET_REQUIRED_RECORDINGS="$recordings" \
            MUSIC_ANALYZER_MUSICNET_REQUIRED_WINDOWS="$windows" \
			MUSIC_ANALYZER_MUSICNET_MAX_RECORDINGS="$recordings" \
			MUSIC_ANALYZER_MUSICNET_MAX_WINDOWS_PER_RECORDING="$max_windows_per_recording" \
            "$binary" > "$temporary" 2>&1
	fi
else
	if [ -n "$attributes" ]; then
        env MUSIC_ANALYZER_MUSICNET_ROOT="$root" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 \
			MUSIC_ANALYZER_MUSICNET_ATTRIBUTE_TSV="$attributes" "$binary" > "$temporary" 2>&1
	else
        env MUSIC_ANALYZER_MUSICNET_ROOT="$root" MUSIC_ANALYZER_MUSICNET_REQUIRED=1 \
            "$binary" > "$temporary" 2>&1
	fi
fi
status=$?
set -e
mv -f "$temporary" "$output"
cat "$output"
exit "$status"
