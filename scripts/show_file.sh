#!/bin/sh
# Print a bounded text file through the repository's Makefile helper.
set -eu

file=${1:?usage: show_file.sh <file> [line-count]}
line_count=${2:-240}
exec sed -n "1,${line_count}p" "$file"
