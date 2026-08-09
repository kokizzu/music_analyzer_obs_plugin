#!/bin/sh
set -eu

if [ "$#" -ne 3 ] || [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "usage: make show-repo-lines FILE=path START=line END=line" >&2
    exit 2
fi

sed -n "$2,$3p" -- "$1"
