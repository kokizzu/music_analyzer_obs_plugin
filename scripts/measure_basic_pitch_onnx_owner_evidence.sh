#!/bin/sh
# Replay ONNX-supported native candidates as potential Vocal mirrors. The
# first corpus prints the TSV header; later corpus outputs omit it.
set -eu

binary=$1
runtime=$2
model=$3
dcs=$4
csd=$5
esmuc=$6
musicnet=$7
threshold=${8:-0.80}

first=1
work_dir=$(mktemp -d "${TMPDIR:-/tmp}/mao-owner-evidence.XXXXXX")
trap 'rm -rf "$work_dir"' EXIT HUP INT TERM
for corpus_root in "DCS:$dcs" "CSD:$csd" "ESMUC:$esmuc" "MusicNet:$musicnet"; do
	corpus=${corpus_root%%:*}
	root=${corpus_root#*:}
	corpus_output="$work_dir/$corpus.tsv"
	printf '%s\n' "basic_pitch_onnx_owner_evidence: $corpus" >&2
	"$binary" "$corpus" "$root" "$runtime" "$model" owner-evidence "$threshold" > "$corpus_output"
	if [ "$first" = 1 ]; then
		cat "$corpus_output"
		first=0
	else
		sed -n '2,$p' "$corpus_output"
	fi
done
