#!/usr/bin/env sh
set -eu

ANDROID_ADB=${ANDROID_ADB:-adb}
PACKAGES=${ANDROID_STATUS_PACKAGES:-"dev.benalu.musicanalyzer.bassguitar dev.benalu.musicanalyzer.complete"}

"$ANDROID_ADB" wait-for-device >/dev/null

printf '%s\n' "Android packages:"
audio_dump=$("$ANDROID_ADB" shell dumpsys audio 2>/dev/null | tr -d '\r' || true)
for package in $PACKAGES; do
	pid=$("$ANDROID_ADB" shell pidof "$package" 2>/dev/null | tr -d '\r' | awk '{ print $1 }' || true)
	permission=$("$ANDROID_ADB" shell dumpsys package "$package" 2>/dev/null | tr -d '\r' |
		awk '/android.permission.RECORD_AUDIO:/ { print $0; found = 1; exit } END { if (!found) print "permission=unknown" }')
	record_state=$(printf '%s\n' "$audio_dump" | awk -v package="$package" '$0 ~ package { print $0 }' | tail -n 2)
	printf '  %s pid=%s %s\n' "$package" "${pid:-not-running}" "$permission"
	if [ -n "$record_state" ]; then
		printf '%s\n' "$record_state" | sed 's/^/    record: /'
	fi
done

printf '\n%s\n' "Recent Android capture logs:"
"$ANDROID_ADB" logcat -d -t 20 -s MusicAnalyzer 2>/dev/null | tr -d '\r' || true

if ! command -v pactl >/dev/null 2>&1; then
	printf '\n%s\n' "Host audio: pactl not found"
	exit 0
fi

printf '\n%s\n' "Host default sink:"
pactl get-default-sink || true

printf '\n%s\n' "Host sources:"
pactl list short sources || true

printf '\n%s\n' "Host playback streams:"
pactl list sink-inputs | awk '
	function clean(value) {
		gsub(/^[ \t"]+|[ \t"]+$/, "", value)
		return value
	}
	function flush() {
		if (id != "")
			printf "  #%s sink=%s corked=%s mute=%s app=%s media=%s\n", id, sink, corked, mute, app, media
	}
	/^Sink Input #/ {
		flush()
		id = substr($3, 2)
		sink = "?"
		corked = "?"
		mute = "?"
		app = "?"
		media = "?"
	}
	/^[ \t]*Sink:/ { sink = $2 }
	/^[ \t]*Corked:/ { corked = $2 }
	/^[ \t]*Mute:/ { mute = $2 }
	/application.name = / {
		value = $0
		sub(/^.*application.name = /, "", value)
		app = clean(value)
	}
	/media.name = / {
		value = $0
		sub(/^.*media.name = /, "", value)
		media = clean(value)
	}
	END { flush() }
' || true

printf '\n%s\n' "Android emulator recording streams:"
pactl list source-outputs | awk '
	function flush() {
		if (id != "" && is_qemu)
			printf "  #%s source=%s app=%s media=%s\n", id, source, app, media
	}
	function clean(value) {
		gsub(/^[ \t"]+|[ \t"]+$/, "", value)
		return value
	}
	/^Source Output #/ {
		flush()
		id = substr($3, 2)
		source = "?"
		app = "?"
		media = "?"
		is_qemu = 0
	}
	/^[ \t]*Source:/ { source = $2 }
	/application.name = / {
		value = $0
		sub(/^.*application.name = /, "", value)
		app = clean(value)
	}
	/media.name = / {
		value = $0
		sub(/^.*media.name = /, "", value)
		media = clean(value)
	}
	/application\.process\.binary = "qemu-system/ || /application\.name = "qemu-system/ || /media\.name = "qemu"/ {
		is_qemu = 1
	}
	END { flush() }
' || true
