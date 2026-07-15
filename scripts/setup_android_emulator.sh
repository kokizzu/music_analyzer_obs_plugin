#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
BUILD_DIR=${BUILD_DIR:-"$ROOT_DIR/build"}
ANDROID_SDK_ROOT=${ANDROID_SDK_ROOT:-"$BUILD_DIR/android-sdk"}
ANDROID_AVD_HOME=${ANDROID_AVD_HOME:-"$BUILD_DIR/android-avd"}
ANDROID_EMULATOR_API=${ANDROID_EMULATOR_API:-35}
ANDROID_EMULATOR_ABI=${ANDROID_EMULATOR_ABI:-x86_64}
ANDROID_EMULATOR_IMAGE=${ANDROID_EMULATOR_IMAGE:-google_apis}
ANDROID_AVD_NAME=${ANDROID_AVD_NAME:-"music_analyzer_api${ANDROID_EMULATOR_API}_${ANDROID_EMULATOR_ABI}"}

CMDLINE_ROOT="$ANDROID_SDK_ROOT/cmdline-tools/latest"
SDKMANAGER="$CMDLINE_ROOT/bin/sdkmanager"
AVDMANAGER="$CMDLINE_ROOT/bin/avdmanager"
EMULATOR="$ANDROID_SDK_ROOT/emulator/emulator"
SYSTEM_IMAGE_PACKAGE="system-images;android-${ANDROID_EMULATOR_API};${ANDROID_EMULATOR_IMAGE};${ANDROID_EMULATOR_ABI}"
SYSTEM_IMAGE_DIR="$ANDROID_SDK_ROOT/system-images/android-${ANDROID_EMULATOR_API}/${ANDROID_EMULATOR_IMAGE}/${ANDROID_EMULATOR_ABI}"

if [ -d "$CMDLINE_ROOT/bin" ]; then
	chmod +x "$CMDLINE_ROOT"/bin/* 2>/dev/null || true
fi

if [ ! -x "$SDKMANAGER" ] || [ ! -x "$AVDMANAGER" ]; then
	printf '%s\n' "setup-android-emulator: run make setup-android first; Android command-line tools are missing" >&2
	exit 1
fi

emulator_packages_installed() {
	[ -x "$EMULATOR" ] && [ -f "$SYSTEM_IMAGE_DIR/source.properties" ]
}

mkdir -p "$ANDROID_AVD_HOME"

if emulator_packages_installed; then
	printf '%s\n' "setup-android-emulator: emulator packages already installed; skipping sdkmanager"
else
	yes | "$SDKMANAGER" --sdk_root="$ANDROID_SDK_ROOT" --licenses >/dev/null 2>&1 || true
	yes | "$SDKMANAGER" --sdk_root="$ANDROID_SDK_ROOT" \
		"emulator" \
		"$SYSTEM_IMAGE_PACKAGE"
fi

if [ -d "$ANDROID_SDK_ROOT/emulator" ]; then
	chmod +x "$ANDROID_SDK_ROOT"/emulator/* 2>/dev/null || true
fi

if [ -f "$ANDROID_AVD_HOME/${ANDROID_AVD_NAME}.ini" ] &&
	[ -d "$ANDROID_AVD_HOME/${ANDROID_AVD_NAME}.avd" ]; then
	printf '%s\n' "setup-android-emulator: AVD already exists at $ANDROID_AVD_HOME/${ANDROID_AVD_NAME}.avd"
else
	avd_tmp="$BUILD_DIR/android-avd-tmp"
	rm -rf "$avd_tmp"
	mkdir -p "$avd_tmp"
	ANDROID_AVD_HOME="$ANDROID_AVD_HOME" HOME="$avd_tmp" \
		sh -c "printf 'no\\n' | '$AVDMANAGER' create avd --force --name '$ANDROID_AVD_NAME' --package '$SYSTEM_IMAGE_PACKAGE'"
	rm -rf "$avd_tmp"
fi

if [ -e /dev/kvm ]; then
	printf '%s\n' "setup-android-emulator: /dev/kvm is present for hardware acceleration"
else
	printf '%s\n' "setup-android-emulator: /dev/kvm is not present; emulator may be slow" >&2
fi

printf '%s\n' "setup-android-emulator: AVD name: $ANDROID_AVD_NAME"
printf '%s\n' "setup-android-emulator: AVD home: $ANDROID_AVD_HOME"
printf '%s\n' "setup-android-emulator: start it with: make android-emulator"
