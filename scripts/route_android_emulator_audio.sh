#!/usr/bin/env sh
set -eu

watch=0
while [ "$#" -gt 0 ]; do
	case "$1" in
		--watch)
			watch=1
			;;
		--once)
			watch=0
			;;
		*)
			printf '%s\n' "android-route-desktop-audio: unknown option: $1" >&2
			exit 2
			;;
	esac
	shift
done

if ! command -v pactl >/dev/null 2>&1; then
	printf '%s\n' "android-route-desktop-audio: pactl is required" >&2
	exit 1
fi

route_once() {
	if [ -n "${ANDROID_MIC_SOURCE:-}" ]; then
		monitor_source=$ANDROID_MIC_SOURCE
	else
		default_sink=$(pactl get-default-sink)
		monitor_source="${default_sink}.monitor"
	fi

	source_row=$(pactl list short sources | awk -v source_name="$monitor_source" '$2 == source_name { print $1 " " $2; exit }')
	if [ -z "$source_row" ]; then
		printf '%s\n' "android-route-desktop-audio: source not found: $monitor_source" >&2
		printf '%s\n' "Available sources:" >&2
		pactl list short sources >&2
		return 1
	fi
	monitor_source_id=${source_row%% *}

	source_outputs=$(pactl list source-outputs | awk '
		function flush() {
			if (id != "" && is_qemu) {
				if (source == "")
					source = "?"
				print id " " source
			}
		}
		/^Source Output #/ {
			flush()
			id = substr($3, 2)
			source = ""
			is_qemu = 0
		}
		/^[[:space:]]*Source:/ {
			source = $2
		}
		/application\.process\.binary = "qemu-system/ || /application\.name = "qemu-system/ || /media\.name = "qemu"/ {
			is_qemu = 1
		}
		END {
			flush()
		}
	')

	if [ -z "$source_outputs" ]; then
		if [ "$watch" -eq 0 ]; then
			printf '%s\n' "android-route-desktop-audio: no active Android emulator recording stream found"
			printf '%s\n' "Start the emulator/app, grant microphone permission, then rerun: make android-route-desktop-audio"
		fi
		return 2
	fi

	printf '%s\n' "$source_outputs" | while read -r output source_id; do
		if [ -z "${output:-}" ]; then
			continue
		fi
		if [ "$source_id" = "$monitor_source_id" ]; then
			if [ "${ANDROID_ROUTE_VERBOSE:-0}" = "1" ]; then
				printf '%s\n' "android-route-desktop-audio: source-output $output already on $monitor_source"
			fi
			continue
		fi
		pactl move-source-output "$output" "$monitor_source"
		printf '%s\n' "android-route-desktop-audio: moved source-output $output to $monitor_source"
	done
}

if [ "$watch" -eq 1 ]; then
	printf '%s\n' "android-route-desktop-audio: watching emulator recording streams; press Ctrl+C to stop"
	reported_wait=0
	while :; do
		if route_once; then
			reported_wait=0
		else
			status=$?
			if [ "$status" -eq 2 ]; then
				if [ "$reported_wait" -eq 0 ]; then
					printf '%s\n' "android-route-desktop-audio: waiting for an active Android emulator recording stream"
					reported_wait=1
				fi
			else
				exit "$status"
			fi
		fi
		sleep "${ANDROID_ROUTE_INTERVAL:-1}"
	done
else
	if route_once; then
		:
	else
		status=$?
		if [ "$status" -eq 2 ]; then
			exit 0
		fi
		exit "$status"
	fi
fi
