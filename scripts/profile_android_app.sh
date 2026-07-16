#!/usr/bin/env sh
set -eu

ANDROID_ADB=${ANDROID_ADB:-adb}
ANDROID_PROFILE_PACKAGE=${ANDROID_PROFILE_PACKAGE:-dev.benalu.musicanalyzer.bassguitar}

"$ANDROID_ADB" wait-for-device >/dev/null
pid=$("$ANDROID_ADB" shell pidof "$ANDROID_PROFILE_PACKAGE" 2>/dev/null | tr -d '\r' | awk '{ print $1 }')
if [ -z "$pid" ]; then
	printf '%s\n' "android-profile: package is not running: $ANDROID_PROFILE_PACKAGE" >&2
	exit 1
fi

read_cpu_ticks() {
	"$ANDROID_ADB" shell cat /proc/stat 2>/dev/null | tr -d '\r' | awk '
		/^cpu / {
			total = 0
			for (i = 2; i <= NF; ++i)
				total += $i
			idle = $5 + $6
			print total " " idle
			exit
		}
	'
}

read_proc_ticks() {
	"$ANDROID_ADB" shell cat "/proc/$pid/stat" 2>/dev/null | tr -d '\r' | awk '{ print $14 + $15 }'
}

cpu_ticks1=$(read_cpu_ticks)
proc1=$(read_proc_ticks)
sleep 1
cpu_ticks2=$(read_cpu_ticks)
proc2=$(read_proc_ticks)
cpu=$(awk -v stats1="$cpu_ticks1" -v stats2="$cpu_ticks2" \
	-v proc1="${proc1:-0}" -v proc2="${proc2:-0}" '
	BEGIN {
		split(stats1, a, " ")
		split(stats2, b, " ")
		total_delta = b[1] - a[1]
		proc_delta = proc2 - proc1
		if (total_delta > 0 && proc_delta >= 0)
			printf "%.1f%%", proc_delta * 100.0 / total_delta
		else
			printf "unknown"
	}
')
device_cpu=$(awk -v stats1="$cpu_ticks1" -v stats2="$cpu_ticks2" '
	BEGIN {
		split(stats1, a, " ")
		split(stats2, b, " ")
		total_delta = b[1] - a[1]
		idle_delta = b[2] - a[2]
		if (total_delta > 0 && idle_delta >= 0)
			printf "%.1f%%", (total_delta - idle_delta) * 100.0 / total_delta
		else
			printf "unknown"
	}
')

meminfo=$("$ANDROID_ADB" shell dumpsys meminfo "$ANDROID_PROFILE_PACKAGE" 2>/dev/null | tr -d '\r')
pss_kb=$(printf '%s\n' "$meminfo" | awk '
	/TOTAL PSS:/ { print $3; found = 1; exit }
	/^ *TOTAL[ \t]+[0-9]/ { print $2; found = 1; exit }
	END { if (!found) print "unknown" }
')

proc_mem=$("$ANDROID_ADB" shell cat /proc/meminfo 2>/dev/null | tr -d '\r')
free_percent=$(printf '%s\n' "$proc_mem" | awk '
	/^MemTotal:/ { total = $2 }
	/^MemAvailable:/ { available = $2 }
	END {
		if (total > 0 && available >= 0)
			printf "%.1f%%", available * 100.0 / total
		else
			printf "unknown"
	}
')

printf 'package\t%s\n' "$ANDROID_PROFILE_PACKAGE"
printf 'pid\t%s\n' "$pid"
printf 'app_cpu\t%s\n' "$cpu"
printf 'device_cpu\t%s\n' "$device_cpu"
printf 'app_pss\t%s KB\n' "$pss_kb"
printf 'device_free_mem\t%s\n' "$free_percent"
