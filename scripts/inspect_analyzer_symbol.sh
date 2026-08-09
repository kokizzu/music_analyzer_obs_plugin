#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || -z $1 ]]; then
	echo "usage: $0 SYMBOL|lines:START:END" >&2
	exit 2
fi

if [[ $1 =~ ^lines:([0-9]+):([0-9]+)$ ]]; then
	sed -n "${BASH_REMATCH[1]},${BASH_REMATCH[2]}p" src/analyzer.cpp
	exit 0
fi

rg -n -C 80 --fixed-strings "$1" src/analyzer.cpp
