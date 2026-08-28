#!/bin/sh
set -eu

object="build/analyzer_hihat_regression.o"
binary="build/analyzer_hihat_regression"
tmp_object="${object}.$$.tmp"
tmp_binary="${binary}.$$.tmp"

g++ -O2 -g -std=c++17 -fPIC -Wall -Wextra -Isrc -Itests \
    -c tests/analyzer_hihat_regression.cpp -o "$tmp_object"
mv "$tmp_object" "$object"
g++ -o "$tmp_binary" \
    build/analyzer_test.o \
    build/btt_BTT.o build/btt_DFT.o build/btt_Filter.o build/btt_STFT.o \
    build/btt_Statistics.o build/btt_fastsin.o \
    build/basic_pitch_onnx_runtime.o build/basic_pitch_onnx_decoder.o \
    build/basic_pitch_onnx_worker.o build/basic_pitch_pcm_history.o \
    "$object" -lm -pthread
mv "$tmp_binary" "$binary"
exec "$binary"
