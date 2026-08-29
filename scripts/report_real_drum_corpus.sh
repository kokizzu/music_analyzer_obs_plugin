#!/bin/sh
set -eu

binary="build/analyzer_real_drum_samples"
root="/media/kyz/sshflashtor/InstrumentSamples"
jobs="${MUSIC_ANALYZER_REAL_DRUM_JOBS:-3}"
verbose=0
verify=0

for option in "$@"; do
	case "$option" in
	--verbose) verbose=1 ;;
	--verify) verify=1 ;;
	*) echo "unknown option: $option" >&2; exit 2 ;;
	esac
done

if [ ! -x "$binary" ]; then
	echo "missing $binary; build/analyzer_real_drum_samples must be a prerequisite" >&2
	exit 1
fi

if [ ! -d "$root" ]; then
	echo "missing external fixture root: $root" >&2
	exit 1
fi

tmpdir=$(mktemp -d "${TMPDIR:-/tmp}/music-analyzer-real-drums.XXXXXX")
trap 'rm -rf "$tmpdir"' EXIT HUP INT TERM

running=0
failed=0
pids=""
names=""

run_manifest() {
	name=$1
	manifest_root=$2
	minimum_kick=0
	minimum_snare=0
	minimum_hihat=0
	if [ "$verify" -eq 1 ]; then
		case "$name" in
		drum_samples) minimum_hihat=65 ;;
		drum_machine_samples) minimum_hihat=45 ;;
		drum_samples_spread) minimum_hihat=50 ;;
		drum_samples_audit) minimum_hihat=58 ;;
		drum_samples_full) minimum_hihat=47 ;;
		hf_drum_kit_samples) minimum_kick=35; minimum_hihat=45 ;;
		esac
	fi
	if [ "$verbose" -eq 1 ]; then
		(
			MUSIC_ANALYZER_REAL_DRUM_ROOT="$manifest_root" \
			MUSIC_ANALYZER_REAL_DRUM_SOURCE="Speaker Monitor" \
			MUSIC_ANALYZER_REAL_DRUM_MIN_KICK="$minimum_kick" \
			MUSIC_ANALYZER_REAL_DRUM_MIN_SNARE="$minimum_snare" \
			MUSIC_ANALYZER_REAL_DRUM_MIN_HIHAT="$minimum_hihat" \
			MUSIC_ANALYZER_REAL_DRUM_VERBOSE=1 \
			"$binary"
		) > "$tmpdir/$name.out" 2>&1 &
	else
		(
			MUSIC_ANALYZER_REAL_DRUM_ROOT="$manifest_root" \
			MUSIC_ANALYZER_REAL_DRUM_SOURCE="Speaker Monitor" \
			MUSIC_ANALYZER_REAL_DRUM_MIN_KICK="$minimum_kick" \
			MUSIC_ANALYZER_REAL_DRUM_MIN_SNARE="$minimum_snare" \
			MUSIC_ANALYZER_REAL_DRUM_MIN_HIHAT="$minimum_hihat" \
			"$binary"
		) > "$tmpdir/$name.out" 2>&1 &
	fi
	pids="$pids $!"
	names="$names $name"
	running=$((running + 1))
}

wait_batch() {
	for pid in $pids; do
		if ! wait "$pid"; then
			failed=1
		fi
	done
	pids=""
	running=0
}

for name in drum_samples drum_machine_samples drum_samples_spread drum_samples_audit drum_samples_full hf_drum_kit_samples; do
	manifest_root="$root/$name"
	if [ ! -f "$manifest_root/manifest.tsv" ]; then
		echo "missing manifest: $manifest_root/manifest.tsv" >&2
		exit 1
	fi
	run_manifest "$name" "$manifest_root"
	if [ "$running" -ge "$jobs" ]; then
		wait_batch
	fi
done

wait_batch

for name in $names; do
	echo "real-drum-corpus manifest=$name"
	cat "$tmpdir/$name.out"
done

exit "$failed"
