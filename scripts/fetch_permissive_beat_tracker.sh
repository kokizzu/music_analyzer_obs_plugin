#!/usr/bin/env bash
# Fetch the MIT-licensed Beat-and-Tempo-Tracking source at one recorded commit.
set -euo pipefail

root_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
destination="$root_dir/third_party/beat_and_tempo_tracking"
repository=https://github.com/michaelkrzyzaniak/Beat-and-Tempo-Tracking.git

if [ -f "$destination/BTT.h" ] && [ -f "$destination/LICENSE" ]; then
	if [ -d "$destination/.git" ]; then
		git -C "$destination" rev-parse HEAD > "$destination/UPSTREAM_COMMIT"
		rm -rf "$destination/.git"
	fi
    printf 'permissive_beat_tracker: existing source %s\n' "$destination"
    exit 0
fi

mkdir -p "$root_dir/third_party"
temporary="$root_dir/build/beat_and_tempo_tracking.fetch"
rm -rf "$temporary" "$destination"
git clone --depth 1 "$repository" "$temporary"
test -f "$temporary/LICENSE"
grep -q 'MIT License' "$temporary/LICENSE"
mv "$temporary" "$destination"
git -C "$destination" rev-parse HEAD > "$destination/UPSTREAM_COMMIT"
rm -rf "$destination/.git"
printf 'permissive_beat_tracker: fetched %s\n' "$(cat "$destination/UPSTREAM_COMMIT")"
