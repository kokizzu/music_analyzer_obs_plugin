#!/bin/sh
set -eu

analyzer=${1:?analyzer executable is required}
sample_dir=${2:?prepared sample directory is required}
minimum_samples=${3:?minimum samples is required}
attribute_output=${4:?attribute output is required}
measurement_output=${5:?measurement output is required}
state_dir=$(dirname "$sample_dir")
pidfile="$state_dir/full_mix_measurement.pid"
logfile="$state_dir/full_mix_measurement.log"

if [ -f "$pidfile" ]; then
	pid=$(cat "$pidfile" 2>/dev/null || true)
	if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
		printf 'AG-PT full-mix measurement already running: pid=%s log=%s\n' "$pid" "$logfile"
		exit 0
	fi
	rm -f "$pidfile"
fi

attribute_tmp="$attribute_output.$$.tmp"
measurement_tmp="$measurement_output.$$.tmp"
setsid nohup sh -c '
	set -eu
	env MUSIC_ANALYZER_REAL_NOTE_SAMPLES_REQUIRED=1 \
		MUSIC_ANALYZER_REAL_NOTE_FULL_MIX=1 \
		MUSIC_ANALYZER_REAL_NOTE_SAMPLE_ROOT="$2" \
		MUSIC_ANALYZER_REAL_NOTE_REQUIRED_SAMPLES="$3" \
		MUSIC_ANALYZER_REAL_NOTE_MIN_BASS=0 \
		MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR=0 \
		MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO=0 \
		MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS=0 \
		MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER=0 \
		MUSIC_ANALYZER_REAL_NOTE_MIN_ANY_HIT_PERCENT=0 \
		MUSIC_ANALYZER_REAL_NOTE_MIN_EXPECTED_ROW_PERCENT=0 \
		MUSIC_ANALYZER_REAL_NOTE_MIN_FIRST_ROW_PERCENT=0 \
		MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_EXPECTED_ROW_PERCENT=0 \
		MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_EXPECTED_ROW_PERCENT=0 \
		MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_EXPECTED_ROW_PERCENT=0 \
		MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_EXPECTED_ROW_PERCENT=0 \
		MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_EXPECTED_ROW_PERCENT=0 \
		MUSIC_ANALYZER_REAL_NOTE_MIN_BASS_FIRST_ROW_PERCENT=0 \
		MUSIC_ANALYZER_REAL_NOTE_MIN_GUITAR_FIRST_ROW_PERCENT=0 \
		MUSIC_ANALYZER_REAL_NOTE_MIN_PIANO_FIRST_ROW_PERCENT=0 \
		MUSIC_ANALYZER_REAL_NOTE_MIN_VOCALS_FIRST_ROW_PERCENT=0 \
		MUSIC_ANALYZER_REAL_NOTE_MIN_OTHER_FIRST_ROW_PERCENT=0 \
		MUSIC_ANALYZER_REAL_NOTE_MAX_DRUM_ACTIVE_PERCENT=100 \
		MUSIC_ANALYZER_REAL_NOTE_MAX_FAILURES=999999 \
		MUSIC_ANALYZER_REAL_NOTE_ATTRIBUTE_TSV="$4" \
		"$1" > "$5"
	mv -f "$4" "$6"
	mv -f "$5" "$7"
' sh "$analyzer" "$sample_dir" "$minimum_samples" "$attribute_tmp" "$measurement_tmp" "$attribute_output" "$measurement_output" >"$logfile" 2>&1 < /dev/null &
pid=$!
printf '%s\n' "$pid" >"$pidfile"
	printf 'AG-PT full-mix measurement started: pid=%s log=%s\n' "$pid" "$logfile"
