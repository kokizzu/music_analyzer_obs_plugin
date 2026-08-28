#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
	printf '%s\n' "usage: summarize_real_note_attributes.sh ATTRIBUTE_TSV" >&2
	exit 2
fi

exec python3 scripts/summarize_real_note_attributes.py "$1"
