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
    // 1/15 makes every nonzero RGB component identical, collapsing orange into
    // yellow. 3/15 retains the calibrated Fret Zealot hue order at low power.
    private static final int LOWEST_CHANNEL_MAX = 3;
    private static final int VIOLET_BLUE_CHANNEL_LEVEL = 4;

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

    private static byte dimChannel(int channel) {
        int clamped = Math.max(0, Math.min(15, channel));
        if (clamped == 0) {
            return 0;
        }
        return (byte) Math.max(1, (clamped * LOWEST_CHANNEL_MAX + 7) / 15);
    }

    private static byte dimBlueChannel(int red, int green, int blue) {
        // The Fret Zealot's red LED is comparatively strong. Keep its minimum
        // purple component but give blue one extra step for a blue-violet hue.
        if (red == 4 && green == 0 && blue == 15) {
            return VIOLET_BLUE_CHANNEL_LEVEL;
        }
        return dimChannel(blue);
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

    void sendPacket(byte[] packet) {
        if (!ready || packet == null || packet.length == 0 || packet.length % 4 != 0) {
            return;
        }
        sdk.sendCommandBufferClear();
        for (int offset = 0; offset < packet.length; offset += 4) {
            int command = (packet[offset] >>> 4) & 0x0f;
            int effect = packet[offset] & 0x0f;
            if (command == 0x04) {
                sdk.set_all((byte) 0, (byte) 0, (byte) 0, LOWEST_SDK_INTENSITY, (byte) 0);
                continue;
            }
            if (command != 0x00) {
                Log.w(TAG, "Ignoring unsupported SDK LED command " + command);
                continue;
            }
            int fret = (packet[offset + 1] >>> 4) & 0x0f;
            int red = packet[offset + 1] & 0x0f;
            int green = (packet[offset + 2] >>> 4) & 0x0f;
            int blue = packet[offset + 2] & 0x0f;
            int stringMask = packet[offset + 3] & 0xff;
            for (int string = 0; string < 6; ++string) {
                if ((stringMask & (1 << (string + 1))) == 0) {
                    continue;
                }
                sdk.set(
                        (byte) fret,
                        fretZealotPixelForStandardTuningString(string),
                        dimChannel(red),
                        dimChannel(green),
                        dimBlueChannel(red, green, blue),
                        LOWEST_SDK_INTENSITY,
                        (byte) effect);
            }
        }
        sdk.sendCommandFlush();
    }

    @Override
    public void close() {
        closing = true;
        active = false;
        ready = false;
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
                // The scale packet itself starts with a full-board black command, so do not
                // issue a separate write or optional GATT reads before it.
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
}
