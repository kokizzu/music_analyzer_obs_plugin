#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
BUILD_DIR=${BUILD_DIR:-"$ROOT_DIR/build"}
ANDROID_SDK_ROOT=${ANDROID_SDK_ROOT:-"$BUILD_DIR/android-sdk"}
ANDROID_CMDLINE_TOOLS_VERSION=${ANDROID_CMDLINE_TOOLS_VERSION:-11076708}
ANDROID_GRADLE_VERSION=${ANDROID_GRADLE_VERSION:-8.10.2}
ANDROID_JDK_HOME=${ANDROID_JDK_HOME:-"$BUILD_DIR/jdk-17"}
ANDROID_COMPILE_SDK=${ANDROID_COMPILE_SDK:-35}
ANDROID_BUILD_TOOLS_VERSION=${ANDROID_BUILD_TOOLS_VERSION:-35.0.0}
ANDROID_NDK_VERSION=${ANDROID_NDK_VERSION:-27.2.12479018}
ANDROID_CMAKE_VERSION=${ANDROID_CMAKE_VERSION:-3.22.1}
PYTHON=${PYTHON:-python3}
CURL=${CURL:-curl}
TAR=${TAR:-tar}

GRADLE_DIR="$BUILD_DIR/gradle"
GRADLE_HOME="$GRADLE_DIR/gradle-$ANDROID_GRADLE_VERSION"
CMDLINE_ROOT="$ANDROID_SDK_ROOT/cmdline-tools/latest"
DOWNLOAD_DIR="$BUILD_DIR/android-downloads"

require_command() {
	if ! command -v "$1" >/dev/null 2>&1; then
		printf '%s\n' "setup-android: missing required command: $1" >&2
		exit 1
	fi
}

extract_zip() {
	zip_file=$1
	destination=$2
	"$PYTHON" -m zipfile -e "$zip_file" "$destination"
}

android_sdk_packages_installed() {
	[ -x "$ANDROID_SDK_ROOT/platform-tools/adb" ] &&
		[ -f "$ANDROID_SDK_ROOT/platforms/android-$ANDROID_COMPILE_SDK/android.jar" ] &&
		{ [ -x "$ANDROID_SDK_ROOT/build-tools/$ANDROID_BUILD_TOOLS_VERSION/aapt" ] ||
			[ -x "$ANDROID_SDK_ROOT/build-tools/$ANDROID_BUILD_TOOLS_VERSION/aapt2" ]; } &&
		[ -f "$ANDROID_SDK_ROOT/ndk/$ANDROID_NDK_VERSION/source.properties" ] &&
		[ -x "$ANDROID_SDK_ROOT/cmake/$ANDROID_CMAKE_VERSION/bin/cmake" ]
}

require_command "$PYTHON"
require_command "$CURL"

mkdir -p "$ANDROID_SDK_ROOT" "$GRADLE_DIR" "$DOWNLOAD_DIR"

java_major_version() {
	if ! command -v "$1" >/dev/null 2>&1; then
		return 1
	fi
	"$1" -version 2>&1 | awk -F'[."]' '/version/ { if ($2 == "1") print $3; else print $2; exit }'
}

java_is_17_or_newer() {
	major=$(java_major_version "$1" || true)
	if [ -z "$major" ]; then
		return 1
	fi
	[ "$major" -ge 17 ] 2>/dev/null
}

setup_java() {
	if [ -x "$ANDROID_JDK_HOME/bin/java" ] && java_is_17_or_newer "$ANDROID_JDK_HOME/bin/java"; then
		JAVA_HOME=$ANDROID_JDK_HOME
		export JAVA_HOME
		PATH="$JAVA_HOME/bin:$PATH"
		export PATH
		return 0
	fi

	if java_is_17_or_newer java; then
		return 0
	fi

	require_command "$TAR"
	case "$(uname -m)" in
		x86_64|amd64)
			jdk_arch=x64
			;;
		aarch64|arm64)
			jdk_arch=aarch64
			;;
		*)
			printf '%s\n' "setup-android: unsupported JDK architecture: $(uname -m)" >&2
			exit 1
			;;
	esac

	jdk_archive="$DOWNLOAD_DIR/temurin-jdk17-linux-${jdk_arch}.tar.gz"
	jdk_tmp="$DOWNLOAD_DIR/jdk"
	rm -rf "$jdk_tmp"
	mkdir -p "$jdk_tmp"
	if [ ! -f "$jdk_archive" ]; then
		"$CURL" -fL --retry 3 \
			-o "$jdk_archive" \
			"https://api.adoptium.net/v3/binary/latest/17/ga/linux/${jdk_arch}/jdk/hotspot/normal/eclipse"
	fi
	"$TAR" -xzf "$jdk_archive" -C "$jdk_tmp"
	jdk_extracted=
	for candidate in "$jdk_tmp"/*; do
		if [ -d "$candidate" ]; then
			jdk_extracted=$candidate
			break
		fi
	done
	if [ -z "$jdk_extracted" ]; then
		printf '%s\n' "setup-android: downloaded JDK archive did not contain a directory" >&2
		exit 1
	fi
	rm -rf "$ANDROID_JDK_HOME"
	mv "$jdk_extracted" "$ANDROID_JDK_HOME"
	JAVA_HOME=$ANDROID_JDK_HOME
	export JAVA_HOME
	PATH="$JAVA_HOME/bin:$PATH"
	export PATH
}

setup_java

if [ ! -x "$CMDLINE_ROOT/bin/sdkmanager" ]; then
	cmdline_zip="$DOWNLOAD_DIR/commandlinetools-linux-${ANDROID_CMDLINE_TOOLS_VERSION}.zip"
	cmdline_tmp="$DOWNLOAD_DIR/cmdline-tools"
	rm -rf "$cmdline_tmp"
	mkdir -p "$cmdline_tmp"
	if [ ! -f "$cmdline_zip" ]; then
		"$CURL" -fL --retry 3 \
			-o "$cmdline_zip" \
			"https://dl.google.com/android/repository/commandlinetools-linux-${ANDROID_CMDLINE_TOOLS_VERSION}_latest.zip"
	fi
	extract_zip "$cmdline_zip" "$cmdline_tmp"
	rm -rf "$CMDLINE_ROOT"
	mkdir -p "$ANDROID_SDK_ROOT/cmdline-tools"
	mv "$cmdline_tmp/cmdline-tools" "$CMDLINE_ROOT"
fi

if [ -d "$CMDLINE_ROOT/bin" ]; then
	chmod +x "$CMDLINE_ROOT"/bin/* 2>/dev/null || true
fi

SDKMANAGER="$CMDLINE_ROOT/bin/sdkmanager"
if [ ! -x "$SDKMANAGER" ]; then
	printf '%s\n' "setup-android: sdkmanager was not installed at $SDKMANAGER" >&2
	exit 1
fi

if android_sdk_packages_installed; then
	printf '%s\n' "setup-android: Android SDK packages already installed; skipping sdkmanager"
else
	yes | "$SDKMANAGER" --sdk_root="$ANDROID_SDK_ROOT" --licenses >/dev/null 2>&1 || true
	yes | "$SDKMANAGER" --sdk_root="$ANDROID_SDK_ROOT" \
		"platform-tools" \
		"platforms;android-$ANDROID_COMPILE_SDK" \
		"build-tools;$ANDROID_BUILD_TOOLS_VERSION" \
		"ndk;$ANDROID_NDK_VERSION" \
		"cmake;$ANDROID_CMAKE_VERSION"
fi

if [ ! -x "$GRADLE_HOME/bin/gradle" ]; then
	gradle_zip="$DOWNLOAD_DIR/gradle-${ANDROID_GRADLE_VERSION}-bin.zip"
	gradle_tmp="$DOWNLOAD_DIR/gradle"
	rm -rf "$gradle_tmp"
	mkdir -p "$gradle_tmp"
	if [ ! -f "$gradle_zip" ]; then
		"$CURL" -fL --retry 3 \
			-o "$gradle_zip" \
			"https://services.gradle.org/distributions/gradle-${ANDROID_GRADLE_VERSION}-bin.zip"
	fi
	extract_zip "$gradle_zip" "$gradle_tmp"
	rm -rf "$GRADLE_HOME"
	mv "$gradle_tmp/gradle-$ANDROID_GRADLE_VERSION" "$GRADLE_HOME"
fi

if [ -d "$GRADLE_HOME/bin" ]; then
	chmod +x "$GRADLE_HOME"/bin/* 2>/dev/null || true
fi

cat >"$ROOT_DIR/android/local.properties" <<EOF
sdk.dir=$ANDROID_SDK_ROOT
EOF

if [ -n "${JAVA_HOME:-}" ] && [ -x "$JAVA_HOME/bin/java" ]; then
	cat >"$ROOT_DIR/android/gradle.properties" <<EOF
org.gradle.java.home=$JAVA_HOME
EOF
fi

printf '%s\n' "setup-android: installed Android SDK at $ANDROID_SDK_ROOT"
printf '%s\n' "setup-android: installed Gradle at $GRADLE_HOME"
if [ -n "${JAVA_HOME:-}" ]; then
	printf '%s\n' "setup-android: using Java at $JAVA_HOME"
fi
printf '%s\n' "setup-android: build complete APK: make android-complete"
printf '%s\n' "setup-android: build bass+guitar APK: make android-bass-guitar"
