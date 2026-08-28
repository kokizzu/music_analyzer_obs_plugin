#!/bin/sh
set -eu

version="$1"
runtime_root="$2"
model_path="$3"
archive_dir="$(dirname "$runtime_root")"
archive="$archive_dir/onnxruntime-linux-x64-$version.tgz"

if [ ! -f "$runtime_root/include/onnxruntime_c_api.h" ]; then
  mkdir -p "$archive_dir"
  curl -fL --retry 2 \
    "https://github.com/microsoft/onnxruntime/releases/download/v$version/onnxruntime-linux-x64-$version.tgz" \
    -o "$archive"
  tar -xzf "$archive" -C "$archive_dir"
  rm -f "$archive"
fi

if [ ! -f "$model_path" ]; then
  mkdir -p "$(dirname "$model_path")"
  curl -fL --retry 2 \
    "https://raw.githubusercontent.com/spotify/basic-pitch/main/basic_pitch/saved_models/icassp_2022/nmp.onnx" \
    -o "$model_path"
fi
