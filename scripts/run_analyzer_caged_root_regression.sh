#!/bin/sh
set -eu

mkdir -p build
"${CXX:-g++}" -O2 -g -std=c++17 -fPIC -Wall -Wextra -Isrc -Itests \
	tests/analyzer_caged_root_regression.cpp build/analyzer_test.o build/btt_BTT.o build/btt_DFT.o \
	build/btt_Filter.o build/btt_STFT.o build/btt_Statistics.o build/btt_fastsin.o \
	build/basic_pitch_onnx_runtime.o build/basic_pitch_onnx_decoder.o \
	build/basic_pitch_onnx_worker.o build/basic_pitch_pcm_history.o -lm -pthread \
	-o build/analyzer_caged_root_regression
build/analyzer_caged_root_regression
