package dev.benalu.musicanalyzer;

import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattDescriptor;
import android.bluetooth.BluetoothGattService;
import android.bluetooth.BluetoothProfile;
import android.content.Context;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import java.io.Closeable;
import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.UUID;

/**
 * Native Android implementation of the public FretSpark SCT-86PRO transport.
 *
 * It deliberately follows the SDK's runtime path: FFF0/FFF3 writes, FFF4
 * notifications, 247-byte MTU, the 0xBC/0x55 frame envelope, configuration
 * queries, and learning-LED batches. OTA and classroom features are not part
 * of the analyzer output path.
 */
@SuppressWarnings("deprecation")
final class AuphySct86ProController implements Closeable {
    private static final String TAG = "MusicAnalyzerAUPHY";
    private static final UUID SERVICE = UUID.fromString("0000fff0-0000-1000-8000-00805f9b34fb");
    private static final UUID WRITE = UUID.fromString("0000fff3-0000-1000-8000-00805f9b34fb");
    private static final UUID NOTIFY = UUID.fromString("0000fff4-0000-1000-8000-00805f9b34fb");
    private static final UUID CLIENT_CHARACTERISTIC_CONFIG =
            UUID.fromString("00002902-0000-1000-8000-00805f9b34fb");
    private static final int REQUESTED_MTU = 247;
    private static final int DEFAULT_LED_COUNT = 90;
    private static final int MAX_LEDS_PER_PACKET = 59;
    private static final long WRITE_WITHOUT_RESPONSE_DELAY_MILLIS = 12;

    // FretSpark application-to-firmware commands.
    private static final int COMMAND_POWER = 0x01;
    private static final int COMMAND_LINEAR_LAYOUT = 0x02;
    private static final int COMMAND_BATCH_DATA = 0x16;
    private static final int COMMAND_BATCH_BEGIN = 0x1c;
    private static final int COMMAND_BATCH_END = 0x1d;
    private static final int COMMAND_QUERY_VERSION = 0x1e;
    private static final int COMMAND_QUERY_LED_CONFIG = 0x1f;
    private static final int COMMAND_LEARNING_LED = 0x22;
    private static final int COMMAND_QUERY_LED_INDEX_MODE = 0x28;

    interface Listener {
        void onConnecting();
        void onReady();
        void onLedCountChanged();
        void onDisconnected();
        void onError();
    }

    private final Context context;
    private final Listener listener;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final ArrayDeque<byte[]> writeQueue = new ArrayDeque<>();

    private BluetoothGatt gatt;
    private BluetoothGattCharacteristic writeCharacteristic;
    private BluetoothGattCharacteristic notifyCharacteristic;
    private boolean active;
    private boolean ready;
    private boolean closing;
    private boolean discovering;
    private boolean writing;
    private boolean writeWithoutResponse;
    private int ledCount = DEFAULT_LED_COUNT;

    AuphySct86ProController(Context context, Listener listener) {
        this.context = context.getApplicationContext();
        this.listener = listener;
    }

    boolean isActive() {
        return active;
    }

    boolean isReady() {
        return ready;
    }

    int maxFret() {
        return Math.max(0, Math.min(41, ledCount / 6 - 1));
    }

    void connect(BluetoothDevice device) {
        if (active || device == null) {
            return;
        }
        active = true;
        ready = false;
        closing = false;
        discovering = false;
        ledCount = DEFAULT_LED_COUNT;
        listener.onConnecting();
        try {
            gatt = device.connectGatt(context, false, callback, BluetoothDevice.TRANSPORT_LE);
            if (gatt == null) {
                fail();
            }
        } catch (SecurityException exception) {
            Log.w(TAG, "Unable to connect SCT-86PRO", exception);
            fail();
        }
    }

    /** Sends the same clear-then-learning-LED scale sequence as FretSpark.showScale. */
    void sendScalePixels(byte[] rawPixels) {
        if (!ready || rawPixels == null || rawPixels.length == 0 || rawPixels.length % 4 != 0) {
            return;
        }
        // Keep setup and query commands FIFO ahead of the frame. This is the
        // FretSpark SendQueue behavior: a later root update must not drop the
        // matrix-layout command that makes the physical string map valid.
        enqueueCommand(COMMAND_LEARNING_LED, new byte[] {0x00});

        byte[] pixels = filterPixels(rawPixels);
        int count = pixels.length / 4;
        if (count == 0) {
            return;
        }
        if (count <= MAX_LEDS_PER_PACKET) {
            byte[] params = new byte[2 + pixels.length];
            params[0] = 0x02;
            params[1] = (byte) count;
            System.arraycopy(pixels, 0, params, 2, pixels.length);
            enqueueCommand(COMMAND_LEARNING_LED, params);
            return;
        }

        int packetCount = (count + MAX_LEDS_PER_PACKET - 1) / MAX_LEDS_PER_PACKET;
        enqueueCommand(COMMAND_BATCH_BEGIN, new byte[] {(byte) packetCount});
        int sequence = 0;
        for (int offset = 0; offset < pixels.length; offset += MAX_LEDS_PER_PACKET * 4) {
            int bytes = Math.min(MAX_LEDS_PER_PACKET * 4, pixels.length - offset);
            int chunkCount = bytes / 4;
            byte[] params = new byte[2 + bytes];
            params[0] = (byte) ++sequence;
            params[1] = (byte) chunkCount;
            System.arraycopy(pixels, offset, params, 2, bytes);
            enqueueCommand(COMMAND_BATCH_DATA, params);
        }
        enqueueCommand(COMMAND_BATCH_END, new byte[0]);
    }

    @Override
    public void close() {
        closing = true;
        active = false;
        ready = false;
        discovering = false;
        writeQueue.clear();
        writing = false;
        BluetoothGatt closingGatt = gatt;
        gatt = null;
        writeCharacteristic = null;
        notifyCharacteristic = null;
        if (closingGatt != null) {
            try {
                closingGatt.disconnect();
                closingGatt.close();
            } catch (SecurityException exception) {
                Log.w(TAG, "Unable to close SCT-86PRO", exception);
            }
        }
        closing = false;
    }

    private byte[] filterPixels(byte[] rawPixels) {
        byte[] result = new byte[rawPixels.length];
        int output = 0;
        boolean[] seen = new boolean[Math.min(256, Math.max(1, ledCount))];
        for (int offset = 0; offset < rawPixels.length; offset += 4) {
            int index = rawPixels[offset] & 0xff;
            if (index >= ledCount || index >= seen.length || seen[index]) {
                continue;
            }
            seen[index] = true;
            System.arraycopy(rawPixels, offset, result, output, 4);
            output += 4;
        }
        return Arrays.copyOf(result, output);
    }

    private void discoverServices() {
        if (gatt == null || discovering) {
            return;
        }
        discovering = true;
        try {
            if (!gatt.discoverServices()) {
                fail();
            }
        } catch (SecurityException exception) {
            Log.w(TAG, "Unable to discover SCT-86PRO services", exception);
            fail();
        }
    }

    private void configureCharacteristics(BluetoothGatt connectedGatt) {
        BluetoothGattService service = connectedGatt.getService(SERVICE);
        BluetoothGattCharacteristic write = service == null ? null : service.getCharacteristic(WRITE);
        BluetoothGattCharacteristic notify = service == null ? null : service.getCharacteristic(NOTIFY);
        if (write == null || notify == null) {
            Log.w(TAG, "SCT-86PRO is missing FFF0/FFF3/FFF4");
            fail();
            return;
        }
        BluetoothGattDescriptor descriptor = notify.getDescriptor(CLIENT_CHARACTERISTIC_CONFIG);
        if (descriptor == null) {
            Log.w(TAG, "SCT-86PRO FFF4 has no CCCD");
            fail();
            return;
        }
        try {
            if (!connectedGatt.setCharacteristicNotification(notify, true)) {
                fail();
                return;
            }
            boolean accepted;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                accepted = connectedGatt.writeDescriptor(descriptor, BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE)
                        == android.bluetooth.BluetoothStatusCodes.SUCCESS;
            } else {
                descriptor.setValue(BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE);
                accepted = connectedGatt.writeDescriptor(descriptor);
            }
            if (!accepted) {
                fail();
                return;
            }
            writeCharacteristic = write;
            notifyCharacteristic = notify;
        } catch (SecurityException exception) {
            Log.w(TAG, "Unable to subscribe SCT-86PRO notifications", exception);
            fail();
        }
    }

    private void becameReady() {
        if (!active || ready || writeCharacteristic == null || notifyCharacteristic == null) {
            return;
        }
        ready = true;
        // Matrix is the FretSpark default. Explicitly select it before the
        // first learning frame so a prior vendor-app linear setting cannot
        // change the string/fret map.
        enqueueCommand(COMMAND_POWER, new byte[] {0x01});
        enqueueCommand(COMMAND_LINEAR_LAYOUT, new byte[] {0x00});
        listener.onReady();
        // FretSpark's automatic handshake queries version, LED count and
        // index mode. Delay these behind the first visual frame; the 90-LED
        // SDK default remains safe until the FFF4 response arrives.
        handler.postDelayed(() -> {
            if (!ready) return;
            enqueueCommand(COMMAND_QUERY_VERSION, new byte[0]);
            enqueueCommand(COMMAND_QUERY_LED_CONFIG, new byte[0]);
            enqueueCommand(COMMAND_QUERY_LED_INDEX_MODE, new byte[0]);
        }, 250);
    }

    private void enqueueCommand(int command, byte[] params) {
        if (gatt == null || writeCharacteristic == null || params == null || params.length > 250) {
            return;
        }
        byte[] frame = new byte[params.length + 4];
        frame[0] = (byte) 0xbc;
        frame[1] = (byte) command;
        frame[2] = (byte) params.length;
        System.arraycopy(params, 0, frame, 3, params.length);
        frame[frame.length - 1] = 0x55;
        writeQueue.add(frame);
        writeNext();
    }

    private void writeNext() {
        if (writing || gatt == null || writeCharacteristic == null) {
            return;
        }
        byte[] frame = writeQueue.pollFirst();
        if (frame == null) {
            return;
        }
        int properties = writeCharacteristic.getProperties();
        boolean withoutResponse = (properties & BluetoothGattCharacteristic.PROPERTY_WRITE_NO_RESPONSE) != 0;
        int writeType = withoutResponse
                ? BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE
                : BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT;
        boolean accepted;
        try {
            writing = true;
            writeWithoutResponse = withoutResponse;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                accepted = gatt.writeCharacteristic(writeCharacteristic, frame, writeType)
                        == android.bluetooth.BluetoothStatusCodes.SUCCESS;
            } else {
                writeCharacteristic.setWriteType(writeType);
                writeCharacteristic.setValue(frame);
                accepted = gatt.writeCharacteristic(writeCharacteristic);
            }
        } catch (SecurityException exception) {
            accepted = false;
        }
        if (!accepted) {
            writing = false;
            fail();
            return;
        }
        if (withoutResponse) {
            handler.postDelayed(() -> {
                writing = false;
                writeNext();
            }, WRITE_WITHOUT_RESPONSE_DELAY_MILLIS);
        }
    }

    private void handleNotify(byte[] value) {
        if (value == null || value.length < 4 || (value[0] & 0xff) != 0xcc
                || (value[value.length - 1] & 0xff) != 0xaa) {
            return;
        }
        int command = value[1] & 0xff;
        int length = value[2] & 0xff;
        if (value.length != length + 4) {
            return;
        }
        if (command == COMMAND_QUERY_LED_CONFIG && length >= 2) {
            int receivedLedCount = ((value[3] & 0xff) << 8) | (value[4] & 0xff);
            if (receivedLedCount >= 6 && receivedLedCount <= 255 && receivedLedCount != ledCount) {
                ledCount = receivedLedCount;
                listener.onLedCountChanged();
            }
        }
    }

    private void disconnected() {
        boolean notify = active && !closing;
        active = false;
        ready = false;
        discovering = false;
        writing = false;
        writeQueue.clear();
        BluetoothGatt disconnectedGatt = gatt;
        gatt = null;
        writeCharacteristic = null;
        notifyCharacteristic = null;
        if (disconnectedGatt != null) {
            try {
                disconnectedGatt.close();
            } catch (SecurityException ignored) {
            }
        }
        if (notify) {
            listener.onDisconnected();
        }
    }

    private void fail() {
        boolean notify = active && !closing;
        close();
        if (notify) {
            listener.onError();
        }
    }

    private final BluetoothGattCallback callback = new BluetoothGattCallback() {
        @Override
        public void onConnectionStateChange(BluetoothGatt callbackGatt, int status, int newState) {
            handler.post(() -> {
                if (callbackGatt != gatt) {
                    try {
                        callbackGatt.close();
                    } catch (SecurityException ignored) {
                    }
                    return;
                }
                if (status == BluetoothGatt.GATT_SUCCESS && newState == BluetoothProfile.STATE_CONNECTED) {
                    listener.onConnecting();
                    try {
                        if (!callbackGatt.requestMtu(REQUESTED_MTU)) {
                            discoverServices();
                        }
                    } catch (SecurityException exception) {
                        discoverServices();
                    }
                } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                    disconnected();
                } else if (status != BluetoothGatt.GATT_SUCCESS) {
                    fail();
                }
            });
        }

        @Override
        public void onMtuChanged(BluetoothGatt callbackGatt, int mtu, int status) {
            handler.post(() -> {
                if (callbackGatt == gatt) {
                    discoverServices();
                }
            });
        }

        @Override
        public void onServicesDiscovered(BluetoothGatt callbackGatt, int status) {
            handler.post(() -> {
                if (callbackGatt != gatt) return;
                if (status == BluetoothGatt.GATT_SUCCESS) {
                    configureCharacteristics(callbackGatt);
                } else {
                    fail();
                }
            });
        }

        @Override
        public void onDescriptorWrite(BluetoothGatt callbackGatt, BluetoothGattDescriptor descriptor, int status) {
            handler.post(() -> {
                if (callbackGatt == gatt && NOTIFY.equals(descriptor.getCharacteristic().getUuid())) {
                    if (status == BluetoothGatt.GATT_SUCCESS) {
                        becameReady();
                    } else {
                        fail();
                    }
                }
            });
        }

        @Override
        public void onCharacteristicWrite(BluetoothGatt callbackGatt, BluetoothGattCharacteristic characteristic,
                                          int status) {
            handler.post(() -> {
                if (callbackGatt != gatt || writeWithoutResponse) return;
                writing = false;
                if (status == BluetoothGatt.GATT_SUCCESS) {
                    writeNext();
                } else {
                    fail();
                }
            });
        }

        @Override
        public void onCharacteristicChanged(BluetoothGatt callbackGatt, BluetoothGattCharacteristic characteristic,
                                            byte[] value) {
            if (callbackGatt == gatt && NOTIFY.equals(characteristic.getUuid()) && value != null) {
                byte[] packet = Arrays.copyOf(value, value.length);
                handler.post(() -> handleNotify(packet));
            }
        }

        @Override
        public void onCharacteristicChanged(BluetoothGatt callbackGatt, BluetoothGattCharacteristic characteristic) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU || callbackGatt != gatt
                    || !NOTIFY.equals(characteristic.getUuid())) {
                return;
            }
            byte[] value = characteristic.getValue();
            if (value != null) {
                byte[] packet = Arrays.copyOf(value, value.length);
                handler.post(() -> handleNotify(packet));
            }
        }
    };
}
