/*
 * Adapted and substantially modified from edgetechlabs/fz-android-sdk.
 * Licensed under the Apache License, Version 2.0; see ../../../../../../LICENSE.
 */
package com.fz.blelib;

import android.annotation.SuppressLint;
import android.app.Service;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattDescriptor;
import android.bluetooth.BluetoothGattService;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothProfile;
import android.bluetooth.BluetoothStatusCodes;
import android.content.Context;
import android.content.Intent;
import android.os.Binder;
import android.os.Build;
import android.os.IBinder;
import android.util.Log;
import java.util.Collections;
import java.util.List;

/**
 * Bound GATT service adapted from edgetechlabs/fz-android-sdk for current Android BLE APIs.
 */
public final class BluetoothLeService extends Service {
    private static final String TAG = "FretZealotGatt";
    private static final int DEFAULT_MTU = 23;
    private static final int REQUESTED_MTU = 517;

    interface Listener {
        void onConnected();
        void onDisconnected(int status);
        void onServicesDiscovered(List<BluetoothGattService> services, int status);
        void onCharacteristicRead(BluetoothGattCharacteristic characteristic, byte[] value, int status);
        void onCharacteristicChanged(BluetoothGattCharacteristic characteristic, byte[] value);
        void onCharacteristicWrite(int status);
    }

    private BluetoothAdapter bluetoothAdapter;
    private BluetoothGatt bluetoothGatt;
    private String bluetoothDeviceAddress;
    private Listener listener;
    private int negotiatedMtu = DEFAULT_MTU;
    private boolean serviceDiscoveryStarted;

    private final BluetoothGattCallback gattCallback = new BluetoothGattCallback() {
        @Override
        @SuppressLint("MissingPermission")
        public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
            if (gatt != bluetoothGatt) {
                closeGatt(gatt);
                return;
            }
            if (status == BluetoothGatt.GATT_SUCCESS
                    && newState == BluetoothProfile.STATE_CONNECTED) {
                Listener current = listener;
                if (current != null) {
                    current.onConnected();
                }
                try {
                    negotiatedMtu = DEFAULT_MTU;
                    serviceDiscoveryStarted = false;
                    if (Build.VERSION.SDK_INT < Build.VERSION_CODES.LOLLIPOP
                            || !gatt.requestMtu(REQUESTED_MTU)) {
                        discoverServices(gatt);
                    }
                } catch (SecurityException exception) {
                    Log.w(TAG, "Unable to prepare Fret Zealot services", exception);
                    notifyDisconnected(BluetoothGatt.GATT_FAILURE);
                }
            } else if (newState == BluetoothProfile.STATE_DISCONNECTED
                    || status != BluetoothGatt.GATT_SUCCESS) {
                notifyDisconnected(status);
            }
        }

        @Override
        public void onServicesDiscovered(BluetoothGatt gatt, int status) {
            Listener current = listener;
            if (gatt == bluetoothGatt && current != null) {
                current.onServicesDiscovered(gatt.getServices(), status);
            }
        }

        @Override
        public void onMtuChanged(BluetoothGatt gatt, int mtu, int status) {
            if (gatt != bluetoothGatt) {
                return;
            }
            if (status == BluetoothGatt.GATT_SUCCESS) {
                negotiatedMtu = mtu;
            } else {
                Log.w(TAG, "Fret Zealot MTU request failed: status=" + status);
            }
            discoverServices(gatt);
        }

        @Override
        public void onCharacteristicRead(
                BluetoothGatt gatt,
                BluetoothGattCharacteristic characteristic,
                byte[] value,
                int status) {
            Listener current = listener;
            if (gatt == bluetoothGatt && current != null) {
                current.onCharacteristicRead(characteristic, value.clone(), status);
            }
        }

        @Override
        @SuppressWarnings("deprecation")
        public void onCharacteristicRead(
                BluetoothGatt gatt, BluetoothGattCharacteristic characteristic, int status) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                return;
            }
            byte[] value = characteristic.getValue();
            Listener current = listener;
            if (gatt == bluetoothGatt && current != null && value != null) {
                current.onCharacteristicRead(characteristic, value.clone(), status);
            }
        }

        @Override
        public void onCharacteristicChanged(
                BluetoothGatt gatt,
                BluetoothGattCharacteristic characteristic,
                byte[] value) {
            Listener current = listener;
            if (gatt == bluetoothGatt && current != null) {
                current.onCharacteristicChanged(characteristic, value.clone());
            }
        }

        @Override
        @SuppressWarnings("deprecation")
        public void onCharacteristicChanged(
                BluetoothGatt gatt, BluetoothGattCharacteristic characteristic) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                return;
            }
            byte[] value = characteristic.getValue();
            Listener current = listener;
            if (gatt == bluetoothGatt && current != null && value != null) {
                current.onCharacteristicChanged(characteristic, value.clone());
            }
        }

        @Override
        public void onCharacteristicWrite(
                BluetoothGatt gatt, BluetoothGattCharacteristic characteristic, int status) {
            Listener current = listener;
            if (gatt == bluetoothGatt && current != null) {
                current.onCharacteristicWrite(status);
            }
        }
    };

    final class LocalBinder extends Binder {
        BluetoothLeService getService() {
            return BluetoothLeService.this;
        }
    }

    private final IBinder binder = new LocalBinder();

    @Override
    public IBinder onBind(Intent intent) {
        return binder;
    }

    @Override
    public boolean onUnbind(Intent intent) {
        close();
        return super.onUnbind(intent);
    }

    void setListener(Listener listener) {
        this.listener = listener;
    }

    boolean initialize() {
        BluetoothManager manager = (BluetoothManager) getSystemService(Context.BLUETOOTH_SERVICE);
        bluetoothAdapter = manager == null ? null : manager.getAdapter();
        return bluetoothAdapter != null;
    }

    @SuppressLint("MissingPermission")
    boolean connect(String address) {
        if (bluetoothAdapter == null || address == null || address.isEmpty()) {
            return false;
        }
        try {
            if (address.equals(bluetoothDeviceAddress) && bluetoothGatt != null) {
                return bluetoothGatt.connect();
            }
            close();
            BluetoothDevice device = bluetoothAdapter.getRemoteDevice(address);
            bluetoothGatt = device.connectGatt(
                    this, false, gattCallback, BluetoothDevice.TRANSPORT_LE);
            bluetoothDeviceAddress = address;
            return bluetoothGatt != null;
        } catch (IllegalArgumentException | SecurityException exception) {
            Log.w(TAG, "Unable to connect to Fret Zealot", exception);
            close();
            return false;
        }
    }

    @SuppressLint("MissingPermission")
    void disconnect() {
        if (bluetoothGatt == null) {
            return;
        }
        try {
            bluetoothGatt.disconnect();
        } catch (SecurityException exception) {
            Log.w(TAG, "Unable to disconnect Fret Zealot", exception);
        }
    }

    @SuppressLint("MissingPermission")
    void close() {
        BluetoothGatt gatt = bluetoothGatt;
        bluetoothGatt = null;
        bluetoothDeviceAddress = null;
        negotiatedMtu = DEFAULT_MTU;
        serviceDiscoveryStarted = false;
        closeGatt(gatt);
    }

    @SuppressLint("MissingPermission")
    private void closeGatt(BluetoothGatt gatt) {
        if (gatt == null) {
            return;
        }
        try {
            gatt.close();
        } catch (SecurityException exception) {
            Log.w(TAG, "Unable to close Fret Zealot GATT", exception);
        }
    }

    private void notifyDisconnected(int status) {
        Listener current = listener;
        if (current != null) {
            current.onDisconnected(status);
        }
    }

    @SuppressLint("MissingPermission")
    private void discoverServices(BluetoothGatt gatt) {
        if (serviceDiscoveryStarted || gatt != bluetoothGatt) {
            return;
        }
        serviceDiscoveryStarted = true;
        try {
            if (!gatt.discoverServices()) {
                notifyDisconnected(BluetoothGatt.GATT_FAILURE);
            }
        } catch (SecurityException exception) {
            Log.w(TAG, "Unable to discover Fret Zealot services", exception);
            notifyDisconnected(BluetoothGatt.GATT_FAILURE);
        }
    }

    int maxWritePayloadBytes() {
        return Math.max(1, negotiatedMtu - 3);
    }

    List<BluetoothGattService> getSupportedGattServices() {
        BluetoothGatt gatt = bluetoothGatt;
        return gatt == null ? Collections.emptyList() : gatt.getServices();
    }

    @SuppressLint("MissingPermission")
    boolean readCharacteristic(BluetoothGattCharacteristic characteristic) {
        if (bluetoothGatt == null || characteristic == null) {
            return false;
        }
        try {
            return bluetoothGatt.readCharacteristic(characteristic);
        } catch (SecurityException exception) {
            Log.w(TAG, "Unable to read Fret Zealot characteristic", exception);
            return false;
        }
    }

    @SuppressLint("MissingPermission")
    @SuppressWarnings("deprecation")
    boolean enableNotifications(BluetoothGattCharacteristic characteristic) {
        if (bluetoothGatt == null || characteristic == null) {
            return false;
        }
        try {
            if (!bluetoothGatt.setCharacteristicNotification(characteristic, true)) {
                return false;
            }
            BluetoothGattDescriptor descriptor =
                    characteristic.getDescriptor(SampleGattAttributes.CLIENT_CHARACTERISTIC_CONFIG);
            if (descriptor == null) {
                return false;
            }
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                return bluetoothGatt.writeDescriptor(
                        descriptor, BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE)
                        == BluetoothStatusCodes.SUCCESS;
            }
            descriptor.setValue(BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE);
            return bluetoothGatt.writeDescriptor(descriptor);
        } catch (SecurityException exception) {
            Log.w(TAG, "Unable to enable Fret Zealot notifications", exception);
            return false;
        }
    }

    @SuppressLint("MissingPermission")
    @SuppressWarnings("deprecation")
    boolean writeCharacteristic(BluetoothGattCharacteristic characteristic, byte[] value) {
        if (bluetoothGatt == null || characteristic == null || value == null) {
            return false;
        }
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                return bluetoothGatt.writeCharacteristic(
                        characteristic,
                        value,
                        BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT)
                        == BluetoothStatusCodes.SUCCESS;
            }
            characteristic.setWriteType(BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT);
            characteristic.setValue(value);
            return bluetoothGatt.writeCharacteristic(characteristic);
        } catch (SecurityException exception) {
            Log.w(TAG, "Unable to write Fret Zealot characteristic", exception);
            return false;
        }
    }
}
