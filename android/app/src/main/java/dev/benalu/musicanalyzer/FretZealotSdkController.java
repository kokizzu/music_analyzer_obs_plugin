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
    private static final int LOWEST_CHANNEL_MAX = 1;

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
                        dimChannel(blue),
                        dimChannel(green),
                        LOWEST_SDK_INTENSITY,
                        (byte) effect);
            }
        }
        sdk.sendCommandFlush();
    }

    private void clearBoard() {
        sdk.sendCommandBufferClear();
        // Fret Zealot 2's official app uses SET_ALL black when it leaves a display
        // mode. Unlike the legacy CLEAR command, that also resets its blue background.
        sdk.set_all((byte) 0, (byte) 0, (byte) 0, LOWEST_SDK_INTENSITY, (byte) 0);
        sdk.sendCommandFlush();
    }

    private void initializeFretZealot2Session() {
        // Mirror the official app's FZ2 session priming before it starts LED writes.
        sdk.readManufacturerName();
        handler.postDelayed(sdk::readModelNumberString, 50L);
        handler.postDelayed(sdk::readBattery, 100L);
        handler.postDelayed(sdk::readHardwareRevision, 150L);
        handler.postDelayed(sdk::readSerialNumber, 200L);
        handler.postDelayed(sdk::readFirmwareRevision, 250L);
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
                // The vendor SDK subscribes to the LED notification characteristic before
                // its first command. Prime the FZ2 session, then render the current scale.
                handler.postDelayed(() -> {
                    if (!active || closing || !sdk.isLED()) {
                        return;
                    }
                    Log.i(TAG, "Fret Zealot LED service ready; preparing current scale");
                    initializeFretZealot2Session();
                    handler.postDelayed(() -> {
                        if (!active || closing || !sdk.isLED()) {
                            return;
                        }
                        try {
                            clearBoard();
                        } catch (RuntimeException exception) {
                            Log.w(TAG, "Unable to clear Fret Zealot board before scale output", exception);
                        }
                        ready = true;
                        listener.onReady();
                    }, 300L);
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
