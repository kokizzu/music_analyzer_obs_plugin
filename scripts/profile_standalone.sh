#!/usr/bin/env sh
set -eu

if ! command -v /usr/bin/time >/dev/null 2>&1; then
	printf '%s\n' "profile-standalone: /usr/bin/time is required" >&2
	exit 1
fi

BUILD_DIR=${BUILD_DIR:-build}
PROFILE_SECONDS=${PROFILE_SECONDS:-20}
PROFILE_SAMPLE_RATE=${PROFILE_SAMPLE_RATE:-48000}
PROFILE_DIR="$BUILD_DIR/profile"
PROFILE_AUDIO="$PROFILE_DIR/profile.f32"

mkdir -p "$PROFILE_DIR"

host_cpu=$(awk -F: '/model name/ { gsub(/^[ \t]+/, "", $2); print $2; exit }' /proc/cpuinfo 2>/dev/null || true)
host_logical_cpus=$(getconf _NPROCESSORS_ONLN 2>/dev/null || true)
printf 'host_cpu\t%s\n' "${host_cpu:-unknown}"
printf 'host_logical_cpus\t%s\n' "${host_logical_cpus:-unknown}"

python3 - "$PROFILE_AUDIO" "$PROFILE_SECONDS" "$PROFILE_SAMPLE_RATE" <<'PY'
import math
import struct
import sys

path = sys.argv[1]
duration = float(sys.argv[2])
sample_rate = int(sys.argv[3])
total = int(duration * sample_rate)
chord_roots = [43, 48, 50, 55]

with open(path, "wb") as out:
    for i in range(total):
        t = i / sample_rate
        root = chord_roots[int(t // 2.0) % len(chord_roots)]
        freqs = [
            440.0 * (2.0 ** ((root - 69) / 12.0)),
            440.0 * (2.0 ** ((root + 7 - 69) / 12.0)),
            440.0 * (2.0 ** ((root + 12 - 69) / 12.0)),
            440.0 * (2.0 ** ((root + 16 - 69) / 12.0)),
        ]
        value = 0.0
        for harmonic, freq in enumerate(freqs, start=1):
            value += (0.12 / harmonic) * math.sin(2.0 * math.pi * freq * t)
        beat = t % 0.5
        if beat < 0.030:
            value += 0.40 * math.sin(2.0 * math.pi * 62.0 * t) * (1.0 - beat / 0.030)
        offbeat = (t + 0.25) % 0.5
        if offbeat < 0.020:
            value += 0.12 * math.sin(2.0 * math.pi * 1800.0 * t) * (1.0 - offbeat / 0.020)
        out.write(struct.pack("<f", max(-0.95, min(0.95, value))))
PY

profile_one() {
	label=$1
	binary=$2
	time_log="$PROFILE_DIR/$label.time"
	stdout_log="$PROFILE_DIR/$label.stdout"

	env SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy /usr/bin/time -v "$binary" \
		--raw-f32le "$PROFILE_AUDIO" \
		--sample-rate "$PROFILE_SAMPLE_RATE" \
		--fps 15 >"$stdout_log" 2>"$time_log"

	cpu=$(sed -n 's/.*Percent of CPU this job got:[ 	]*//p' "$time_log")
	rss=$(sed -n 's/.*Maximum resident set size (kbytes):[ 	]*//p' "$time_log")
	elapsed=$(sed -n 's/.*Elapsed (wall clock) time (h:mm:ss or m:ss):[ 	]*//p' "$time_log")
	user_seconds=$(sed -n 's/.*User time (seconds):[ 	]*//p' "$time_log")
	sys_seconds=$(sed -n 's/.*System time (seconds):[ 	]*//p' "$time_log")
	realtime_cpu=$(awk -v user="${user_seconds:-0}" -v sys="${sys_seconds:-0}" \
		-v duration="$PROFILE_SECONDS" 'BEGIN { printf "%.1f%%", (user + sys) * 100.0 / duration }')

	printf '%s\tJobCPU %s\tRealtimeCPU %s\tMaxRSS %s KB\tElapsed %s\tUser %ss\tSys %ss\n' \
		"$label" "${cpu:-unknown}" "$realtime_cpu" "${rss:-unknown}" "${elapsed:-unknown}" \
		"${user_seconds:-unknown}" "${sys_seconds:-unknown}"
}

profile_one "bass-guitar" "$BUILD_DIR/music-analyzer-bass-guitar"
profile_one "complete" "$BUILD_DIR/music-analyzer-standalone"
