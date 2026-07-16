package dev.benalu.musicanalyzer;

import android.Manifest;
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
import android.os.Debug;
import android.os.Process;
import android.util.Log;
import android.view.KeyEvent;
import android.view.View;
import java.util.ArrayList;

public final class MainActivity extends Activity {
    private static final String TAG = "MusicAnalyzer";
    private static final int REQUEST_RECORD_AUDIO = 10;
    private static final int SAMPLE_RATE = 48000;
    private static final long METRICS_INTERVAL_NANOS = 1_000_000_000L;
    private static final long ACTIVE_FRAME_DELAY_MS = 50;
    private static final long IDLE_FRAME_DELAY_MS = 250;
    private static final long CAPTURE_LOG_INTERVAL_NANOS = 1_000_000_000L;

    private AnalyzerView analyzerView;
    private volatile boolean running;
    private Thread audioThread;
    private long nativeHandle;
    private long lastAnalysisNanos;
    private long lastMetricsNanos;
    private long lastCaptureLogNanos;
    private long lastProcessCpuMillis;
    private final Object inputLock = new Object();
    private final ArrayList<InputChoice> inputChoices = new ArrayList<>();
    private int inputChoiceIndex;
    private int selectedInputDeviceId = Integer.MIN_VALUE;
    private volatile String selectedInputLabel = "ANDROID";

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        boolean bassGuitar = "bass-guitar".equals(BuildConfig.MAO_LAYOUT);
        int width = bassGuitar ? 960 : 960;
        int height = bassGuitar ? 420 : 540;
        nativeHandle = MusicAnalyzerNative.nativeCreate(SAMPLE_RATE, width, height, bassGuitar);
        lastAnalysisNanos = System.nanoTime();
        lastMetricsNanos = lastAnalysisNanos;
        lastProcessCpuMillis = Process.getElapsedCpuTime();
        refreshInputDevices(true);
        analyzerView = new AnalyzerView(this, width, height);
        analyzerView.setKeepScreenOn(true);
        analyzerView.setFocusable(true);
        analyzerView.setFocusableInTouchMode(true);
        analyzerView.setOnClickListener(v -> cycleInputDevice());
        setContentView(analyzerView);
        analyzerView.requestFocus();

        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
            startAudio();
        } else {
            requestPermissions(new String[] {Manifest.permission.RECORD_AUDIO}, REQUEST_RECORD_AUDIO);
        }
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_SPACE && event.getRepeatCount() == 0) {
            cycleInputDevice();
            return true;
        }
        return super.onKeyDown(keyCode, event);
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

    private float readAppRamMb() {
        long pssKb = Debug.getPss();
        if (pssKb < 0) {
            return -1.0f;
        }
        return (float) pssKb / 1024.0f;
    }

    private float readAppCpuPercent(long nowNanos) {
        long cpuMillis = Process.getElapsedCpuTime();
        long elapsedNanos = nowNanos - lastMetricsNanos;
        long cpuDeltaMillis = cpuMillis - lastProcessCpuMillis;
        lastProcessCpuMillis = cpuMillis;
        if (elapsedNanos <= 0 || cpuDeltaMillis < 0) {
            return -1.0f;
        }

        float elapsedMillis = (float) elapsedNanos / 1_000_000.0f;
        if (elapsedMillis <= 0.0f) {
            return -1.0f;
        }
        return Math.max(0.0f, Math.min(999.0f, (cpuDeltaMillis * 100.0f) / elapsedMillis));
    }

    private void updateRuntimeMetrics(long nowNanos) {
        if (nativeHandle == 0 || nowNanos - lastMetricsNanos < METRICS_INTERVAL_NANOS) {
            return;
        }
        float cpuPercent = readAppCpuPercent(nowNanos);
        lastMetricsNanos = nowNanos;
        MusicAnalyzerNative.nativeSetRuntimeMetrics(
                nativeHandle,
                cpuPercent,
                readAppRamMb());
    }

    private static boolean isProbablyEmulator() {
        String fingerprint = Build.FINGERPRINT == null ? "" : Build.FINGERPRINT;
        String model = Build.MODEL == null ? "" : Build.MODEL;
        String product = Build.PRODUCT == null ? "" : Build.PRODUCT;
        String hardware = Build.HARDWARE == null ? "" : Build.HARDWARE;
        return fingerprint.contains("generic")
                || fingerprint.contains("emulator")
                || model.contains("sdk")
                || model.contains("Emulator")
                || product.contains("sdk")
                || hardware.contains("goldfish")
                || hardware.contains("ranchu");
    }

    private static int[] captureSources() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            if (isProbablyEmulator()) {
                return new int[] {
                    MediaRecorder.AudioSource.DEFAULT,
                    MediaRecorder.AudioSource.MIC,
                    MediaRecorder.AudioSource.UNPROCESSED
                };
            }
            return new int[] {
                MediaRecorder.AudioSource.UNPROCESSED,
                MediaRecorder.AudioSource.DEFAULT,
                MediaRecorder.AudioSource.MIC
            };
        }
        return new int[] {
            MediaRecorder.AudioSource.DEFAULT,
            MediaRecorder.AudioSource.MIC
        };
    }

    private static final class InputChoice {
        final AudioDeviceInfo device;
        final int deviceId;
        final String label;

        InputChoice(AudioDeviceInfo device, int deviceId, String label) {
            this.device = device;
            this.deviceId = deviceId;
            this.label = label;
        }
    }

    private static final class RecorderSelection {
        final AudioRecord recorder;
        final int source;

        RecorderSelection(AudioRecord recorder, int source) {
            this.recorder = recorder;
            this.source = source;
        }
    }

    private static String inputTypeLabel(int type) {
        switch (type) {
            case AudioDeviceInfo.TYPE_USB_DEVICE:
                return "USB";
            case AudioDeviceInfo.TYPE_USB_HEADSET:
                return "USB HEADSET";
            case AudioDeviceInfo.TYPE_WIRED_HEADSET:
                return "WIRED HEADSET";
            case AudioDeviceInfo.TYPE_BUILTIN_MIC:
                return "BUILT-IN MIC";
            case AudioDeviceInfo.TYPE_LINE_ANALOG:
                return "LINE IN";
            case AudioDeviceInfo.TYPE_BLUETOOTH_SCO:
                return "BT SCO";
            default:
                return "INPUT";
        }
    }

    private static String inputDeviceLabel(AudioDeviceInfo device) {
        if (device == null) {
            return "ANDROID DEFAULT";
        }
        CharSequence productName = device.getProductName();
        String name = productName == null ? "" : productName.toString().trim();
        String prefix = inputTypeLabel(device.getType());
        if (name.isEmpty() || name.equals(prefix)) {
            return prefix;
        }
        return prefix + " " + name;
    }

    private ArrayList<InputChoice> discoverInputChoices() {
        ArrayList<InputChoice> choices = new ArrayList<>();
        choices.add(new InputChoice(null, Integer.MIN_VALUE, "ANDROID DEFAULT"));

        AudioManager audioManager = getSystemService(AudioManager.class);
        if (audioManager == null) {
            return choices;
        }

        for (AudioDeviceInfo device : audioManager.getDevices(AudioManager.GET_DEVICES_INPUTS)) {
            if (device == null || !device.isSource()) {
                continue;
            }
            choices.add(new InputChoice(device, device.getId(), inputDeviceLabel(device)));
        }
        return choices;
    }

    private static String numberedSourceLabel(int index, int count, String label) {
        if (count <= 1) {
            return label;
        }
        return (index + 1) + "/" + count + " " + label;
    }

    private void updateSelectedInputLabelLocked() {
        if (inputChoices.isEmpty()) {
            inputChoices.add(new InputChoice(null, Integer.MIN_VALUE, "ANDROID DEFAULT"));
        }
        inputChoiceIndex = Math.max(0, Math.min(inputChoiceIndex, inputChoices.size() - 1));
        InputChoice choice = inputChoices.get(inputChoiceIndex);
        selectedInputDeviceId = choice.deviceId;
        selectedInputLabel = numberedSourceLabel(inputChoiceIndex, inputChoices.size(), choice.label);
    }

    private void updateNativeSourceName() {
        if (nativeHandle != 0) {
            MusicAnalyzerNative.nativeSetSourceName(nativeHandle, selectedInputLabel);
        }
    }

    private void refreshInputDevices(boolean keepCurrentDevice) {
        ArrayList<InputChoice> discovered = discoverInputChoices();
        synchronized (inputLock) {
            int nextIndex = 0;
            if (keepCurrentDevice) {
                for (int i = 0; i < discovered.size(); ++i) {
                    if (discovered.get(i).deviceId == selectedInputDeviceId) {
                        nextIndex = i;
                        break;
                    }
                }
            } else if (inputChoiceIndex < discovered.size()) {
                nextIndex = inputChoiceIndex;
            }
            inputChoices.clear();
            inputChoices.addAll(discovered);
            inputChoiceIndex = nextIndex;
            updateSelectedInputLabelLocked();
        }
        updateNativeSourceName();
    }

    private InputChoice selectedInputChoice() {
        synchronized (inputLock) {
            if (inputChoices.isEmpty()) {
                inputChoices.add(new InputChoice(null, Integer.MIN_VALUE, "ANDROID DEFAULT"));
                updateSelectedInputLabelLocked();
            }
            return inputChoices.get(inputChoiceIndex);
        }
    }

    private void cycleInputDevice() {
        refreshInputDevices(false);
        synchronized (inputLock) {
            if (inputChoices.size() <= 1) {
                return;
            }
            inputChoiceIndex = (inputChoiceIndex + 1) % inputChoices.size();
            updateSelectedInputLabelLocked();
        }
        updateNativeSourceName();
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
            stopAudio();
            startAudio();
        }
    }

    private RecorderSelection createAudioRecord(int minBuffer, int bufferFrames, InputChoice inputChoice) {
        int bufferBytes = Math.max(minBuffer, bufferFrames * 4);
        for (int source : captureSources()) {
            try {
                AudioRecord recorder = new AudioRecord(
                        source,
                        SAMPLE_RATE,
                        AudioFormat.CHANNEL_IN_MONO,
                        AudioFormat.ENCODING_PCM_FLOAT,
                        bufferBytes);
                if (recorder.getState() == AudioRecord.STATE_INITIALIZED) {
                    if (inputChoice.device != null && !recorder.setPreferredDevice(inputChoice.device)) {
                        recorder.release();
                        continue;
                    }
                    if (BuildConfig.DEBUG) {
                        Log.i(TAG, "using AudioRecord source " + source + " input=" + selectedInputLabel);
                    }
                    return new RecorderSelection(recorder, source);
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

    private void logCaptureLevel(float[] samples, int count, int source) {
        if (!BuildConfig.DEBUG || count <= 0) {
            return;
        }

        double squareSum = 0.0;
        float peak = 0.0f;
        for (int i = 0; i < count; ++i) {
            float sample = samples[i];
            squareSum += (double) sample * (double) sample;
            peak = Math.max(peak, Math.abs(sample));
        }

        long now = System.nanoTime();
        if (now - lastCaptureLogNanos < CAPTURE_LOG_INTERVAL_NANOS) {
            return;
        }
        lastCaptureLogNanos = now;
        float rms = (float) Math.sqrt(squareSum / (double) count);
        Log.i(TAG, "capture source=" + source + " frames=" + count + " rms=" + rms + " peak=" + peak);
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
        int recorderSource = MediaRecorder.AudioSource.DEFAULT;
        AudioTrack monitor = null;
        try {
            InputChoice inputChoice = selectedInputChoice();
            RecorderSelection selection = createAudioRecord(minBuffer, bufferFrames, inputChoice);
            if (selection == null) {
                running = false;
                return;
            }
            recorder = selection.recorder;
            recorderSource = selection.source;
            monitor = createMonitorTrack(bufferFrames);
            recorder.startRecording();
            float[] samples = new float[bufferFrames];
            while (running) {
                int count = recorder.read(samples, 0, samples.length, AudioRecord.READ_BLOCKING);
                if (count > 0 && nativeHandle != 0) {
                    logCaptureLevel(samples, count, recorderSource);
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
        private final RectF destination = new RectF();
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
            destination.set(left, top, left + drawW, top + drawH);
            canvas.drawBitmap(bitmap, null, destination, paint);
            if (running) {
                postInvalidateDelayed(age < 1.5f ? ACTIVE_FRAME_DELAY_MS : IDLE_FRAME_DELAY_MS);
            }
        }
    }
}
