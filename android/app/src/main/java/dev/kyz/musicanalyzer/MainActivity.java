package dev.kyz.musicanalyzer;

import android.Manifest;
import android.app.ActivityManager;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.media.AudioAttributes;
import android.media.AudioDeviceInfo;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioRecord;
import android.media.AudioTrack;
import android.media.MediaRecorder;
import android.os.Build;
import android.os.Bundle;
import android.os.Process;
import android.view.View;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

public final class MainActivity extends Activity {
    private static final int REQUEST_RECORD_AUDIO = 10;
    private static final int SAMPLE_RATE = 48000;
    private static final long METRICS_INTERVAL_NANOS = 1_000_000_000L;
    private static final long ACTIVE_FRAME_DELAY_MS = 33;
    private static final long IDLE_FRAME_DELAY_MS = 120;

    private AnalyzerView analyzerView;
    private volatile boolean running;
    private Thread audioThread;
    private long nativeHandle;
    private long lastAnalysisNanos;
    private long lastMetricsNanos;
    private long[] lastCpuTicks;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        boolean bassGuitar = "bass-guitar".equals(BuildConfig.MAO_LAYOUT);
        int width = bassGuitar ? 960 : 960;
        int height = bassGuitar ? 420 : 540;
        nativeHandle = MusicAnalyzerNative.nativeCreate(SAMPLE_RATE, width, height, bassGuitar);
        lastAnalysisNanos = System.nanoTime();
        lastMetricsNanos = 0;
        analyzerView = new AnalyzerView(this, width, height);
        analyzerView.setKeepScreenOn(true);
        setContentView(analyzerView);

        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
            startAudio();
        } else {
            requestPermissions(new String[] {Manifest.permission.RECORD_AUDIO}, REQUEST_RECORD_AUDIO);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_RECORD_AUDIO && grantResults.length > 0
                && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            startAudio();
        }
    }

    @Override
    protected void onDestroy() {
        stopAudio();
        if (nativeHandle != 0) {
            MusicAnalyzerNative.nativeDestroy(nativeHandle);
            nativeHandle = 0;
        }
        super.onDestroy();
    }

    private void startAudio() {
        if (running) {
            return;
        }
        running = true;
        audioThread = new Thread(this::captureAudio, "MusicAnalyzerAudio");
        audioThread.start();
    }

    private void stopAudio() {
        running = false;
        if (audioThread != null) {
            try {
                audioThread.join(800);
            } catch (InterruptedException ignored) {
                Thread.currentThread().interrupt();
            }
            audioThread = null;
        }
    }

    private static float clampPercent(float value) {
        if (!Float.isFinite(value)) {
            return -1.0f;
        }
        return Math.max(0.0f, Math.min(100.0f, value));
    }

    private long[] readTotalCpuTicks() {
        try (BufferedReader reader = new BufferedReader(new FileReader("/proc/stat"))) {
            String line = reader.readLine();
            if (line == null || !line.startsWith("cpu ")) {
                return null;
            }
            String[] parts = line.trim().split("\\s+");
            if (parts.length < 5) {
                return null;
            }
            long total = 0;
            for (int i = 1; i < parts.length; i++) {
                total += Long.parseLong(parts[i]);
            }
            long idle = Long.parseLong(parts[4]);
            if (parts.length > 5) {
                idle += Long.parseLong(parts[5]);
            }
            return new long[] {total, idle};
        } catch (IOException | NumberFormatException ignored) {
            return null;
        }
    }

    private float readTotalCpuPercent() {
        long[] ticks = readTotalCpuTicks();
        if (ticks == null) {
            return -1.0f;
        }
        if (lastCpuTicks == null) {
            lastCpuTicks = ticks;
            return -1.0f;
        }

        long totalDelta = ticks[0] - lastCpuTicks[0];
        long idleDelta = ticks[1] - lastCpuTicks[1];
        lastCpuTicks = ticks;
        if (totalDelta <= 0) {
            return -1.0f;
        }
        return clampPercent(((float) (totalDelta - idleDelta) * 100.0f) / (float) totalDelta);
    }

    private float readFreeMemoryPercent() {
        ActivityManager activityManager = getSystemService(ActivityManager.class);
        if (activityManager == null) {
            return -1.0f;
        }
        ActivityManager.MemoryInfo info = new ActivityManager.MemoryInfo();
        activityManager.getMemoryInfo(info);
        if (info.totalMem <= 0) {
            return -1.0f;
        }
        return clampPercent(((float) info.availMem * 100.0f) / (float) info.totalMem);
    }

    private void updateRuntimeMetrics(long nowNanos) {
        if (nativeHandle == 0 || nowNanos - lastMetricsNanos < METRICS_INTERVAL_NANOS) {
            return;
        }
        lastMetricsNanos = nowNanos;
        MusicAnalyzerNative.nativeSetRuntimeMetrics(
                nativeHandle,
                readTotalCpuPercent(),
                readFreeMemoryPercent());
    }

    private AudioRecord createAudioRecord(int minBuffer, int bufferFrames) {
        int bufferBytes = Math.max(minBuffer, bufferFrames * 4);
        int[] sources = Build.VERSION.SDK_INT >= Build.VERSION_CODES.N
                ? new int[] {MediaRecorder.AudioSource.UNPROCESSED, MediaRecorder.AudioSource.DEFAULT}
                : new int[] {MediaRecorder.AudioSource.DEFAULT};
        for (int source : sources) {
            try {
                AudioRecord recorder = new AudioRecord(
                        source,
                        SAMPLE_RATE,
                        AudioFormat.CHANNEL_IN_MONO,
                        AudioFormat.ENCODING_PCM_FLOAT,
                        bufferBytes);
                if (recorder.getState() == AudioRecord.STATE_INITIALIZED) {
                    return recorder;
                }
                recorder.release();
            } catch (IllegalArgumentException | UnsupportedOperationException ignored) {
            }
        }
        return null;
    }

    private AudioDeviceInfo chooseMonitorOutputDevice() {
        AudioManager audioManager = getSystemService(AudioManager.class);
        if (audioManager == null) {
            return null;
        }

        AudioDeviceInfo fallback = null;
        for (AudioDeviceInfo device : audioManager.getDevices(AudioManager.GET_DEVICES_OUTPUTS)) {
            switch (device.getType()) {
                case AudioDeviceInfo.TYPE_USB_DEVICE:
                case AudioDeviceInfo.TYPE_USB_HEADSET:
                case AudioDeviceInfo.TYPE_WIRED_HEADPHONES:
                case AudioDeviceInfo.TYPE_WIRED_HEADSET:
                case AudioDeviceInfo.TYPE_LINE_ANALOG:
                    return device;
                case AudioDeviceInfo.TYPE_BLUETOOTH_A2DP:
                case AudioDeviceInfo.TYPE_BLUETOOTH_SCO:
                case AudioDeviceInfo.TYPE_HDMI:
                    if (fallback == null) {
                        fallback = device;
                    }
                    break;
                default:
                    break;
            }
        }
        return fallback;
    }

    private AudioTrack createMonitorTrack(int bufferFrames) {
        AudioDeviceInfo outputDevice = chooseMonitorOutputDevice();
        if (outputDevice == null) {
            return null;
        }

        int minBuffer = AudioTrack.getMinBufferSize(
                SAMPLE_RATE,
                AudioFormat.CHANNEL_OUT_MONO,
                AudioFormat.ENCODING_PCM_FLOAT);
        if (minBuffer <= 0) {
            return null;
        }

        try {
            AudioFormat format = new AudioFormat.Builder()
                    .setSampleRate(SAMPLE_RATE)
                    .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                    .setEncoding(AudioFormat.ENCODING_PCM_FLOAT)
                    .build();
            AudioAttributes attributes = new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_MEDIA)
                    .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                    .build();
            AudioTrack track = new AudioTrack.Builder()
                    .setAudioAttributes(attributes)
                    .setAudioFormat(format)
                    .setBufferSizeInBytes(Math.max(minBuffer, bufferFrames * 4 * 2))
                    .setTransferMode(AudioTrack.MODE_STREAM)
                    .build();
            if (!track.setPreferredDevice(outputDevice)) {
                track.release();
                return null;
            }
            track.play();
            return track;
        } catch (RuntimeException ignored) {
            return null;
        }
    }

    private void captureAudio() {
        Process.setThreadPriority(Process.THREAD_PRIORITY_AUDIO);
        int minBuffer = AudioRecord.getMinBufferSize(
                SAMPLE_RATE,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_FLOAT);
        if (minBuffer <= 0) {
            return;
        }
        int bufferFrames = Math.max(1024, minBuffer / 4);
        AudioRecord recorder = null;
        AudioTrack monitor = null;
        try {
            recorder = createAudioRecord(minBuffer, bufferFrames);
            if (recorder == null) {
                running = false;
                return;
            }
            monitor = createMonitorTrack(bufferFrames);
            recorder.startRecording();
            float[] samples = new float[bufferFrames];
            while (running) {
                int count = recorder.read(samples, 0, samples.length, AudioRecord.READ_BLOCKING);
                if (count > 0 && nativeHandle != 0) {
                    boolean changed = MusicAnalyzerNative.nativePushSamples(nativeHandle, samples, count);
                    if (changed) {
                        lastAnalysisNanos = System.nanoTime();
                        analyzerView.postInvalidateOnAnimation();
                    }
                }
                if (count > 0 && monitor != null) {
                    monitor.write(samples, 0, count, AudioTrack.WRITE_NON_BLOCKING);
                }
            }
        } catch (SecurityException ignored) {
            running = false;
        } finally {
            if (monitor != null) {
                try {
                    monitor.stop();
                } catch (IllegalStateException ignored) {
                }
                monitor.release();
            }
            if (recorder != null) {
                recorder.stop();
                recorder.release();
            }
        }
    }

    private final class AnalyzerView extends View {
        private final Bitmap bitmap;
        private final Paint paint = new Paint(Paint.FILTER_BITMAP_FLAG);
        private long lastDrawNanos = System.nanoTime();

        AnalyzerView(Activity activity, int width, int height) {
            super(activity);
            bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888);
            setBackgroundColor(Color.BLACK);
        }

        @Override
        protected void onDraw(Canvas canvas) {
            long now = System.nanoTime();
            float elapsed = Math.max(0.0f, (now - lastDrawNanos) / 1_000_000_000.0f);
            float age = Math.max(0.0f, (now - lastAnalysisNanos) / 1_000_000_000.0f);
            lastDrawNanos = now;
            updateRuntimeMetrics(now);
            if (nativeHandle != 0) {
                MusicAnalyzerNative.nativeRender(nativeHandle, bitmap, elapsed, age);
            }

            float viewW = getWidth();
            float viewH = getHeight();
            float scale = Math.min(viewW / bitmap.getWidth(), viewH / bitmap.getHeight());
            float drawW = bitmap.getWidth() * scale;
            float drawH = bitmap.getHeight() * scale;
            float left = (viewW - drawW) * 0.5f;
            float top = (viewH - drawH) * 0.5f;
            canvas.drawColor(Color.BLACK);
            canvas.drawBitmap(bitmap, null, new RectF(left, top, left + drawW, top + drawH), paint);
            if (running) {
                postInvalidateDelayed(age < 1.5f ? ACTIVE_FRAME_DELAY_MS : IDLE_FRAME_DELAY_MS);
            }
        }
    }
}
