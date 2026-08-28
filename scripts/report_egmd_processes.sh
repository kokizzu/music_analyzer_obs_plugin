#!/usr/bin/env sh
set -eu

if pgrep -af "build/analyzer_egmd"; then
    exit 0
fi
printf '%s\n' "analyzer_egmd: no running process"
