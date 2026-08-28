#!/bin/sh
set -eu

binary=$1
runtime=$2
model=$3
dcs=$4
csd=$5
esmuc=$6
musicnet=$7

printf '%s\n' 'corpus	threshold	windows	expected	native_hits	onnx_hits	fused_hits	novel_correct	novel_false'
for threshold in 0.80 0.85 0.90 0.95; do
	"$binary" DCS "$dcs" "$runtime" "$model" all "$threshold"
	"$binary" CSD "$csd" "$runtime" "$model" all "$threshold"
	"$binary" ESMUC "$esmuc" "$runtime" "$model" all "$threshold"
	"$binary" MusicNet "$musicnet" "$runtime" "$model" all "$threshold"
done
