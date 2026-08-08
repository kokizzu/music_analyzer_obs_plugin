package dev.benalu.musicanalyzer;

import android.graphics.Bitmap;

final class MusicAnalyzerNative {
    static {
        System.loadLibrary("music_analyzer_android");
    }

    private MusicAnalyzerNative() {
    }

    static native long nativeCreate(int sampleRate, int width, int height, boolean bassGuitar);

    static native void nativeSetSourceName(long handle, String sourceName);

    static native boolean nativePushSamples(long handle, float[] samples, int length);

    static native void nativeSetRuntimeMetrics(long handle, float cpuPercent, float ramMb, float batteryPercent,
            boolean batteryCharging);

    static native boolean nativeApplyControlAction(long handle, int actionKind, int value);

    static native boolean nativeSetManualRoot(long handle, int pitchClass);

    static native boolean nativeHandleApcPad(long handle, int note, int velocity);

    static native boolean nativeHandleMvaveSwitch(long handle, int switchIndex, boolean held);

    static native void nativeSetDeviceState(long handle, int device, int connectionState);

    static native boolean nativeSetAutoconnect(long handle, boolean enabled);

    static native boolean nativeToggleAutoconnect(long handle);

    static native int nativeTouchTarget(long handle, int x, int y);

    static native long nativeGetControlRevision(long handle);

    static native boolean nativeIsAutomaticRootMode(long handle);

    static native byte[] nativeGetApcLedMessages(long handle);

    static native byte[] nativeGetLiteJamPacket(long handle);

    static native byte[] nativeGetFretZealotPacket(long handle);

    static native void nativeRender(long handle, Bitmap bitmap, float elapsedSeconds, float snapshotAgeSeconds);

    static native void nativeDestroy(long handle);
}
