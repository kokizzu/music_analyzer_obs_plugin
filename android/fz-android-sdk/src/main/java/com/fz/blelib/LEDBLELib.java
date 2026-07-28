/*
 * Adapted and substantially modified from edgetechlabs/fz-android-sdk.
 * Licensed under the Apache License, Version 2.0; see ../../../../../../LICENSE.
 */
package com.fz.blelib;

import android.annotation.SuppressLint;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattService;
import android.bluetooth.BluetoothManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.util.Log;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;

/**
 * Android 15-compatible core of the edgetechlabs/fz-android-sdk LEDBLELib API.
 */
@SuppressWarnings("deprecation")
public final class LEDBLELib {
    private static final String TAG = "FretZealotSdk";
    private static final long SCAN_PERIOD_MILLIS = 10_000L;
    private static final int CHUNK_BYTES = 20;

    public static final int FadeNotActive = 0;
    public static final int FadeInShort = 1;
    public static final int FadeInLong = 2;
    public static final int FadeOutShort = 3;
    public static final int FadeOutLong = 4;

    private static final int COMMAND_SET = 0x00;
    private static final int COMMAND_SET_ALL = 0x01;
    private static final int COMMAND_SET_ACROSS = 0x02;
    private static final int COMMAND_SET_SUBSET = 0x03;
    private static final int COMMAND_CLEAR = 0x04;
    private static final int COMMAND_SET_DISPLAY = 0x08;

    private static LEDBLELib instance;

    private final Context context;
    private final BluetoothAdapter bluetoothAdapter;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    private final ArrayList<Byte> commandBuffer = new ArrayList<>();

    private BluetoothAdapter.LeScanCallback scanCallback;
    private boolean scanning;
    private boolean serviceBound;
    private boolean connected;
    private String deviceAddress = "";
    private LEDBLELibCallback callback;
    private BluetoothLeService bluetoothLeService;
    private BluetoothGattCharacteristic ledCharacteristic;
    private BluetoothGattCharacteristic batteryCharacteristic;
    private BluetoothGattCharacteristic manufacturerCharacteristic;
    private BluetoothGattCharacteristic modelCharacteristic;
    private BluetoothGattCharacteristic serialCharacteristic;
    private BluetoothGattCharacteristic hardwareCharacteristic;

    private byte[] activePayload;
    private byte[] pendingPayload;
    private int activeOffset;
    private boolean writeInFlight;

    public static synchronized LEDBLELib getInstance(Context context) {
        if (instance == null) {
            instance = new LEDBLELib(context.getApplicationContext());
        }
        return instance;
    }

    public static synchronized LEDBLELib getInstance() {
        return instance;
    }

    public LEDBLELib(Context context) {
        this.context = context.getApplicationContext();
        BluetoothManager manager =
                (BluetoothManager) this.context.getSystemService(Context.BLUETOOTH_SERVICE);
        bluetoothAdapter = manager == null ? null : manager.getAdapter();
    }

    public boolean isSupported() {
        return bluetoothAdapter != null;
    }

    public boolean isScanning() {
        return scanning;
    }

    public boolean isConnected() {
        return connected;
    }

    @SuppressLint("MissingPermission")
    public boolean isEnabled() {
        try {
            return bluetoothAdapter != null && bluetoothAdapter.isEnabled();
        } catch (SecurityException exception) {
            return false;
        }
    }

    public boolean isLED() {
        return ledCharacteristic != null;
    }

    public boolean isDFU() {
        return false;
    }

    @SuppressLint("MissingPermission")
    public void startScan(BluetoothAdapter.LeScanCallback callback) {
        if (bluetoothAdapter == null || callback == null || scanning) {
            return;
        }
        scanCallback = callback;
        try {
            scanning = bluetoothAdapter.startLeScan(callback);
        } catch (SecurityException exception) {
            scanning = false;
            Log.w(TAG, "Unable to scan for Fret Zealot", exception);
        }
        if (scanning) {
            mainHandler.postDelayed(this::stopScan, SCAN_PERIOD_MILLIS);
        }
    }

    @SuppressLint("MissingPermission")
    public void stopScan() {
        BluetoothAdapter.LeScanCallback current = scanCallback;
        scanCallback = null;
        if (bluetoothAdapter != null && current != null) {
            try {
                bluetoothAdapter.stopLeScan(current);
            } catch (SecurityException exception) {
                Log.w(TAG, "Unable to stop Fret Zealot scan", exception);
            }
        }
        scanning = false;
    }

    public void startService(String address, LEDBLELibCallback callback) {
        stopService();
        this.callback = callback;
        deviceAddress = address == null ? "" : address;
        Intent intent = new Intent(context, BluetoothLeService.class);
        try {
            serviceBound = context.bindService(intent, serviceConnection, Context.BIND_AUTO_CREATE);
        } catch (SecurityException exception) {
            serviceBound = false;
            Log.w(TAG, "Unable to bind Fret Zealot service", exception);
        }
        if (!serviceBound) {
            notifyDisconnected();
        }
    }

    public void stopService() {
        stopScan();
        BluetoothLeService service = bluetoothLeService;
        bluetoothLeService = null;
        if (service != null) {
            service.setListener(null);
            service.disconnect();
            service.close();
        }
        if (serviceBound) {
            try {
                context.unbindService(serviceConnection);
            } catch (IllegalArgumentException ignored) {
            }
        }
        serviceBound = false;
        connected = false;
        clearCharacteristics();
        clearWrites();
        callback = null;
    }

    public void connect(String address) {
        deviceAddress = address == null ? "" : address;
        BluetoothLeService service = bluetoothLeService;
        if (service != null && !service.connect(deviceAddress)) {
            notifyDisconnected();
        }
    }

    public void disconnect() {
        BluetoothLeService service = bluetoothLeService;
        if (service != null) {
            service.disconnect();
        }
    }

    /** Retained for source compatibility with the SDK's activity lifecycle API. */
    public void onResume() {
    }

    /** Retained for source compatibility with the SDK's activity lifecycle API. */
    public void onPause() {
    }

    public String getDeviceAddress() {
        return deviceAddress;
    }

    public void sendCommandBufferClear() {
        commandBuffer.clear();
    }

    public void sendCommandFlush() {
        byte[] payload = new byte[commandBuffer.size()];
        for (int index = 0; index < commandBuffer.size(); ++index) {
            payload[index] = commandBuffer.get(index);
        }
        pendingPayload = payload;
        startPendingWriteIfIdle();
    }

    public void set(
            byte strand, byte pixel, byte red, byte blue, byte green, byte intensity, byte fadeMode) {
        addBuffer((byte) COMMAND_SET, fadeMode, strand, red, green, blue, pixel);
    }

    public void set_all(byte red, byte blue, byte green, byte intensity, byte fadeMode) {
        addBuffer((byte) COMMAND_SET_ALL, fadeMode, (byte) 0, red, green, blue, (byte) 0);
    }

    public void set_across(
            byte pixel, byte red, byte blue, byte green, byte intensity, byte fadeMode) {
        addBuffer((byte) COMMAND_SET_ACROSS, fadeMode, (byte) 0, red, green, blue, pixel);
    }

    public void set_subset(
            byte strandStart,
            byte pixel,
            byte red,
            byte blue,
            byte green,
            byte intensity,
            byte fadeMode) {
        addBuffer((byte) COMMAND_SET_SUBSET, fadeMode, strandStart, red, green, blue, pixel);
    }

    public void clear() {
        addBuffer((byte) COMMAND_CLEAR, (byte) 0, (byte) 0,
                (byte) 0, (byte) 0, (byte) 0, (byte) 0);
    }

    public void set_display(byte strandStart, byte intensity, byte fadeMode) {
        addBuffer((byte) COMMAND_SET_DISPLAY, fadeMode, strandStart,
                (byte) 0, (byte) 0, (byte) 0, (byte) 0);
    }

    public void addBuffer(
            byte command,
            byte fade,
            byte strand,
            byte red,
            byte blue,
            byte green,
            byte pixel) {
        commandBuffer.add((byte) ((command << 4) | (fade & 0x0f)));
        commandBuffer.add((byte) ((strand << 4) | (red & 0x0f)));
        commandBuffer.add((byte) (((green & 0x0f) << 4) | (blue & 0x0f)));
        commandBuffer.add((byte) (1 << (pixel + 1)));
    }

    public void readBattery() {
        readCharacteristic(batteryCharacteristic);
    }

    public void readManufacturerName() {
        readCharacteristic(manufacturerCharacteristic);
    }

    public void readModelNumberString() {
        readCharacteristic(modelCharacteristic);
    }

    public void readSerialNumber() {
        readCharacteristic(serialCharacteristic);
    }

    public void readHardwareRevision() {
        readCharacteristic(hardwareCharacteristic);
    }

    private void readCharacteristic(BluetoothGattCharacteristic characteristic) {
        BluetoothLeService service = bluetoothLeService;
        if (service != null && characteristic != null) {
            service.readCharacteristic(characteristic);
        }
    }

    private void startPendingWriteIfIdle() {
        if (writeInFlight || activePayload != null || pendingPayload == null) {
            return;
        }
        activePayload = pendingPayload;
        pendingPayload = null;
        activeOffset = 0;
        sendNextChunk();
    }

    private void sendNextChunk() {
        if (activePayload == null || writeInFlight) {
            return;
        }
        if (activeOffset >= activePayload.length) {
            activePayload = null;
            activeOffset = 0;
            startPendingWriteIfIdle();
            return;
        }
        int end = Math.min(activePayload.length, activeOffset + CHUNK_BYTES);
        byte[] chunk = Arrays.copyOfRange(activePayload, activeOffset, end);
        BluetoothLeService service = bluetoothLeService;
        if (service == null || ledCharacteristic == null
                || !service.writeCharacteristic(ledCharacteristic, chunk)) {
            Log.w(TAG, "Fret Zealot SDK rejected LED write");
            clearWrites();
            notifyDisconnected();
            return;
        }
        activeOffset = end;
        writeInFlight = true;
    }

    private void onWriteComplete(int status) {
        writeInFlight = false;
        if (status != BluetoothGatt.GATT_SUCCESS) {
            Log.w(TAG, "Fret Zealot LED write failed: " + status);
            clearWrites();
            notifyDisconnected();
            return;
        }
        sendNextChunk();
    }

    private void clearWrites() {
        commandBuffer.clear();
        activePayload = null;
        pendingPayload = null;
        activeOffset = 0;
        writeInFlight = false;
    }

    private void findCharacteristics(List<BluetoothGattService> services) {
        clearCharacteristics();
        for (BluetoothGattService service : services) {
            for (BluetoothGattCharacteristic characteristic : service.getCharacteristics()) {
                UUID uuid = characteristic.getUuid();
                if (SampleGattAttributes.LED_2_CH.equals(uuid)) {
                    ledCharacteristic = characteristic;
                } else if (SampleGattAttributes.LED_CH.equals(uuid) && ledCharacteristic == null) {
                    ledCharacteristic = characteristic;
                } else if (SampleGattAttributes.BATTERY.equals(uuid)) {
                    batteryCharacteristic = characteristic;
                } else if (SampleGattAttributes.MANUFACTURER_NAME.equals(uuid)) {
                    manufacturerCharacteristic = characteristic;
                } else if (SampleGattAttributes.MODEL_NUMBER.equals(uuid)) {
                    modelCharacteristic = characteristic;
                } else if (SampleGattAttributes.SERIAL_NUMBER.equals(uuid)) {
                    serialCharacteristic = characteristic;
                } else if (SampleGattAttributes.HARDWARE_REVISION.equals(uuid)) {
                    hardwareCharacteristic = characteristic;
                }
            }
        }
    }

    private void clearCharacteristics() {
        ledCharacteristic = null;
        batteryCharacteristic = null;
        manufacturerCharacteristic = null;
        modelCharacteristic = null;
        serialCharacteristic = null;
        hardwareCharacteristic = null;
    }

    private void dispatchRead(BluetoothGattCharacteristic characteristic, byte[] value) {
        LEDBLELibCallback current = callback;
        if (current == null || characteristic == null || value == null) {
            return;
        }
        UUID uuid = characteristic.getUuid();
        if (SampleGattAttributes.BATTERY.equals(uuid) && value.length > 0) {
            current.onBatteryString(Integer.toString(value[0] & 0xff));
        } else if (SampleGattAttributes.MANUFACTURER_NAME.equals(uuid)) {
            current.onManufactureNameString(new String(value));
        } else if (SampleGattAttributes.MODEL_NUMBER.equals(uuid)) {
            current.onModelNumberString(new String(value));
        } else if (SampleGattAttributes.SERIAL_NUMBER.equals(uuid)) {
            current.onSerialNumberString(new String(value));
        } else if (SampleGattAttributes.HARDWARE_REVISION.equals(uuid)) {
            current.onHardwareRevisionString(new String(value));
        } else {
            current.onDataReceived(value.clone());
        }
    }

    private void notifyDisconnected() {
        connected = false;
        clearCharacteristics();
        clearWrites();
        LEDBLELibCallback current = callback;
        if (current != null) {
            current.onDisconnected();
        }
    }

    private final BluetoothLeService.Listener serviceListener =
            new BluetoothLeService.Listener() {
                @Override
                public void onConnected() {
                    mainHandler.post(() -> {
                        connected = true;
                        LEDBLELibCallback current = callback;
                        if (current != null) {
                            current.onConnected();
                        }
                    });
                }

                @Override
                public void onDisconnected(int status) {
                    mainHandler.post(LEDBLELib.this::notifyDisconnected);
                }

                @Override
                public void onServicesDiscovered(List<BluetoothGattService> services, int status) {
                    List<BluetoothGattService> copy = new ArrayList<>(services);
                    mainHandler.post(() -> {
                        if (status == BluetoothGatt.GATT_SUCCESS) {
                            findCharacteristics(copy);
                        }
                        LEDBLELibCallback current = callback;
                        if (current != null) {
                            current.onServiceDiscovered(copy);
                        }
                    });
                }

                @Override
                public void onCharacteristicRead(
                        BluetoothGattCharacteristic characteristic, byte[] value, int status) {
                    if (status == BluetoothGatt.GATT_SUCCESS) {
                        mainHandler.post(() -> dispatchRead(characteristic, value));
                    }
                }

                @Override
                public void onCharacteristicChanged(
                        BluetoothGattCharacteristic characteristic, byte[] value) {
                    mainHandler.post(() -> dispatchRead(characteristic, value));
                }

                @Override
                public void onCharacteristicWrite(int status) {
                    mainHandler.post(() -> onWriteComplete(status));
                }
            };

    private final ServiceConnection serviceConnection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName name, IBinder binder) {
            BluetoothLeService.LocalBinder localBinder =
                    (BluetoothLeService.LocalBinder) binder;
            bluetoothLeService = localBinder.getService();
            bluetoothLeService.setListener(serviceListener);
            if (!bluetoothLeService.initialize() || !bluetoothLeService.connect(deviceAddress)) {
                notifyDisconnected();
            }
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {
            bluetoothLeService = null;
            notifyDisconnected();
        }
    };
}
