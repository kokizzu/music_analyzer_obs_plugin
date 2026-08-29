#!/usr/bin/env bash
# Print the SCT-86PRO BLE lifecycle emitted by the installed debug analyzer.
set -euo pipefail

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
adb_path="$repo_root/build/android-sdk/platform-tools/adb"

if [ ! -x "$adb_path" ]; then
  echo "AUPHY runtime check unavailable: Android SDK adb is missing."
  exit 1
fi

authorized_devices=$("$adb_path" devices | awk 'NR > 1 && $2 == "device" { print $1 }')
if [ -z "$authorized_devices" ]; then
  echo "AUPHY runtime check unavailable: no authorized Android device."
  exit 1
fi

echo "SCT-86PRO runtime log (newest retained entries):"
auphy_log=$("$adb_path" logcat -d -v threadtime -s MusicAnalyzerAUPHY:V MusicAnalyzerDevices:V)
if [ -z "$auphy_log" ]; then
  echo "No AUPHY lifecycle log is retained. Enable AU in the app and power the SCT-86PRO so it advertises, then run this target again."
  exit 0
fi
printf '%s\n' "$auphy_log"
