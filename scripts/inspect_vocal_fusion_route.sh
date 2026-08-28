#!/bin/sh
set -eu

printf '%s\n' '== Basic Pitch replay and gate targets =='
rg -n -C 2 'basic-pitch.*(replay|gate|safe|strict)|BASIC_PITCH.*(REPLAY|SAFE|STRICT)' Makefile
printf '%s\n' '== live gate constants =='
rg -n -C 2 'BasicPitch|basic_pitch|kBasicPitch|vocal.*fusion' src/plugin.cpp src/analyzer.cpp src/analyzer.hpp src/basic_pitch_onnx_worker.cpp
printf '%s\n' '== documented contract =='
sed -n '1,90p' docs/basic_pitch_vocal_fusion.md
