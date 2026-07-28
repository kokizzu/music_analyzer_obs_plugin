/*
 * Adapted from edgetechlabs/fz-android-sdk and retained for API compatibility.
 * Licensed under the Apache License, Version 2.0; see ../../../../../../LICENSE.
 */
package com.fz.blelib;

import android.bluetooth.BluetoothGattService;
import java.util.List;

/** Callback API retained from edgetechlabs/fz-android-sdk. */
public interface LEDBLELibCallback {
    void onConnected();
    void onDisconnected();
    void onServiceDiscovered(List<BluetoothGattService> serviceList);
    void onDataReceived(byte[] rxBytes);
    void onBatteryString(String value);
    void onManufactureNameString(String value);
    void onModelNumberString(String value);
    void onSerialNumberString(String value);
    void onHardwareRevisionString(String value);
}
