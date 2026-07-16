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

    static native void nativeSetRuntimeMetrics(long handle, float cpuPercent, float ramMb);

    static native void nativeRender(long handle, Bitmap bitmap, float elapsedSeconds, float snapshotAgeSeconds);

    static native void nativeDestroy(long handle);
}
