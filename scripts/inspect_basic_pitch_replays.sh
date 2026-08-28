#!/bin/sh
set -eu

for replay in \
	build/basic_pitch_onnx_choir_replay.tsv \
	build/basic_pitch_onnx_choir_full_replay.tsv \
	build/basic_pitch_onnx_choir_safe_replay.tsv \
	build/basic_pitch_onnx_choir_strict_replay.tsv \
	build/basic_pitch_onnx_musicnet_strict_replay.tsv \
	build/basic_pitch_onnx_cross_domain_safe_replay.tsv \
	build/basic_pitch_onnx_cross_domain_worker_safe_replay.tsv; do
	if [ -f "$replay" ]; then
		printf '== %s ==\n' "$replay"
		cat "$replay"
	else
		printf 'missing=%s\n' "$replay"
	fi
done

for audit in build/basic_pitch_onnx_owner_evidence.tsv build/basic_pitch_onnx_owner_evidence_audit.txt; do
	if [ -f "$audit" ]; then
		printf '== %s ==\n' "$audit"
		cat "$audit"
	else
		printf 'missing=%s\n' "$audit"
	fi
done

if [ -f build/basic_pitch_onnx_strict_sweep.tsv ]; then
	printf '%s\n' '== build/basic_pitch_onnx_strict_sweep.tsv =='
	cat build/basic_pitch_onnx_strict_sweep.tsv
fi
