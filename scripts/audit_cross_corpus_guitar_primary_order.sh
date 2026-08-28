#!/bin/sh
set -eu

guitar_chord_mix=${1:?Guitar Chord Mix attribute TSV is required}
gaps=${2:?GAPS attribute TSV is required}
guitar_techs=${3:?Guitar-TECHS attribute TSV is required}

audit_focus() {
	name=$1
	focus=$2
	protected_one=$3
	protected_two=$4
	output=$5
	{
		printf 'cross_corpus_primary_order: focus=%s protected=%s,%s\n' "$name" \
			"$(basename "$protected_one" .tsv)" "$(basename "$protected_two" .tsv)"
		python3 scripts/analyze_guitar_primary_order.py "$focus" \
			--protected-path "$protected_one" --protected-path "$protected_two" --examples 0 --summary-only |
			awk '
				/^same_root_extension_cross_corpus:/ ||
				/^cpp_style_cross_corpus:/ ||
				/^guitar_primary_order:/ { print }
			'
	} > "$output"
}

# Each focus scan is read-only and independent.  Run them concurrently so the
# third protection corpus increases validation strength without tripling the
# wall-clock delay before the generated accuracy dashboard can be refreshed.
audit_dir=$(mktemp -d "${TMPDIR:-/tmp}/music-analyzer-primary-order.XXXXXX")
trap 'rm -rf "$audit_dir"' EXIT HUP INT TERM

audit_focus "Guitar_Chord_Mix" "$guitar_chord_mix" "$gaps" "$guitar_techs" \
	"$audit_dir/guitar_chord_mix.out" &
pid_guitar_chord_mix=$!
audit_focus "GAPS" "$gaps" "$guitar_chord_mix" "$guitar_techs" \
	"$audit_dir/gaps.out" &
pid_gaps=$!
audit_focus "Guitar-TECHS" "$guitar_techs" "$guitar_chord_mix" "$gaps" \
	"$audit_dir/guitar_techs.out" &
pid_guitar_techs=$!

wait "$pid_guitar_chord_mix"
wait "$pid_gaps"
wait "$pid_guitar_techs"
cat "$audit_dir/guitar_chord_mix.out" "$audit_dir/gaps.out" "$audit_dir/guitar_techs.out"
