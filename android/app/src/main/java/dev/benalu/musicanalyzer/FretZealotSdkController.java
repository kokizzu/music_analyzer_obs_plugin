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
    // packet is applied to its LEDs. Keep the frame active briefly so AUTO
    // root changes coalesce instead of building deltas from an unfinished map.
    private static final long LEGACY_FRAME_SETTLE_MILLIS = 250L;

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
    // A complete replacement is sent as target LEDs then non-target clears.
    // Splitting those operations keeps each legacy board frame small enough to
    // apply reliably without blacking out the whole fretboard.
    private boolean activeScaleFrameRequiresClearPass;
    // A legacy Fret Zealot can acknowledge a complete BLE payload before its
    // LED processor has applied every command. Reassert targets once before
    // any stale-pixel clear so a dropped first pass never becomes a partial
    // scale that remains on the board.
    private boolean activeScaleFrameRequiresTargetReassert;

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
        activeScaleFrameRequiresClearPass = false;
        activeScaleFrameRequiresTargetReassert = false;
    }

    private void onScaleFrameFlushed(ScaleFrame completed) {
        handler.postDelayed(() -> finishScaleFrame(completed), LEGACY_FRAME_SETTLE_MILLIS);
    }

    private void finishScaleFrame(ScaleFrame completed) {
        if (!active || closing || activeScaleFrame != completed) {
            return;
        }
        if (activeScaleFrameRequiresTargetReassert) {
            activeScaleFrameRequiresTargetReassert = false;
            sdk.sendCommandBufferClear();
            writeScaleFrameReconciliation(completed);
            sdk.sendCommandFlush(() -> onScaleFrameFlushed(completed));
            return;
        }
        if (activeScaleFrameRequiresClearPass) {
            activeScaleFrameRequiresClearPass = false;
            // The target LEDs are now all present. Clear the rest in a second,
            // smaller frame so a new AUTO root never appears only partially.
            sdk.sendCommandBufferClear();
            writeScaleFrameNonTargetClear(completed);
            sdk.sendCommandFlush(() -> onScaleFrameFlushed(completed));
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
        sdk.sendCommandBufferClear();
        boolean boardReset = false;
        if (containsScaleResetMarker && needsInitialScaleReset) {
            sdk.set_all((byte) 0, (byte) 0, (byte) 0, LOWEST_SDK_INTENSITY, (byte) 0);
            needsInitialScaleReset = false;
            boardReset = true;
        }
        if (reconcileWholeBoard) {
            writeScaleFrameReconciliation(target);
            // The second target pass runs after the first pass has settled.
            // It is deliberately ordered before stale clears: a frame that
            // loses one legacy command must not commit a partial new scale.
            activeScaleFrameRequiresTargetReassert = true;
            activeScaleFrameRequiresClearPass = !boardReset;
        } else {
            // Manual updates are deltas. Sending a full clear here can overrun
            // legacy firmware and leave only a partial scale visible.
            writeScaleFrameDelta(committedScaleFrame, target);
            activeScaleFrameRequiresTargetReassert = false;
            activeScaleFrameRequiresClearPass = false;
        }
        activeScaleFrame = target;
        sdk.sendCommandFlush(() -> onScaleFrameFlushed(target));
    }

    // The controller applies set commands serially, including within one BLE
    // batch. Light new/recoloured notes first, then clear obsolete notes, so
    // first-generation 20-byte writes retain a continuous visible scale.
    private void writeScaleFrameDelta(ScaleFrame current, ScaleFrame target) {
        for (int string = 0; string < STRING_COUNT; ++string) {
            for (int fret = 0; fret < FRET_COUNT; ++fret) {
                if (target.lit[string][fret] && !target.samePixel(current, string, fret)) {
                    setPixel(string, fret, target.red[string][fret], target.green[string][fret],
                            target.blue[string][fret], target.effect[string][fret]);
                }
            }
        }
        for (int string = 0; string < STRING_COUNT; ++string) {
            for (int fret = 0; fret < FRET_COUNT; ++fret) {
                if (current.lit[string][fret] && !target.lit[string][fret]) {
                    setPixel(string, fret, (byte) 0, (byte) 0, (byte) 0, (byte) 0);
                }
            }
        }
    }

    // The legacy board can occasionally finish only part of a previous frame
    // while AUTO root estimates are changing. Reassert every target pixel.
    // The preceding delta already retires obsolete pixels, and batching those
    // clears here makes the recovery frame large enough to fail partially.
    private void writeScaleFrameReconciliation(ScaleFrame target) {
        for (int string = 0; string < STRING_COUNT; ++string) {
            for (int fret = 0; fret < FRET_COUNT; ++fret) {
                if (target.lit[string][fret]) {
                    setPixel(string, fret, target.red[string][fret], target.green[string][fret],
                            target.blue[string][fret], target.effect[string][fret]);
                }
            }
        }
    }

    private void writeScaleFrameNonTargetClear(ScaleFrame target) {
        for (int string = 0; string < STRING_COUNT; ++string) {
            for (int fret = 0; fret < FRET_COUNT; ++fret) {
                if (!target.lit[string][fret]) {
                    setPixel(string, fret, (byte) 0, (byte) 0, (byte) 0, (byte) 0);
                }
            }
        }
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
