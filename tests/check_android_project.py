#!/usr/bin/env python3

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise SystemExit(f"check_android_project: {message}")


def main():
    app_gradle = (ROOT / "android" / "app" / "build.gradle").read_text(encoding="utf-8")
    gradle_properties = (ROOT / "android" / "gradle.properties").read_text(encoding="utf-8")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    setup_script = (ROOT / "scripts" / "setup_android.sh").read_text(encoding="utf-8")
    emulator_setup_script = (ROOT / "scripts" / "setup_android_emulator.sh").read_text(encoding="utf-8")
    route_audio_script = (ROOT / "scripts" / "route_android_emulator_audio.sh").read_text(encoding="utf-8")
    native_cmake = (ROOT / "android" / "app" / "src" / "main" / "cpp" / "CMakeLists.txt").read_text(
        encoding="utf-8"
    )
    bridge = (ROOT / "android" / "app" / "src" / "main" / "cpp" / "android_bridge.cpp").read_text(
        encoding="utf-8"
    )
    activity = (
        ROOT / "android" / "app" / "src" / "main" / "java" / "dev" / "kyz" / "musicanalyzer" / "MainActivity.java"
    ).read_text(encoding="utf-8")

    require("productFlavors" in app_gradle, "Android app must define product flavors")
    require("complete" in app_gradle, "complete Android flavor missing")
    require("bassGuitar" in app_gradle, "bassGuitar Android flavor missing")
    require("bass-guitar" in app_gradle, "bass-guitar layout build config missing")
    require("MAO_LAYOUT" in app_gradle, "complete layout build config missing")
    require('ndkVersion "27.2.12479018"' in app_gradle, "Android app must pin the setup NDK version")
    require("android.javaCompile.suppressSourceTargetDeprecationWarning=true" in gradle_properties,
            "Android Gradle Java source/target deprecation warning must be suppressed")

    require("setup-android:" in makefile, "Makefile setup-android target missing")
    require("setup-android-emulator:" in makefile, "Makefile setup-android-emulator target missing")
    require("android-emulator:" in makefile, "Makefile android-emulator target missing")
    require("android-emulator-stop:" in makefile, "Makefile android-emulator-stop target missing")
    require("emu kill" in makefile, "Makefile must close the emulator through adb emu kill")
    require("android-route-desktop-audio:" in makefile, "Makefile android-route-desktop-audio target missing")
    require("android-route-desktop-audio-watch:" in makefile,
            "Makefile android-route-desktop-audio-watch target missing")
    require("--watch" in makefile, "Makefile must expose persistent Android audio routing")
    require("android-install-bass-guitar:" in makefile, "Makefile android-install-bass-guitar target missing")
    require("android-run-bass-guitar:" in makefile, "Makefile android-run-bass-guitar target missing")
    require("dev.kyz.musicanalyzer.bassguitar" in makefile,
            "Makefile must launch bass-guitar Android package")
    require("install -r" in makefile and "BASS_GUITAR_APK" in makefile,
            "Makefile must install Android APKs with adb install -r")
    require("monkey -p" in makefile, "Makefile must launch Android apps through monkey")
    require("android-complete:" in makefile, "Makefile android-complete target missing")
    require("android-bass-guitar:" in makefile, "Makefile android-bass-guitar target missing")
    require("ANDROID_SDK_ROOT" in makefile, "Makefile Android SDK root missing")
    require("ANDROID_AVD_HOME" in makefile, "Makefile Android AVD home missing")
    require("ANDROID_GRADLE_VERSION" in makefile, "Makefile Android Gradle version missing")

    require("sdkmanager" in setup_script, "setup-android must install SDK packages with sdkmanager")
    require("android_sdk_packages_installed" in setup_script,
            "setup-android must check installed SDK packages before sdkmanager")
    require("skipping sdkmanager" in setup_script,
            "setup-android must skip sdkmanager when required packages are already installed")
    require("ndk;" in setup_script, "setup-android must install NDK")
    require("cmake;" in setup_script, "setup-android must install Android CMake")
    require("gradle-" in setup_script, "setup-android must install local Gradle")
    require("ANDROID_JDK_HOME" in setup_script, "setup-android must configure a local JDK fallback")
    require("api.adoptium.net" in setup_script, "setup-android must be able to download JDK 17")
    require("org.gradle.java.home" in setup_script, "setup-android must write Gradle Java home when needed")
    require("android/local.properties" in setup_script, "setup-android must write Android local.properties")

    require('"emulator"' in emulator_setup_script, "setup-android-emulator must install emulator package")
    require("system-images;android-" in emulator_setup_script,
            "setup-android-emulator must install an Android system image")
    require("emulator_packages_installed" in emulator_setup_script,
            "setup-android-emulator must check installed emulator packages before sdkmanager")
    require("skipping sdkmanager" in emulator_setup_script,
            "setup-android-emulator must skip sdkmanager when emulator packages are installed")
    require("avdmanager" in emulator_setup_script, "setup-android-emulator must create an AVD")
    require("ANDROID_AVD_HOME" in emulator_setup_script, "setup-android-emulator must keep AVD files local")
    require("/dev/kvm" in emulator_setup_script, "setup-android-emulator must report KVM availability")

    require("pactl get-default-sink" in route_audio_script,
            "android-route-desktop-audio must default to the current desktop sink monitor")
    require("move-source-output" in route_audio_script,
            "android-route-desktop-audio must move emulator recording streams")
    require("--watch" in route_audio_script, "android-route-desktop-audio must support persistent routing")
    require("ANDROID_ROUTE_INTERVAL" in route_audio_script,
            "android-route-desktop-audio watch interval must be configurable")
    require("Source:" in route_audio_script,
            "android-route-desktop-audio must check the current source before moving streams")
    require("ANDROID_MIC_SOURCE" in route_audio_script,
            "android-route-desktop-audio must allow explicit source override")
    require("qemu-system" in route_audio_script,
            "android-route-desktop-audio must target Android emulator recording streams")

    require("src/analyzer.cpp" in native_cmake, "Android native target must use shared analyzer.cpp")
    require("src/visualizer_renderer.cpp" in native_cmake, "Android native target must use shared renderer.cpp")
    require("android_bridge.cpp" in native_cmake, "Android native bridge missing from native target")
    require("jnigraphics" in native_cmake, "Android native target must link jnigraphics for AndroidBitmap")
    require("SDL" not in native_cmake, "Android target must not use SDL")

    require("AnalysisInputMode::FullMix" in bridge, "Android analyzer must use FullMix mode")
    require("VisualizerLayoutMode::BassGuitar" in bridge, "Android bridge must expose bass-guitar layout")
    require("render_visualizer" in bridge, "Android bridge must render through shared renderer")
    require("advance_visualizer_drum_history" in bridge, "Android bridge must advance shared drum history")

    require("AudioRecord" in activity, "Android app must capture device audio input")
    require("AudioSource.UNPROCESSED" in activity,
            "Android app must prefer unprocessed audio capture for music analysis")
    require("/proc/stat" in activity, "Android app must sample total CPU usage")
    require("ActivityManager.MemoryInfo" in activity, "Android app must sample free memory")
    require("nativeSetRuntimeMetrics" in activity and "nativeSetRuntimeMetrics" in bridge,
            "Android runtime metrics must flow into the shared renderer")
    require("postInvalidateDelayed" in activity, "Android rendering must be frame-rate bounded")
    require("420 : 540" in activity, "Android compact layout height must match the shared renderer")
    require("AudioTrack" in activity, "Android app must explicitly monitor input to an output device")
    require("GET_DEVICES_OUTPUTS" in activity, "Android app must inspect output devices before monitoring")
    require("setPreferredDevice" in activity, "Android app must route monitor audio to the chosen output")
    require("WRITE_NON_BLOCKING" in activity, "Android app must write monitor audio without blocking analysis")
    require("TYPE_BUILTIN_SPEAKER" not in activity, "Android app must not intentionally monitor through speaker")
    require("BuildConfig.MAO_LAYOUT" in activity, "Android app must select layout from flavor")
    require("setKeepScreenOn(true)" in activity, "Android app must keep the analyzer screen awake")
    require("postInvalidateOnAnimation" in activity, "Android app must repaint continuously while running")
    require("std::vector<float> local" not in bridge,
            "Android JNI audio push must avoid per-callback temporary vectors")
    require("input_buffer" in bridge and "std::memmove" in bridge,
            "Android JNI audio buffer must reuse storage and compact without front erases")

    print("check_android_project: ok")


if __name__ == "__main__":
    main()
