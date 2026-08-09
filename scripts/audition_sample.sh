#!/usr/bin/env bash
# Play a short source excerpt while investigating detector traits.
set -euo pipefail

audio_path=${1:?audio path is required}
start_seconds=${2:-0}
duration_seconds=${3:-3}

if [[ ! -f "$audio_path" ]]; then
	echo "audition_sample: missing audio file: $audio_path" >&2
	exit 2
fi

case "$start_seconds:$duration_seconds" in
	*[!0-9.:]*|:*)
		echo "audition_sample: start and duration must be non-negative decimal seconds" >&2
		exit 2
		;;
esac

if command -v ffplay >/dev/null 2>&1; then
	exec ffplay -v error -nodisp -autoexit -ss "$start_seconds" -t "$duration_seconds" "$audio_path"
fi
if command -v mpv >/dev/null 2>&1; then
	exec mpv --no-video --really-quiet --start="$start_seconds" --length="$duration_seconds" "$audio_path"
fi

echo "audition_sample: install ffplay or mpv to play audio excerpts" >&2
exit 127
