#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
	echo "usage: $0 COMMIT_MESSAGE PATH..." >&2
	exit 2
fi

message=$1
shift
git diff --check
git add -- "$@"
git commit -m "$message"
