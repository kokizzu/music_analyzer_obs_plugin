#!/bin/sh
# Run the GuitarSet-format attribute summary through make run-repo-script.
set -eu

if [ "$#" -ne 1 ]; then
    printf '%s\n' 'usage: make run-repo-script SCRIPT=scripts/summarize_guitarset_attributes.sh ARGS=build/attributes.tsv' >&2
    exit 2
fi

exec python3 scripts/summarize_guitarset_attributes.py "$1"
