#!/usr/bin/env sh
set -eu

ANDROID_ADB=${ANDROID_ADB:-adb}
PACKAGE=${ANDROID_DEBUG_ROOT_PACKAGE:-dev.benalu.musicanalyzer.complete}
ACTIVITY=${ANDROID_DEBUG_ROOT_ACTIVITY:-dev.benalu.musicanalyzer.MainActivity}
ROOT_EXTRA=dev.benalu.musicanalyzer.DEBUG_MANUAL_ROOT

start_with_root() {
    "$ANDROID_ADB" shell am start --activity-single-top -n "$PACKAGE/$ACTIVITY" \
        --ei "$ROOT_EXTRA" "$1" >/dev/null
}

"$ANDROID_ADB" wait-for-device
"$ANDROID_ADB" logcat -c
"$ANDROID_ADB" shell am force-stop "$PACKAGE"
start_with_root 6 # F#

ready=false
attempt=0
while [ "$attempt" -lt 15 ]; do
    if "$ANDROID_ADB" logcat -d -v brief -s MusicAnalyzerFZ | grep -q 'LED service ready'; then
        ready=true
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done

if [ "$ready" != true ]; then
    printf '%s\n' 'measure-fret-zealot-update: Fret Zealot did not become ready within 15 seconds' >&2
    exit 1
fi

# The readiness callback starts the F# frame. Let that initial frame finish so
# the following result measures only a stable adjacent-root transition.
sleep 1

# Repeatable adjacent-root transition: F# to G.
start_with_root 7
sleep 2
"$ANDROID_ADB" logcat -d -v brief -s FretZealotSdk FretZealotGatt MusicAnalyzerFZ
