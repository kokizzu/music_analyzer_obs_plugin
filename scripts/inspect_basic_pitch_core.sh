#!/bin/sh
# Render a non-interactive backtrace for the optional Basic Pitch corpus replay.
# Keeping this in the repository makes the crash diagnosis reproducible through
# the Makefile instead of asking a contributor to construct a debugger command.
set -eu

binary=${1:?usage: inspect_basic_pitch_core.sh BINARY CORE}
core=${2:?usage: inspect_basic_pitch_core.sh BINARY CORE}

if ! command -v gdb >/dev/null 2>&1; then
	printf '%s\n' 'inspect_basic_pitch_core: gdb is unavailable'
	exit 1
fi
if [ ! -f "$core" ]; then
	printf '%s\n' "inspect_basic_pitch_core: missing core file $core"
	exit 1
fi

gdb -batch -q "$binary" "$core" \
	-ex 'set pagination off' \
	-ex 'thread apply all bt full'
