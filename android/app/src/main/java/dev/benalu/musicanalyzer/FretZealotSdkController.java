package dev.benalu.musicanalyzer;

import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGattService;
import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import com.fz.blelib.LEDBLELib;
import com.fz.blelib.LEDBLELibCallback;
import java.io.Closeable;
import java.util.List;

/** Owns the official Fret Zealot SDK lifecycle and translates shared analyzer packets to its API. */
final class FretZealotSdkController implements Closeable {
    private static final String TAG = "MusicAnalyzerFZ";
    private static final byte LOWEST_SDK_INTENSITY = 3;
    private static final int STRING_COUNT = 6;
    // Physical LED indices 0-14 correspond to musical frets 1-15.
    private static final int FRET_COUNT = 15;
    // 1/15 makes every nonzero RGB component identical, collapsing orange into
    // yellow. 3/15 retains the calibrated Fret Zealot hue order at low power.
    private static final int LOWEST_CHANNEL_MAX = 3;
    // The original Fret Zealot reports GATT completion before the last legacy
    // packet is applied to its LEDs. Keep the frame active until each batch has
    // physically settled so AUTO-root changes coalesce without interleaving.
    private static final long LEGACY_BATCH_SETTLE_MILLIS = 750L;
    // The first-generation board can acknowledge a large BLE payload before it
    // has applied every LED command. Keep each flushed command buffer bounded.
    private static final int LEGACY_SCALE_COMMANDS_PER_FLUSH = 12;

    interface Listener {
        void onConnecting();
        void onReady();
        void onDisconnected();
        void onError();
    }

    private final LEDBLELib sdk;
    private final Listener listener;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private boolean active;
    private boolean ready;
    private boolean closing;
    // Scale packets include a reset marker for controllers that need one, but
    // sending set_all on every root change produces a visible full-board blink.
    private boolean needsInitialScaleReset = true;
    // A scale update can take longer than an AUTO-root revision. Keep only the
    // latest request while one packet is in flight, then build its delta from
    // the frame that the guitar actually confirmed.
    private ScaleFrame committedScaleFrame = new ScaleFrame();
    private ScaleFrame activeScaleFrame;
    private ScaleFrame queuedScaleFrame;
    private boolean queuedScaleFrameRequiresReconciliation;
    private boolean activeScaleFrameReconcilesWholeBoard;
    private boolean activeScaleFrameClearsNonTargets;
    private int activeScaleFramePhase;
    private int activeScaleFrameCursor;
    private int activeScaleFrameBatchId;

    FretZealotSdkController(Context context, Listener listener) {
        sdk = LEDBLELib.getInstance(context.getApplicationContext());
        this.listener = listener;
    }

    boolean isActive() {
        return active;
    }

    boolean isReady() {
        return ready;
    }

    boolean isScaleFrameInFlight() {
        return activeScaleFrame != null;
    }

    private static byte dimChannel(int channel) {
        int clamped = Math.max(0, Math.min(15, channel));
        if (clamped == 0) {
            return 0;
        }
        return (byte) Math.max(1, (clamped * LOWEST_CHANNEL_MAX + 7) / 15);
    }

    private static byte fretZealotPixelForStandardTuningString(int lowToHighString) {
        // Analyzer packets use E-A-D-G-B-E. The Fret Zealot SDK labels the
        // physical pixels in the opposite, high-E-to-low-E order.
        return (byte) (5 - lowToHighString);
    }

    void connect(BluetoothDevice device) {
        if (active || device == null) {
            return;
        }
        final String address;
        try {
            address = device.getAddress();
        } catch (SecurityException exception) {
            Log.w(TAG, "Unable to read Fret Zealot address", exception);
            listener.onError();
            return;
        }
        active = true;
        ready = false;
        closing = false;
        needsInitialScaleReset = true;
        clearScaleFrames();
        listener.onConnecting();
        try {
            sdk.startService(address, sdkCallback);
            sdk.onResume();
        } catch (RuntimeException exception) {
            Log.w(TAG, "Unable to start Fret Zealot SDK", exception);
            active = false;
            sdk.stopService();
            listener.onError();
        }
    }

    void sendPacket(byte[] packet, boolean reconcileWholeBoard) {
        if (!ready || packet == null || packet.length == 0 || packet.length % 4 != 0) {
            return;
        }
        ScaleFrame target = new ScaleFrame();

        boolean containsScaleResetMarker = false;
        for (int offset = 0; offset < packet.length; offset += 4) {
            int command = (packet[offset] >>> 4) & 0x0f;
            if (command == 0x04) {
                containsScaleResetMarker = true;
                continue;
            }
            if (command != 0x00) {
                Log.w(TAG, "Ignoring unsupported SDK LED command " + command);
                continue;
            }
            int stringMask = packet[offset + 3] & 0xff;
            int fret = (packet[offset + 1] >>> 4) & 0x0f;
            if (fret >= FRET_COUNT) {
                continue;
            }
            byte red = dimChannel(packet[offset + 1] & 0x0f);
            byte green = dimChannel((packet[offset + 2] >>> 4) & 0x0f);
            byte blue = dimChannel(packet[offset + 2] & 0x0f);
            byte effect = (byte) (packet[offset] & 0x0f);
            for (int string = 0; string < STRING_COUNT; ++string) {
                if ((stringMask & (1 << (string + 1))) == 0) {
                    continue;
                }
                target.lit[string][fret] = true;
                target.red[string][fret] = red;
                target.green[string][fret] = green;
                target.blue[string][fret] = blue;
                target.effect[string][fret] = effect;
            }
        }

        if (activeScaleFrame != null) {
            queuedScaleFrame = target;
            queuedScaleFrameRequiresReconciliation |= reconcileWholeBoard;
            return;
        }
        startScaleFrame(target, containsScaleResetMarker, reconcileWholeBoard);
    }

    @Override
    public void close() {
        closing = true;
        active = false;
        ready = false;
        needsInitialScaleReset = true;
        clearScaleFrames();
        try {
            sdk.onPause();
            sdk.stopService();
        } catch (RuntimeException exception) {
            Log.w(TAG, "Unable to stop Fret Zealot SDK", exception);
        } finally {
            closing = false;
        }
    }

    private final LEDBLELibCallback sdkCallback = new LEDBLELibCallback() {
        @Override
        public void onConnected() {
            handler.post(() -> {
                if (active && !closing) {
                    listener.onConnecting();
                }
            });
        }

        @Override
        public void onDisconnected() {
            handler.post(() -> {
                if (closing || !active) {
                    return;
                }
                active = false;
                ready = false;
                needsInitialScaleReset = true;
                clearScaleFrames();
                listener.onDisconnected();
            });
        }

        @Override
        public void onServiceDiscovered(List<BluetoothGattService> serviceList) {
            handler.post(() -> {
                if (!active || closing) {
                    return;
                }
                if (!sdk.isLED()) {
                    Log.w(TAG, "Fret Zealot SDK found no supported LED characteristic");
                    close();
                    listener.onError();
                    return;
                }
                // Let the notification descriptor write finish before the first LED packet.
                // Its reset marker performs the one required full-board clear for this session.
                handler.postDelayed(() -> {
                    if (!active || closing || !sdk.isLED()) {
                        return;
                    }
                    Log.i(TAG, "Fret Zealot LED service ready; sending current scale");
                    ready = true;
                    listener.onReady();
                }, 150L);
            });
        }

        @Override
        public void onDataReceived(byte[] rxBytes) {
        }

        @Override
        public void onBatteryString(String value) {
        }

        @Override
        public void onManufactureNameString(String value) {
        }

        @Override
        public void onModelNumberString(String value) {
        }

        @Override
        public void onSerialNumberString(String value) {
        }

        @Override
        public void onHardwareRevisionString(String value) {
        }
    };

    private void clearScaleFrames() {
        committedScaleFrame = new ScaleFrame();
        activeScaleFrame = null;
        queuedScaleFrame = null;
        queuedScaleFrameRequiresReconciliation = false;
        activeScaleFrameReconcilesWholeBoard = false;
        activeScaleFrameClearsNonTargets = false;
        activeScaleFramePhase = 0;
        activeScaleFrameCursor = 0;
        ++activeScaleFrameBatchId;
    }

    private void onScaleFrameFlushed(ScaleFrame completed, int batchId) {
        handler.postDelayed(
                () -> finishScaleFrameBatch(completed, batchId), LEGACY_BATCH_SETTLE_MILLIS);
    }

    private void scheduleScaleFrameBatchFallback(ScaleFrame completed, int batchId) {
        handler.postDelayed(
                () -> finishScaleFrameBatch(completed, batchId), LEGACY_BATCH_SETTLE_MILLIS);
    }

    private void finishScaleFrameBatch(ScaleFrame completed, int batchId) {
        if (!active || closing || activeScaleFrame != completed || batchId != activeScaleFrameBatchId) {
            return;
        }
        // Invalidate both the callback and fallback for this batch before a
        // subsequent batch can be submitted.
        ++activeScaleFrameBatchId;
        finishScaleFrame(completed);
    }

    private void finishScaleFrame(ScaleFrame completed) {
        if (!active || closing || activeScaleFrame != completed) {
            return;
        }
        if (flushNextScaleFrameBatch(completed)) {
            return;
        }
        committedScaleFrame = completed;
        activeScaleFrame = null;
        if (queuedScaleFrame != null) {
            ScaleFrame queued = queuedScaleFrame;
            boolean reconcileWholeBoard = queuedScaleFrameRequiresReconciliation;
            queuedScaleFrame = null;
            queuedScaleFrameRequiresReconciliation = false;
            startScaleFrame(queued, false, reconcileWholeBoard);
        }
    }

    private void startScaleFrame(ScaleFrame target, boolean containsScaleResetMarker,
            boolean reconcileWholeBoard) {
        boolean boardReset = false;
        if (containsScaleResetMarker && needsInitialScaleReset) {
            needsInitialScaleReset = false;
            boardReset = true;
        }
        activeScaleFrame = target;
        activeScaleFrameReconcilesWholeBoard = reconcileWholeBoard;
        activeScaleFrameClearsNonTargets = reconcileWholeBoard && !boardReset;
        activeScaleFramePhase = 0;
        activeScaleFrameCursor = 0;
        if (boardReset) {
            sdk.sendCommandBufferClear();
            sdk.set_all((byte) 0, (byte) 0, (byte) 0, LOWEST_SDK_INTENSITY, (byte) 0);
            int batchId = ++activeScaleFrameBatchId;
            sdk.sendCommandFlush(() -> onScaleFrameFlushed(target, batchId));
            scheduleScaleFrameBatchFallback(target, batchId);
            return;
        }
        if (!flushNextScaleFrameBatch(target)) {
            finishScaleFrame(target);
        }
    }

    private boolean flushNextScaleFrameBatch(ScaleFrame target) {
        while (activeScaleFramePhase < 2) {
            sdk.sendCommandBufferClear();
            int commands = 0;
            while (activeScaleFrameCursor < STRING_COUNT * FRET_COUNT
                    && commands < LEGACY_SCALE_COMMANDS_PER_FLUSH) {
                int string = activeScaleFrameCursor / FRET_COUNT;
                int fret = activeScaleFrameCursor % FRET_COUNT;
                ++activeScaleFrameCursor;
                if (activeScaleFramePhase == 0) {
                    boolean needsTarget = target.lit[string][fret]
                            && (activeScaleFrameReconcilesWholeBoard
                            || !target.samePixel(committedScaleFrame, string, fret));
                    if (!needsTarget) {
                        continue;
                    }
                    setPixel(string, fret, target.red[string][fret], target.green[string][fret],
                            target.blue[string][fret], target.effect[string][fret]);
                } else {
                    boolean needsClear = activeScaleFrameClearsNonTargets
                            ? !target.lit[string][fret]
                            : committedScaleFrame.lit[string][fret] && !target.lit[string][fret];
                    if (!needsClear) {
                        continue;
                    }
                    setPixel(string, fret, (byte) 0, (byte) 0, (byte) 0, (byte) 0);
                }
                ++commands;
            }
            if (commands > 0) {
                int batchId = ++activeScaleFrameBatchId;
                sdk.sendCommandFlush(() -> onScaleFrameFlushed(target, batchId));
                scheduleScaleFrameBatchFallback(target, batchId);
                return true;
            }
            ++activeScaleFramePhase;
            activeScaleFrameCursor = 0;
        }
        return false;
    }

    private void setPixel(int string, int fret, byte red, byte green, byte blue, byte effect) {
        sdk.set(
                (byte) fret,
                fretZealotPixelForStandardTuningString(string),
                red,
                green,
                blue,
                LOWEST_SDK_INTENSITY,
                effect);
    }

    private static final class ScaleFrame {
        final boolean[][] lit = new boolean[STRING_COUNT][FRET_COUNT];
        final byte[][] red = new byte[STRING_COUNT][FRET_COUNT];
        final byte[][] green = new byte[STRING_COUNT][FRET_COUNT];
        final byte[][] blue = new byte[STRING_COUNT][FRET_COUNT];
        final byte[][] effect = new byte[STRING_COUNT][FRET_COUNT];

        boolean samePixel(ScaleFrame other, int string, int fret) {
            return other.lit[string][fret]
                    && red[string][fret] == other.red[string][fret]
                    && green[string][fret] == other.green[string][fret]
                    && blue[string][fret] == other.blue[string][fret]
                    && effect[string][fret] == other.effect[string][fret];
        }
    }
}
