#!/bin/sh
set -eu

if [ "$#" -ne 1 ] || [ -z "$1" ]; then
	echo "usage: make search-repo QUERY='fixed text'" >&2
	exit 2
fi

exec rg -n --fixed-strings -- "$1"
