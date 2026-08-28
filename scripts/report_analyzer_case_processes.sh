#!/usr/bin/env sh
set -eu

if pgrep -af "build/analyzer_cases"; then
    exit 0
fi
printf '%s\n' "analyzer_cases: no running process"
