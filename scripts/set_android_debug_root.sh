#!/usr/bin/env sh
set -eu

ANDROID_ADB=${ANDROID_ADB:-adb}
ANDROID_DEBUG_ROOT=${ANDROID_DEBUG_ROOT:-G}
PACKAGE=${ANDROID_DEBUG_ROOT_PACKAGE:-dev.benalu.musicanalyzer.complete}
ACTIVITY=${ANDROID_DEBUG_ROOT_ACTIVITY:-dev.benalu.musicanalyzer.MainActivity}

normalized=$(printf '%s' "$ANDROID_DEBUG_ROOT" | tr '[:lower:]' '[:upper:]' | tr -d ' ')
case "$normalized" in
    C) pitch_class=0 ;;
    C\#|DB) pitch_class=1 ;;
    D) pitch_class=2 ;;
    D\#|EB) pitch_class=3 ;;
    E|FB) pitch_class=4 ;;
    F|E\#) pitch_class=5 ;;
    F\#|GB) pitch_class=6 ;;
    G) pitch_class=7 ;;
    G\#|AB) pitch_class=8 ;;
    A) pitch_class=9 ;;
    A\#|BB) pitch_class=10 ;;
    B|CB) pitch_class=11 ;;
    *)
        printf '%s\n' "android-set-root: unsupported root '$ANDROID_DEBUG_ROOT'" >&2
        exit 2
        ;;
esac

"$ANDROID_ADB" wait-for-device
result=$("$ANDROID_ADB" shell am start --activity-single-top -n "$PACKAGE/$ACTIVITY" \
    --ei dev.benalu.musicanalyzer.DEBUG_MANUAL_ROOT "$pitch_class")
case "$result" in
    *"Error type "*|*"Error:"*)
        printf '%s\n' "$result" >&2
        exit 1
        ;;
esac
printf '%s\n' "android-set-root: requested manual root $normalized ($pitch_class)"
