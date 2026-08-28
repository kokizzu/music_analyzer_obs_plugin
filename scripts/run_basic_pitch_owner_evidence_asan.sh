#!/bin/sh
# Rebuild the isolated corpus replay with AddressSanitizer, run one DCS pass,
# then restore the ordinary binary even when ASan reports a failure.
set -eu

make_cmd=${1:?usage: run_basic_pitch_owner_evidence_asan.sh MAKE BINARY CXXFLAGS LDFLAGS DCS RUNTIME MODEL LOG}
binary=${2:?}
base_cxxflags=${3:?}
base_ldflags=${4:-}
dcs=${5:?}
runtime=${6:?}
model=${7:?}
log=${8:?}

asan_cxxflags="$base_cxxflags -O1 -fno-omit-frame-pointer -fsanitize=address"
asan_ldflags="$base_ldflags -fsanitize=address"

restore() {
	"$make_cmd" -s -B "$binary" CXXFLAGS="$base_cxxflags" LDFLAGS="$base_ldflags" >/dev/null
}
trap restore EXIT

"$make_cmd" -s -B "$binary" CXXFLAGS="$asan_cxxflags" LDFLAGS="$asan_ldflags"
set +e
ASAN_OPTIONS=abort_on_error=1:detect_leaks=0 \
	"$binary" DCS "$dcs" "$runtime" "$model" owner-evidence 0.80 >"$log" 2>&1
status=$?
set -e
cat "$log"
exit "$status"
