#!/bin/sh
set -eu

root="build/InstrumentSamples/real-goal-fixture/prepared-multitrack-fixture"
if [ ! -d "$root" ]; then
	echo "missing external Prepared Multitrack fixture: $root" >&2
	exit 1
fi

export MUSIC_ANALYZER_PREPARED_MULTITRACK_ROOT="$root"
exec make test-real-prepared-multitrack-20
