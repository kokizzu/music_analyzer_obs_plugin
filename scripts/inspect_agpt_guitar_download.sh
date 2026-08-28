#!/bin/sh
# Report the AG-PT-set archive state without scanning or modifying samples.
set -eu

archive=${1:?archive path is required}
if [ "$#" -eq 2 ]; then
	sleep "$2"
elif [ "$#" -ne 1 ]; then
	echo "usage: $0 ARCHIVE [WAIT_SECONDS]" >&2
	exit 2
fi
printf 'archive=%s\n' "$archive"
if [ -L build/InstrumentSamples ]; then
	printf 'build/InstrumentSamples -> %s\n' "$(readlink build/InstrumentSamples)"
fi
if [ -f "$archive" ]; then
	du -h "$archive"
	printf 'state=complete-candidate\n'
elif [ -f "$archive.part" ]; then
	du -h "$archive.part"
	stat -c 'partial_bytes=%s modified=%y' "$archive.part"
	if [ -f "$archive.part.aria2" ]; then
		du -h "$archive.part.aria2"
	fi
	printf 'state=resumable-partial\n'
else
	printf 'state=not-present\n'
fi
extracted_dir=$(dirname "$archive")/extracted
state_dir=$(dirname "$archive")
if [ -f "$state_dir/extract.pid" ]; then
	extract_pid=$(cat "$state_dir/extract.pid")
	if kill -0 "$extract_pid" 2>/dev/null; then
		ps -o pid=,state=,etime=,pcpu=,cmd= -p "$extract_pid" | sed 's/^/extraction_process=/'
	else
		printf 'extraction_process=not-running pid=%s\n' "$extract_pid"
	fi
fi
if [ -f "$state_dir/extract.log" ]; then
	tail -n 8 "$state_dir/extract.log" | sed 's/^/extraction_log=/'
fi
if [ -d "$extracted_dir" ]; then
	if [ -f "$extracted_dir/.source_archive_md5" ]; then
		printf 'extraction=complete archive_md5=%s\n' "$(cat "$extracted_dir/.source_archive_md5")"
	else
		printf 'extraction=in-progress-or-unverified\n'
	fi
	find "$extracted_dir" -type f -name '*.wav' -print | head -n 1 | sed 's/^/extracted_wav=/'
fi
if command -v pgrep >/dev/null 2>&1; then
	processes=$(pgrep -f 'aria2c.*aGPTset_z' || true)
	if [ -n "$processes" ]; then
		ps -o pid=,state=,etime=,pcpu=,cmd= -p "$processes"
	fi
fi
