/*
 * Adapted and modified from edgetechlabs/fz-android-sdk.
 * Licensed under the Apache License, Version 2.0; see ../../../../../../LICENSE.
 */
package com.fz.blelib;

import java.util.UUID;

/** Fret Zealot GATT identifiers from edgetechlabs/fz-android-sdk. */
public final class SampleGattAttributes {
    public static final UUID LED_SERVICE =
            UUID.fromString("6e400001-b5a3-f393-e0a9-e50e24dcca9e");
    public static final UUID LED_CH =
            UUID.fromString("6e400002-b5a3-f393-e0a9-e50e24dcca9e");
    public static final UUID LED_CH_NOTI =
            UUID.fromString("6e400003-b5a3-f393-e0a9-e50e24dcca9e");
    public static final UUID LED_2_SERVICE =
            UUID.fromString("fb1e4001-54ae-4a28-9f74-dfccb248601d");
    public static final UUID LED_2_CH =
            UUID.fromString("fb1e4002-54ae-4a28-9f74-dfccb248601d");

    public static final UUID BATTERY =
            UUID.fromString("00002a19-0000-1000-8000-00805f9b34fb");
    public static final UUID MANUFACTURER_NAME =
            UUID.fromString("00002a29-0000-1000-8000-00805f9b34fb");
    public static final UUID MODEL_NUMBER =
            UUID.fromString("00002a24-0000-1000-8000-00805f9b34fb");
    public static final UUID SERIAL_NUMBER =
            UUID.fromString("00002a25-0000-1000-8000-00805f9b34fb");
    public static final UUID HARDWARE_REVISION =
            UUID.fromString("00002a27-0000-1000-8000-00805f9b34fb");

    private SampleGattAttributes() {
    }
}
