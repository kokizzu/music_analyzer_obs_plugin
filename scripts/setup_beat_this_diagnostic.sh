#!/usr/bin/env bash
# Install the optional, offline-only Beat This! inference dependencies without
# touching the system interpreter. Model/cache files stay in the external
# sample store; executable extensions stay in the local build directory because
# the removable store may be mounted noexec.
set -euo pipefail

model_cache=${1:?expected external diagnostic directory}
runtime=${2:?expected local runtime directory}
python=${3:?expected Python interpreter}
site_packages="$runtime/site-packages"

mkdir -p "$site_packages" "$model_cache/cache"
"$python" -m pip install --disable-pip-version-check --no-compile --no-deps --target "$site_packages" \
  beat-this soxr rotary-embedding-torch

# Keep the host CPU PyTorch first on sys.path. The optional package directory
# must never pull a second CUDA-enabled torch into the offline diagnostic.
"$python" -c '
import sys
sys.path.append("'"$site_packages"'")
import beat_this, rotary_embedding_torch, soxr, torch
print("Beat This diagnostic dependencies: ready")
'
