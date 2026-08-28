#!/bin/sh
set -eu

sample_dir=${1:?prepared sample directory is required}
minimum_samples=${2:?minimum samples is required}
state_dir=$(dirname "$sample_dir")
pidfile="$state_dir/prepare.pid"
logfile="$state_dir/prepare.log"
manifest="$sample_dir/manifest.tsv"

if [ -f "$pidfile" ]; then
	pid=$(cat "$pidfile" 2>/dev/null || true)
	if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
		printf 'preparation_process=running pid=%s\n' "$pid"
		ps -o pid=,state=,etimes=,pcpu=,pmem=,command= -p "$pid" | sed 's/^/  /'
	else
		printf 'preparation_process=not-running pid=%s\n' "${pid:---}"
	fi
else
	printf '%s\n' 'preparation_process=not-started'
fi

if [ -f "$manifest" ]; then
	prepared=$(awk 'END { print (NR > 0 ? NR - 1 : 0) }' "$manifest")
	printf 'prepared_samples=%s required=%s\n' "$prepared" "$minimum_samples"
	if [ "$prepared" -ge "$minimum_samples" ]; then
		printf '%s\n' 'preparation=complete'
	else
		printf '%s\n' 'preparation=incomplete'
	fi
else
	printf '%s\n' 'preparation=no-manifest'
	if [ -d "$sample_dir" ]; then
		partial_samples=$(find "$sample_dir" -type f -name '*.wav' | wc -l | tr -d '[:space:]')
		printf 'prepared_samples_partial=%s\n' "$partial_samples"
	fi
fi

if [ -f "$logfile" ]; then
	printf '%s\n' 'preparation_log_tail:'
	tail -n 12 "$logfile" | sed 's/^/  /'
fi

evaluation_pidfile="$state_dir/evaluation.pid"
evaluation_logfile="$state_dir/evaluation.log"
if [ -f "$evaluation_pidfile" ]; then
	evaluation_pid=$(cat "$evaluation_pidfile" 2>/dev/null || true)
	if [ -n "$evaluation_pid" ] && kill -0 "$evaluation_pid" 2>/dev/null; then
		printf 'evaluation_process=running pid=%s\n' "$evaluation_pid"
		ps -o pid=,state=,etimes=,pcpu=,pmem=,command= -p "$evaluation_pid" | sed 's/^/  /'
	else
		printf 'evaluation_process=not-running pid=%s\n' "${evaluation_pid:---}"
	fi
else
	printf '%s\n' 'evaluation_process=not-queued'
fi
if [ -f "$evaluation_logfile" ]; then
	printf '%s\n' 'evaluation_log_tail:'
	tail -n 12 "$evaluation_logfile" | sed 's/^/  /'
fi

shard_outputs=$(find build -maxdepth 1 -type f -name 'real_note_agpt_guitar_shard_*.out' | wc -l | tr -d '[:space:]')
printf 'evaluation_shard_outputs=%s/32\n' "$shard_outputs"
if [ -f build/real_note_agpt_guitar_shard_0.out ]; then
	printf '%s\n' 'evaluation_shard_0_head:'
	sed -n '1,28p' build/real_note_agpt_guitar_shard_0.out | sed 's/^/  /'
fi
if [ -f build/agpt_guitar_measurement.tsv ]; then
	printf '%s\n' 'evaluation_measurement:'
	cat build/agpt_guitar_measurement.tsv | sed 's/^/  /'
fi
full_mix_pidfile="$state_dir/full_mix_measurement.pid"
full_mix_logfile="$state_dir/full_mix_measurement.log"
if [ -f "$full_mix_pidfile" ]; then
	full_mix_pid=$(cat "$full_mix_pidfile" 2>/dev/null || true)
	if [ -n "$full_mix_pid" ] && kill -0 "$full_mix_pid" 2>/dev/null; then
		printf 'full_mix_measurement_process=running pid=%s\n' "$full_mix_pid"
		ps -o pid=,state=,etimes=,pcpu=,pmem=,command= -p "$full_mix_pid" | sed 's/^/  /'
	else
		printf 'full_mix_measurement_process=not-running pid=%s\n' "${full_mix_pid:---}"
	fi
else
	printf '%s\n' 'full_mix_measurement_process=not-started'
fi
if [ -f "$full_mix_logfile" ]; then
	printf '%s\n' 'full_mix_measurement_log_tail:'
	tail -n 12 "$full_mix_logfile" | sed 's/^/  /'
fi
if [ -f build/agpt_guitar_full_mix_attributes.tsv ]; then
	printf '%s\n' 'full_mix_attribute_schema:'
	head -n 1 build/agpt_guitar_full_mix_attributes.tsv | cut -c 1-2000 | sed 's/^/  /'
	printf '%s\n' 'full_mix_first_row:'
	sed -n '2p' build/agpt_guitar_full_mix_attributes.tsv | cut -f1-18 | sed 's/^/  /'
fi
for partial in build/agpt_guitar_full_mix_attributes.tsv.*.tmp; do
	if [ -f "$partial" ]; then
		partial_rows=$(awk 'END { print (NR > 0 ? NR - 1 : 0) }' "$partial")
		printf 'full_mix_partial=%s rows=%s\n' "$partial" "$partial_rows"
	fi
done
mining_state_dir=build
mining_pidfile="$mining_state_dir/visual_mining.pid"
mining_logfile="$mining_state_dir/visual_mining.log"
if [ -f "$mining_pidfile" ]; then
	mining_pid=$(cat "$mining_pidfile" 2>/dev/null || true)
	if [ -n "$mining_pid" ] && kill -0 "$mining_pid" 2>/dev/null; then
		printf 'visual_miner_process=running pid=%s\n' "$mining_pid"
		ps -o pid=,state=,etimes=,pcpu=,pmem=,command= -p "$mining_pid" | sed 's/^/  /'
	else
		printf 'visual_miner_process=not-running pid=%s\n' "${mining_pid:---}"
	fi
else
	printf '%s\n' 'visual_miner_process=not-started'
fi
if [ -f "$mining_logfile" ]; then
	printf '%s\n' 'visual_miner_log_tail:'
	tail -n 12 "$mining_logfile" | sed 's/^/  /'
fi
