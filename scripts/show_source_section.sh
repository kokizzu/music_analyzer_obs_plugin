#!/bin/sh
set -eu

if [ "$#" -ne 3 ]; then
	printf '%s\n' "usage: show_source_section.sh PATH START END" >&2
	exit 2
fi

path=$1
start=$2
end=$3

case "$start:$end" in
	*[!0-9:]*|*::*|:*)
		printf '%s\n' "show_source_section: START and END must be positive integers" >&2
		exit 2
		;;
esac

if [ "$start" -lt 1 ] || [ "$end" -lt "$start" ] || [ ! -f "$path" ]; then
	printf '%s\n' "show_source_section: invalid range or missing file" >&2
	exit 2
fi

sed -n "${start},${end}p" "$path"
