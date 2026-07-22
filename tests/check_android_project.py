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
    android_profile_script = (ROOT / "scripts" / "profile_android_app.sh").read_text(encoding="utf-8")
    android_audio_status_script = (ROOT / "scripts" / "android_audio_status.sh").read_text(encoding="utf-8")
    native_cmake = (ROOT / "android" / "app" / "src" / "main" / "cpp" / "CMakeLists.txt").read_text(
        encoding="utf-8"
    )
    bridge = (ROOT / "android" / "app" / "src" / "main" / "cpp" / "android_bridge.cpp").read_text(
        encoding="utf-8"
    )
    activity = (
        ROOT / "android" / "app" / "src" / "main" / "java" / "dev" / "benalu" / "musicanalyzer" / "MainActivity.java"
    ).read_text(encoding="utf-8")
    manifest = (ROOT / "android" / "app" / "src" / "main" / "AndroidManifest.xml").read_text(encoding="utf-8")
    native_api = (
        ROOT / "android" / "app" / "src" / "main" / "java" / "dev" / "benalu" / "musicanalyzer" /
        "MusicAnalyzerNative.java"
    ).read_text(encoding="utf-8")
    external_devices = (
        ROOT / "android" / "app" / "src" / "main" / "java" / "dev" / "benalu" / "musicanalyzer" /
        "ExternalDeviceManager.java"
    ).read_text(encoding="utf-8")
    fret_control = (ROOT / "src" / "fret_control.cpp").read_text(encoding="utf-8")
    external_control_docs = (ROOT / "docs" / "external_fret_control.md").read_text(encoding="utf-8")

    require("productFlavors" in app_gradle, "Android app must define product flavors")
    require("complete" in app_gradle, "complete Android flavor missing")
    require("bassGuitar" in app_gradle, "bassGuitar Android flavor missing")
    require('namespace "dev.benalu.musicanalyzer"' in app_gradle and
            'applicationId "dev.benalu.musicanalyzer"' in app_gradle,
            "Android package namespace must use dev.benalu.musicanalyzer")
    require("bass-guitar" in app_gradle, "bass-guitar layout build config missing")
    require("MAO_LAYOUT" in app_gradle, "complete layout build config missing")
    require('ndkVersion "27.2.12479018"' in app_gradle, "Android app must pin the setup NDK version")
    require("sourceCompatibility JavaVersion.VERSION_17" in app_gradle and
            "targetCompatibility JavaVersion.VERSION_17" in app_gradle,
            "Android app must compile Java without obsolete source/target warnings")
    require("android.javaCompile.suppressSourceTargetDeprecationWarning=true" in gradle_properties,
            "Android Gradle Java source/target deprecation warning must be suppressed")

    require("setup-android:" in makefile, "Makefile setup-android target missing")
    require("setup-android-emulator:" in makefile, "Makefile setup-android-emulator target missing")
    require("android-emulator:" in makefile, "Makefile android-emulator target missing")
    require("android-emulator-stop:" in makefile, "Makefile android-emulator-stop target missing")
    require("android-stop-apps:" in makefile, "Makefile android-stop-apps target missing")
    require("android-uninstall-old-packages:" in makefile,
            "Makefile android-uninstall-old-packages target missing")
    require("dev.kyz.musicanalyzer" in makefile,
            "android-stop-apps must stop old package ids during the namespace migration")
    require("emu kill" in makefile, "Makefile must close the emulator through adb emu kill")
    require("android-profile:" in makefile and "android-profile-complete:" in makefile and
            "android-profile-bass-guitar:" in makefile and "scripts/profile_android_app.sh" in makefile,
            "Makefile android-profile target missing")
    require("ANDROID_PROFILE_PACKAGE ?= dev.benalu.musicanalyzer.bassguitar" in makefile,
            "Makefile android-profile must default to the bass-guitar package")
    require("android-audio-status:" in makefile and "scripts/android_audio_status.sh" in makefile,
            "Makefile android-audio-status target missing")
    require("android-route-desktop-audio:" in makefile, "Makefile android-route-desktop-audio target missing")
    require("android-route-desktop-audio-watch:" in makefile,
            "Makefile android-route-desktop-audio-watch target missing")
    require("--watch" in makefile, "Makefile must expose persistent Android audio routing")
    require("android-install-bass-guitar:" in makefile, "Makefile android-install-bass-guitar target missing")
    require("android-run-bass-guitar:" in makefile, "Makefile android-run-bass-guitar target missing")
    require("dev.benalu.musicanalyzer.bassguitar" in makefile,
            "Makefile must launch bass-guitar Android package")
    require("android-grant-permissions:" in makefile and "pm grant" in makefile and
            "android.permission.RECORD_AUDIO" in makefile and "android.permission.BLUETOOTH_SCAN" in makefile and
            "android.permission.BLUETOOTH_CONNECT" in makefile,
            "Makefile must expose and use Android microphone/BLE permission grants")
    require("am force-stop dev.benalu.musicanalyzer.complete" in makefile and
            "am force-stop dev.benalu.musicanalyzer.bassguitar" in makefile,
            "Makefile must stop the other Android flavor before launching")
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
    require("/proc/stat" in android_profile_script and "dumpsys meminfo" in android_profile_script,
            "android-profile must report app CPU and memory through adb")
    require("dumpsys audio" in android_audio_status_script and "logcat" in android_audio_status_script and
            "pactl list sink-inputs" in android_audio_status_script and
            "pactl list source-outputs" in android_audio_status_script,
            "android-audio-status must report Android and host capture routing")

    require("src/analyzer.cpp" in native_cmake, "Android native target must use shared analyzer.cpp")
    require("src/visualizer_renderer.cpp" in native_cmake, "Android native target must use shared renderer.cpp")
    require("src/fret_control.cpp" in native_cmake, "Android native target must use shared fret control")
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
    require("isProbablyEmulator" in activity and "AudioSource.DEFAULT" in activity and
            "AudioSource.MIC" in activity,
            "Android app must use emulator-friendly capture sources before UNPROCESSED on emulators")
    require("GET_DEVICES_INPUTS" in activity and "setPreferredDevice(inputChoice.device)" in activity,
            "Android app must enumerate and select input devices such as USB audio interfaces")
    require("cycleInputDevice" in activity and "KEYCODE_SPACE" in activity and "setOnClickListener" in activity,
            "Android app must expose input-device cycling through keyboard and touch")
    require("nativeSetSourceName" in activity and "nativeSetSourceName" in bridge,
            "Android selected input label must flow into the shared renderer")
    require("using AudioRecord source" in activity and "capture source=" in activity,
            "Android app must log capture source and capture RMS/peak in debug builds")
    require("Process.getElapsedCpuTime()" in activity, "Android app must sample app process CPU usage")
    require("readTotalCpu" not in activity and "/proc/stat" not in activity,
            "Android app must not rely on restricted /proc/stat for on-screen CPU")
    require("Debug.getPss()" in activity, "Android app must sample app RAM usage")
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
    require("std::vector<float> local" not in bridge and "std::vector<float> samples" not in bridge,
            "Android JNI audio push must avoid per-callback temporary vectors")
    require("std::array<float, mao::kAnalysisWindow> ring" in bridge and "analysis_window" in bridge,
            "Android JNI audio buffer must use preallocated ring and analysis-window storage")
    require("decimation_factor" in bridge and "decimated_buffer.resize" in bridge,
            "Android analyzer must preallocate and use decimated analysis input")
    require("analysis_interval_seconds = 0.10f" in bridge,
            "Android analyzer must use the lower-CPU 100 ms analysis hop")
    require("kAndroidIdleAnalysisSeconds" in bridge and "should_skip_silent_analysis" in bridge,
            "Android analyzer must throttle expensive analysis during sustained silence")
    require("append_visualizer_drum_hits(&state->renderer" not in bridge.split("nativePushSamples", 1)[1].split(
        "nativeSetRuntimeMetrics", 1)[0],
            "Android audio thread must not mutate renderer state")
    require("snapshot_mutex" in bridge and "std::atomic<float>" in bridge,
            "Android renderer must copy snapshots without blocking audio analysis")
    require("nativeHandleApcPad" in bridge and "apc_action_for_pad" in bridge,
            "Android JNI must route APC pads through the shared control map")
    require("nativeHandleMvaveSwitch" in bridge and "mvave_action_for_switch" in bridge,
            "Android JNI must route M-VAVE press/hold actions through the shared control map")
    require("nativeGetLiteJamPacket" in bridge and "nativeGetFretZealotPacket" in bridge and
            "nativeGetApcLedMessages" in bridge,
            "Android JNI must expose all external-device output encoders")

    require("android.permission.BLUETOOTH_SCAN" in manifest and
            "android.permission.BLUETOOTH_CONNECT" in manifest,
            "Android manifest must request modern BLE scan/connect permissions")
    require("android.software.midi" in manifest and "android.hardware.bluetooth_le" in manifest,
            "Android manifest must declare optional MIDI and BLE features")
    require("ExternalDeviceManager" in activity and "setOnLongClickListener" in activity and
            "nativeToggleAutoconnect" in activity,
            "Android activity must own device discovery and expose the autoconnect toggle")
    require("BLUETOOTH_SCAN" in activity and "BLUETOOTH_CONNECT" in activity,
            "Android activity must request runtime BLE permissions")
    require("nativeGetControlRevision" in native_api and "nativeSetDeviceState" in native_api,
            "Android native API must expose synchronized external control state")

    require("Lite Jam RGB".lower() in external_devices.lower() and
            "0000ee04-0000-1000-8000-00805f9b34fb" in external_devices and
            "WRITE_TYPE_NO_RESPONSE" in external_devices,
            "Android BLE manager must discover and write LiteJam LEDs without response")
    require("6e400002-b5a3-f393-e0a9-e50e24dcca9e" in external_devices and
            "fb1e4002-54ae-4a28-9f74-dfccb248601d" in external_devices,
            "Android BLE manager must support both Fret Zealot write characteristics")
    require("openBluetoothDevice" in external_devices and "openOutputPort" in external_devices and
            "openInputPort" in external_devices,
            "Android MIDI manager must support BLE MIDI, controller input, and APC LED output")
    require("MVAVE_HOLD_MILLIS" in external_devices and "mvaveRelease" in external_devices,
            "M-VAVE handling must distinguish short releases from holds")
    require("kMajorColors" in fret_control and "build_litejam_major_scale_packet" in fret_control and
            "build_fret_zealot_major_scale_packet" in fret_control and "build_apc_led_messages" in fret_control,
            "shared fret control must contain rainbow scale and APC output encoders")
    require("CubeSuite" in external_control_docs and "Note On" in external_control_docs and
            "Long-press" in external_control_docs,
            "external control documentation must cover M-VAVE setup and autoconnect UI")

    print("check_android_project: ok")


if __name__ == "__main__":
    main()
