package dev.benalu.musicanalyzer;

import android.Manifest;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattDescriptor;
import android.bluetooth.BluetoothGattService;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothProfile;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanRecord;
import android.bluetooth.le.ScanResult;
import android.content.Context;
import android.content.pm.PackageManager;
import android.media.midi.MidiDevice;
import android.media.midi.MidiDeviceInfo;
import android.media.midi.MidiDeviceStatus;
import android.media.midi.MidiInputPort;
import android.media.midi.MidiManager;
import android.media.midi.MidiOutputPort;
import android.media.midi.MidiReceiver;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.util.Log;
import java.io.Closeable;
import java.io.IOException;
import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Locale;
import java.util.UUID;

@SuppressWarnings("deprecation")
final class ExternalDeviceManager implements Closeable {
    private static final String TAG = "MusicAnalyzerDevices";

    private static final int DEVICE_LITEJAM = 0;
    private static final int DEVICE_FRET_ZEALOT = 1;
    private static final int DEVICE_APC_MINI = 2;
    private static final int DEVICE_MVAVE = 3;
    private static final int DEVICE_AUPHY_SCT_86PRO = 4;

    private static final int STATE_DISABLED = 0;
    private static final int STATE_SEARCHING = 1;
    private static final int STATE_CONNECTING = 2;
    private static final int STATE_CONNECTED = 3;
    private static final int STATE_ERROR = 4;

    private static final UUID LITEJAM_SERVICE = UUID.fromString("000000ee-0000-1000-8000-00805f9b34fb");
    private static final UUID LITEJAM_LED = UUID.fromString("0000ee04-0000-1000-8000-00805f9b34fb");
    private static final UUID BLE_MIDI_SERVICE = UUID.fromString("03b80e5a-ede8-4b33-a751-6ce34ec4c700");
    private static final UUID BLE_MIDI_IO = UUID.fromString("7772e5db-3868-4112-a1a9-f2669d106bf3");
    private static final UUID CLIENT_CHARACTERISTIC_CONFIG =
            UUID.fromString("00002902-0000-1000-8000-00805f9b34fb");

    private static final long MVAVE_HOLD_MILLIS = 600;
    private static final int REQUESTED_MTU = 247;
    private static final int BLE_CHUNK_BYTES = 20;
    private static final long WRITE_WITHOUT_RESPONSE_DELAY_MILLIS = 12;
    private static final long BLE_RETRY_DELAY_MILLIS = 1500;
    // A first-generation Fret Zealot takes a few hundred milliseconds to
    // apply a frame. Keep its last complete AUTO scale visible until a root
    // has been quiet long enough for one reliable two-phase replacement.
    // A full legacy-board replacement includes a target pass and a stale-pixel
    // clear pass. Do not start it until the estimator has stayed on one root
    // long enough for the previous full frame to be useful.
    private static final long FRET_ZEALOT_AUTO_ROOT_STABLE_MILLIS = 1250;
    private static final long FRET_ZEALOT_FRAME_IDLE_RETRY_MILLIS = 100;

    private final Context context;
    private final long nativeHandle;
    private final Runnable invalidateDisplay;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final BleTarget liteJam = new BleTarget(DEVICE_LITEJAM, false);
    private final FretZealotSdkController fretZealot;
    private final AuphySct86ProController auphySct86Pro;
    private final boolean[] deviceAutoconnect = {false, true, true, false, false};
    private final boolean[] mvavePressed = new boolean[4];
    private final long[] mvavePressedAt = new long[4];

    private BluetoothAdapter bluetoothAdapter;
    private BluetoothLeScanner bleScanner;
    private boolean scanning;
    private boolean started;
    private boolean autoconnect = true;
    private long lastOutputRevision;
    private byte[] lastFretZealotPacket;
    private byte[] pendingFretZealotPacket;
    // AUTO-root revisions are debounced before they reach the legacy board.
    // While the estimator is still changing, keep its last complete scale
    // rather than risking a partly applied replacement.
    private boolean fretZealotAutoReconciliationScheduled;
    private final Runnable sendStableFretZealotPacket;

    private MidiManager midiManager;
    private boolean midiCallbackRegistered;
    private boolean apcOpening;
    private boolean mvaveOpening;
    private MidiConnection apcConnection;
    private MidiConnection mvaveConnection;
    private BluetoothGatt mvaveGatt;
    private BluetoothGattCharacteristic mvaveGattCharacteristic;
    private boolean mvaveGattConnecting;
    private boolean mvaveGattSubscribed;
    private int mvaveBleRunningStatus;

    ExternalDeviceManager(Context context, long nativeHandle, Runnable invalidateDisplay) {
        this.context = context;
        this.nativeHandle = nativeHandle;
        this.invalidateDisplay = invalidateDisplay;
        fretZealot = new FretZealotSdkController(context, new FretZealotSdkController.Listener() {
            @Override
            public void onConnecting() {
                setDeviceState(DEVICE_FRET_ZEALOT, STATE_CONNECTING);
            }

            @Override
            public void onReady() {
                setDeviceState(DEVICE_FRET_ZEALOT, STATE_CONNECTED);
                refreshOutputs(true);
                if (allEnabledBleDevicesConnected()) {
                    stopBleScan();
                }
            }

            @Override
            public void onDisconnected() {
                setDeviceState(DEVICE_FRET_ZEALOT,
                        shouldAutoconnectDevice(DEVICE_FRET_ZEALOT)
                                ? STATE_SEARCHING : STATE_DISABLED);
                scheduleBleScanRetry();
            }

            @Override
            public void onError() {
                setDeviceState(DEVICE_FRET_ZEALOT,
                        shouldAutoconnectDevice(DEVICE_FRET_ZEALOT)
                                ? STATE_ERROR : STATE_DISABLED);
                scheduleBleScanRetry();
            }
        });
        auphySct86Pro = new AuphySct86ProController(context, new AuphySct86ProController.Listener() {
            @Override
            public void onConnecting() {
                setDeviceState(DEVICE_AUPHY_SCT_86PRO, STATE_CONNECTING);
            }

            @Override
            public void onReady() {
                setDeviceState(DEVICE_AUPHY_SCT_86PRO, STATE_CONNECTED);
                refreshOutputs(true);
                if (allEnabledBleDevicesConnected()) {
                    stopBleScan();
                }
            }

            @Override
            public void onLedCountChanged() {
                refreshOutputs(true);
            }

            @Override
            public void onDisconnected() {
                setDeviceState(DEVICE_AUPHY_SCT_86PRO,
                        shouldAutoconnectDevice(DEVICE_AUPHY_SCT_86PRO)
                                ? STATE_SEARCHING : STATE_DISABLED);
                scheduleBleScanRetry();
            }

            @Override
            public void onError() {
                setDeviceState(DEVICE_AUPHY_SCT_86PRO,
                        shouldAutoconnectDevice(DEVICE_AUPHY_SCT_86PRO)
                                ? STATE_ERROR : STATE_DISABLED);
                scheduleBleScanRetry();
            }
        });
        sendStableFretZealotPacket = () -> {
            if (!started || !fretZealot.isReady() || pendingFretZealotPacket == null) {
                fretZealotAutoReconciliationScheduled = false;
                return;
            }
            if (fretZealot.isScaleFrameInFlight()) {
                // Do not turn a stable update into a queued frame. A legacy
                // board can visibly retain only a prefix if a replacement
                // starts before its previous target/clear pass has settled.
                retryFretZealotAutoReconciliation();
                return;
            }
            byte[] packet = pendingFretZealotPacket;
            pendingFretZealotPacket = null;
            fretZealotAutoReconciliationScheduled = false;
            // A genuinely stable AUTO root gets one complete scale replay.
            // Do not stream deltas while the estimator is still revising its
            // root: legacy boards can apply only a prefix of those frames.
            fretZealot.sendPacket(packet, true);
        };
    }

    void start() {
        if (started) {
            startBleScanIfAllowed();
            return;
        }
        started = true;
        startMidiDiscovery();
        startBleScanIfAllowed();
    }

    void onPermissionsChanged() {
        startBleScanIfAllowed();
    }

    void onAnalyzerChanged() {
        handler.post(() -> refreshOutputs(false));
    }

    void setAutoconnect(boolean enabled) {
        autoconnect = enabled;
        MusicAnalyzerNative.nativeSetAutoconnect(nativeHandle, enabled);
        if (enabled) {
            setDisconnectedDevicesSearching();
            startMidiDiscovery();
            startBleScanIfAllowed();
        } else {
            stopBleScan();
            closeBleTarget(liteJam, STATE_DISABLED);
            closeFretZealot(STATE_DISABLED);
            closeAuphySct86Pro(STATE_DISABLED);
            closeMidiConnection(true, STATE_DISABLED);
            closeMidiConnection(false, STATE_DISABLED);
            closeMvaveGatt(STATE_DISABLED);
        }
        invalidateDisplay.run();
    }

    void toggleDeviceAutoconnect(int device) {
        if (device < 0 || device >= deviceAutoconnect.length) {
            return;
        }
        setDeviceAutoconnect(device, !deviceAutoconnect[device]);
    }

    private void setDeviceAutoconnect(int device, boolean enabled) {
        if (deviceAutoconnect[device] == enabled) {
            return;
        }
        deviceAutoconnect[device] = enabled;
        if (!enabled || !autoconnect || !started) {
            switch (device) {
                case DEVICE_LITEJAM:
                    closeBleTarget(liteJam, STATE_DISABLED);
                    break;
                case DEVICE_FRET_ZEALOT:
                    closeFretZealot(STATE_DISABLED);
                    break;
                case DEVICE_AUPHY_SCT_86PRO:
                    closeAuphySct86Pro(STATE_DISABLED);
                    break;
                case DEVICE_APC_MINI:
                    closeMidiConnection(true, STATE_DISABLED);
                    break;
                case DEVICE_MVAVE:
                    closeMidiConnection(false, STATE_DISABLED);
                    closeMvaveGatt(STATE_DISABLED);
                    break;
                default:
                    break;
            }
            if (allEnabledBleDevicesConnected()) {
                stopBleScan();
            }
        } else {
            setDeviceState(device, STATE_SEARCHING);
            if (device == DEVICE_APC_MINI || device == DEVICE_MVAVE) {
                startMidiDiscovery();
            }
            if (device != DEVICE_APC_MINI) {
                startBleScanIfAllowed();
            }
        }
        invalidateDisplay.run();
    }

    private boolean shouldAutoconnectDevice(int device) {
        return started && autoconnect && device >= 0 && device < deviceAutoconnect.length
                && deviceAutoconnect[device];
    }

    private boolean hasEnabledBleDevice() {
        return deviceAutoconnect[DEVICE_LITEJAM]
                || deviceAutoconnect[DEVICE_FRET_ZEALOT]
                || deviceAutoconnect[DEVICE_AUPHY_SCT_86PRO]
                || deviceAutoconnect[DEVICE_MVAVE];
    }

    private boolean allEnabledBleDevicesConnected() {
        return (!deviceAutoconnect[DEVICE_LITEJAM] || liteJam.characteristic != null)
                && (!deviceAutoconnect[DEVICE_FRET_ZEALOT] || fretZealot.isReady())
                && (!deviceAutoconnect[DEVICE_AUPHY_SCT_86PRO] || auphySct86Pro.isReady())
                && (!deviceAutoconnect[DEVICE_MVAVE] || hasMvaveConnection());
    }

    @Override
    public void close() {
        started = false;
        stopBleScan();
        closeBleTarget(liteJam, STATE_DISABLED);
        closeFretZealot(STATE_DISABLED);
        closeAuphySct86Pro(STATE_DISABLED);
        closeMidiConnection(true, STATE_DISABLED);
        closeMidiConnection(false, STATE_DISABLED);
        closeMvaveGatt(STATE_DISABLED);
        if (midiManager != null && midiCallbackRegistered) {
            midiManager.unregisterDeviceCallback(midiDeviceCallback);
            midiCallbackRegistered = false;
        }
        handler.removeCallbacksAndMessages(null);
    }

    private boolean hasBlePermissions() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.S) {
            return context.checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)
                    == PackageManager.PERMISSION_GRANTED;
        }
        return context.checkSelfPermission(Manifest.permission.BLUETOOTH_SCAN) == PackageManager.PERMISSION_GRANTED
                && context.checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT)
                == PackageManager.PERMISSION_GRANTED;
    }

    private void setDeviceState(int device, int state) {
        Log.d(TAG, "Device state " + device + " -> " + state);
        MusicAnalyzerNative.nativeSetDeviceState(nativeHandle, device, state);
        invalidateDisplay.run();
    }

    private void setDisconnectedDevicesSearching() {
        if (shouldAutoconnectDevice(DEVICE_LITEJAM) && liteJam.gatt == null) {
            setDeviceState(DEVICE_LITEJAM, STATE_SEARCHING);
        }
        if (shouldAutoconnectDevice(DEVICE_FRET_ZEALOT) && !fretZealot.isActive()) {
            setDeviceState(DEVICE_FRET_ZEALOT, STATE_SEARCHING);
        }
        if (shouldAutoconnectDevice(DEVICE_AUPHY_SCT_86PRO) && !auphySct86Pro.isActive()) {
            setDeviceState(DEVICE_AUPHY_SCT_86PRO, STATE_SEARCHING);
        }
        if (shouldAutoconnectDevice(DEVICE_APC_MINI) && apcConnection == null && !apcOpening) {
            setDeviceState(DEVICE_APC_MINI, STATE_SEARCHING);
        }
        if (shouldAutoconnectDevice(DEVICE_MVAVE) && !hasMvaveConnection() && !isMvaveOpening()) {
            setDeviceState(DEVICE_MVAVE, STATE_SEARCHING);
        }
    }

    private void startBleScanIfAllowed() {
        if (!started || !autoconnect || !hasEnabledBleDevice()) {
            return;
        }
        if (!hasBlePermissions()) {
            if (deviceAutoconnect[DEVICE_LITEJAM]) {
                setDeviceState(DEVICE_LITEJAM, STATE_DISABLED);
            }
            if (deviceAutoconnect[DEVICE_FRET_ZEALOT]) {
                setDeviceState(DEVICE_FRET_ZEALOT, STATE_DISABLED);
            }
            if (deviceAutoconnect[DEVICE_AUPHY_SCT_86PRO]) {
                setDeviceState(DEVICE_AUPHY_SCT_86PRO, STATE_DISABLED);
            }
            if (deviceAutoconnect[DEVICE_MVAVE]) {
                setDeviceState(DEVICE_MVAVE, STATE_DISABLED);
            }
            return;
        }
        BluetoothManager manager = context.getSystemService(BluetoothManager.class);
        bluetoothAdapter = manager == null ? null : manager.getAdapter();
        if (bluetoothAdapter == null || !bluetoothAdapter.isEnabled()) {
            if (deviceAutoconnect[DEVICE_LITEJAM]) {
                setDeviceState(DEVICE_LITEJAM, STATE_ERROR);
            }
            if (deviceAutoconnect[DEVICE_FRET_ZEALOT]) {
                setDeviceState(DEVICE_FRET_ZEALOT, STATE_ERROR);
            }
            if (deviceAutoconnect[DEVICE_AUPHY_SCT_86PRO]) {
                setDeviceState(DEVICE_AUPHY_SCT_86PRO, STATE_ERROR);
            }
            if (deviceAutoconnect[DEVICE_MVAVE]) {
                setDeviceState(DEVICE_MVAVE, STATE_ERROR);
            }
            return;
        }
        openBondedMvaveIfAvailable();
        if (shouldAutoconnectDevice(DEVICE_LITEJAM) && liteJam.gatt == null) {
            setDeviceState(DEVICE_LITEJAM, STATE_SEARCHING);
        }
        if (shouldAutoconnectDevice(DEVICE_FRET_ZEALOT) && !fretZealot.isActive()) {
            setDeviceState(DEVICE_FRET_ZEALOT, STATE_SEARCHING);
        }
        if (shouldAutoconnectDevice(DEVICE_AUPHY_SCT_86PRO) && !auphySct86Pro.isActive()) {
            setDeviceState(DEVICE_AUPHY_SCT_86PRO, STATE_SEARCHING);
        }
        if (scanning || allEnabledBleDevicesConnected()) {
            return;
        }
        bleScanner = bluetoothAdapter.getBluetoothLeScanner();
        if (bleScanner == null) {
            if (deviceAutoconnect[DEVICE_LITEJAM]) {
                setDeviceState(DEVICE_LITEJAM, STATE_ERROR);
            }
            if (deviceAutoconnect[DEVICE_FRET_ZEALOT]) {
                setDeviceState(DEVICE_FRET_ZEALOT, STATE_ERROR);
            }
            if (deviceAutoconnect[DEVICE_AUPHY_SCT_86PRO]) {
                setDeviceState(DEVICE_AUPHY_SCT_86PRO, STATE_ERROR);
            }
            if (deviceAutoconnect[DEVICE_MVAVE]) {
                setDeviceState(DEVICE_MVAVE, STATE_ERROR);
            }
            return;
        }
        try {
            bleScanner.startScan(scanCallback);
            scanning = true;
        } catch (SecurityException exception) {
            Log.w(TAG, "BLE scan permission denied", exception);
            if (deviceAutoconnect[DEVICE_LITEJAM]) {
                setDeviceState(DEVICE_LITEJAM, STATE_ERROR);
            }
            if (deviceAutoconnect[DEVICE_FRET_ZEALOT]) {
                setDeviceState(DEVICE_FRET_ZEALOT, STATE_ERROR);
            }
            if (deviceAutoconnect[DEVICE_AUPHY_SCT_86PRO]) {
                setDeviceState(DEVICE_AUPHY_SCT_86PRO, STATE_ERROR);
            }
            if (deviceAutoconnect[DEVICE_MVAVE]) {
                setDeviceState(DEVICE_MVAVE, STATE_ERROR);
            }
        }
    }

    private void stopBleScan() {
        if (!scanning || bleScanner == null) {
            scanning = false;
            return;
        }
        try {
            bleScanner.stopScan(scanCallback);
        } catch (SecurityException exception) {
            Log.w(TAG, "Unable to stop BLE scan", exception);
        }
        scanning = false;
    }

    private String scanName(ScanResult result) {
        ScanRecord record = result.getScanRecord();
        String name = record == null ? null : record.getDeviceName();
        if (name == null) {
            try {
                name = result.getDevice().getName();
            } catch (SecurityException ignored) {
                name = null;
            }
        }
        return name == null ? "" : name.toLowerCase(Locale.ROOT);
    }

    private boolean isLiteJamName(String name) {
        return name.startsWith("lite jam rgb") || name.contains("litejam") || name.contains("lite jam");
    }

    private boolean isFretZealotName(String name) {
        return name.contains("fret zealot") || name.contains("fretzealot");
    }

    private boolean isAuphySct86ProName(String name) {
        // Official FretSpark AUPHY patterns: SCT-86PRO-XXXX with optional
        // hyphen/underscore/space separators. OTA advertisements are not
        // runtime LED devices and intentionally do not match this expression.
        return name.matches("^sct[-_ ]?86pro[-_][a-z0-9]{4}$");
    }

    private boolean isMvaveBleName(String name) {
        return name.contains("chocolate") || name.contains("m-vave") || name.contains("mvave")
                || name.contains("footctrl");
    }

    private void openBondedMvaveIfAvailable() {
        if (!shouldAutoconnectDevice(DEVICE_MVAVE) || bluetoothAdapter == null
                || hasMvaveConnection() || isMvaveOpening()) {
            return;
        }
        try {
            for (BluetoothDevice device : bluetoothAdapter.getBondedDevices()) {
                String name = device.getName();
                if (name != null && isMvaveBleName(name.toLowerCase(Locale.ROOT))) {
                    Log.i(TAG, "Opening bonded M-VAVE BLE-MIDI device: " + name);
                    connectMvaveGatt(device);
                    return;
                }
            }
        } catch (SecurityException exception) {
            Log.w(TAG, "Unable to inspect bonded M-VAVE devices", exception);
        }
    }

    private boolean hasMvaveConnection() {
        return mvaveConnection != null || mvaveGattSubscribed;
    }

    private boolean isMvaveOpening() {
        return mvaveOpening || mvaveGattConnecting || (mvaveGatt != null && !mvaveGattSubscribed);
    }

    private void connectMvaveGatt(BluetoothDevice device) {
        if (!shouldAutoconnectDevice(DEVICE_MVAVE) || hasMvaveConnection() || isMvaveOpening()) {
            return;
        }
        mvaveGattConnecting = true;
        setDeviceState(DEVICE_MVAVE, STATE_CONNECTING);
        try {
            mvaveGatt = device.connectGatt(context, false, mvaveGattCallback, BluetoothDevice.TRANSPORT_LE);
            if (mvaveGatt == null) {
                mvaveGattConnecting = false;
                setDeviceState(DEVICE_MVAVE, STATE_ERROR);
                scheduleBleScanRetry();
            }
        } catch (SecurityException exception) {
            mvaveGattConnecting = false;
            setDeviceState(DEVICE_MVAVE, STATE_ERROR);
            scheduleBleScanRetry();
            Log.w(TAG, "Unable to connect M-VAVE BLE-MIDI device", exception);
        }
    }

    private void closeMvaveGatt(int finalState) {
        BluetoothGatt gatt = mvaveGatt;
        mvaveGatt = null;
        mvaveGattCharacteristic = null;
        mvaveGattConnecting = false;
        mvaveGattSubscribed = false;
        mvaveBleRunningStatus = 0;
        Arrays.fill(mvavePressed, false);
        if (gatt != null) {
            try {
                gatt.disconnect();
                gatt.close();
            } catch (SecurityException exception) {
                Log.w(TAG, "Unable to close M-VAVE BLE-MIDI device", exception);
            }
        }
        setDeviceState(DEVICE_MVAVE, finalState);
    }

    private void failMvaveGatt() {
        closeMvaveGatt(shouldAutoconnectDevice(DEVICE_MVAVE) ? STATE_SEARCHING : STATE_DISABLED);
        scheduleBleScanRetry();
    }

    private void discoverMvaveServices(BluetoothGatt gatt) {
        try {
            if (!gatt.discoverServices()) {
                failMvaveGatt();
            }
        } catch (SecurityException exception) {
            Log.w(TAG, "Unable to discover M-VAVE BLE-MIDI service", exception);
            failMvaveGatt();
        }
    }

    private void configureMvaveGatt(BluetoothGatt gatt) {
        BluetoothGattCharacteristic characteristic =
                findCharacteristic(gatt, BLE_MIDI_SERVICE, BLE_MIDI_IO);
        if (characteristic == null) {
            Log.w(TAG, "M-VAVE device does not expose the standard BLE-MIDI characteristic");
            failMvaveGatt();
            return;
        }
        BluetoothGattDescriptor descriptor = characteristic.getDescriptor(CLIENT_CHARACTERISTIC_CONFIG);
        if (descriptor == null) {
            Log.w(TAG, "M-VAVE BLE-MIDI characteristic has no notification descriptor");
            failMvaveGatt();
            return;
        }
        int properties = characteristic.getProperties();
        byte[] descriptorValue = (properties & BluetoothGattCharacteristic.PROPERTY_NOTIFY) != 0
                ? BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
                : BluetoothGattDescriptor.ENABLE_INDICATION_VALUE;
        try {
            if (!gatt.setCharacteristicNotification(characteristic, true)) {
                failMvaveGatt();
                return;
            }
            boolean accepted;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                accepted = gatt.writeDescriptor(descriptor, descriptorValue)
                        == android.bluetooth.BluetoothStatusCodes.SUCCESS;
            } else {
                descriptor.setValue(descriptorValue);
                accepted = gatt.writeDescriptor(descriptor);
            }
            if (!accepted) {
                failMvaveGatt();
                return;
            }
            mvaveGattCharacteristic = characteristic;
        } catch (SecurityException exception) {
            Log.w(TAG, "Unable to subscribe to M-VAVE BLE-MIDI input", exception);
            failMvaveGatt();
        }
    }

    private void handleMvaveBlePacket(byte[] packet) {
        if (packet == null || packet.length < 2) {
            return;
        }
        StringBuilder raw = new StringBuilder();
        for (byte value : packet) {
            if (raw.length() > 0) {
                raw.append(' ');
            }
            raw.append(String.format(Locale.ROOT, "%02X", value & 0xff));
        }
        Log.d(TAG, "M-VAVE BLE raw: " + raw);

        int index = 1; // BLE-MIDI packet header.
        while (index < packet.length) {
            int timestamp = packet[index] & 0xff;
            if ((timestamp & 0x80) == 0) {
                ++index;
                continue;
            }
            ++index; // Every MIDI event starts with a timestamp-low byte.
            if (index >= packet.length) {
                break;
            }

            int value = packet[index] & 0xff;
            if ((value & 0x80) != 0) {
                ++index;
                if (value >= 0x80 && value < 0xf0) {
                    mvaveBleRunningStatus = value;
                } else if (value >= 0xf8) {
                    continue;
                } else {
                    mvaveBleRunningStatus = 0;
                    while (index < packet.length && (packet[index] & 0xff) < 0x80) {
                        ++index;
                    }
                    continue;
                }
            }
            if (mvaveBleRunningStatus == 0) {
                continue;
            }

            int message = mvaveBleRunningStatus & 0xf0;
            int dataBytes = (message == 0xc0 || message == 0xd0) ? 1 : 2;
            if (index + dataBytes > packet.length) {
                break;
            }
            int data1 = packet[index++] & 0x7f;
            int data2 = dataBytes == 2 ? packet[index++] & 0x7f : 0;
            handleMvaveMessage(mvaveBleRunningStatus, data1, data2);
        }
    }

    private void connectBle(BleTarget target, BluetoothDevice device) {
        if (!shouldAutoconnectDevice(target.deviceIndex) || target.gatt != null || target.connecting) {
            return;
        }
        target.connecting = true;
        setDeviceState(target.deviceIndex, STATE_CONNECTING);
        try {
            target.gatt = device.connectGatt(context, false, bleGattCallback, BluetoothDevice.TRANSPORT_LE);
            if (target.gatt == null) {
                target.connecting = false;
                setDeviceState(target.deviceIndex, STATE_ERROR);
                scheduleBleScanRetry();
            }
        } catch (SecurityException exception) {
            target.connecting = false;
            setDeviceState(target.deviceIndex, STATE_ERROR);
            scheduleBleScanRetry();
            Log.w(TAG, "Unable to connect BLE device", exception);
        }
    }

    private BleTarget targetForGatt(BluetoothGatt gatt) {
        if (liteJam.gatt == gatt) {
            return liteJam;
        }
        return null;
    }

    private void discoverServices(BluetoothGatt gatt) {
        try {
            if (!gatt.discoverServices()) {
                BleTarget target = targetForGatt(gatt);
                if (target != null) {
                    failBleTarget(target);
                }
            }
        } catch (SecurityException exception) {
            BleTarget target = targetForGatt(gatt);
            if (target != null) {
                failBleTarget(target);
            }
        }
    }

    private BluetoothGattCharacteristic findCharacteristic(
            BluetoothGatt gatt, UUID serviceUuid, UUID characteristicUuid) {
        BluetoothGattService service = gatt.getService(serviceUuid);
        return service == null ? null : service.getCharacteristic(characteristicUuid);
    }

    private void configureBleTarget(BleTarget target, BluetoothGatt gatt) {
        BluetoothGattCharacteristic characteristic =
                findCharacteristic(gatt, LITEJAM_SERVICE, LITEJAM_LED);
        if (characteristic == null) {
            failBleTarget(target);
            return;
        }
        target.characteristic = characteristic;
        target.connecting = false;
        setDeviceState(target.deviceIndex, STATE_CONNECTED);
        refreshOutputs(true);
        if (allEnabledBleDevicesConnected()) {
            stopBleScan();
        }
    }

    private void closeBleTarget(BleTarget target, int finalState) {
        BluetoothGatt gatt = target.gatt;
        target.clear();
        if (gatt != null) {
            try {
                gatt.disconnect();
                gatt.close();
            } catch (SecurityException exception) {
                Log.w(TAG, "Unable to close BLE device", exception);
            }
        }
        setDeviceState(target.deviceIndex, finalState);
    }

    private void closeFretZealot(int finalState) {
        handler.removeCallbacks(sendStableFretZealotPacket);
        pendingFretZealotPacket = null;
        fretZealotAutoReconciliationScheduled = false;
        lastFretZealotPacket = null;
        fretZealot.close();
        setDeviceState(DEVICE_FRET_ZEALOT, finalState);
    }

    private void closeAuphySct86Pro(int finalState) {
        auphySct86Pro.close();
        setDeviceState(DEVICE_AUPHY_SCT_86PRO, finalState);
    }

    private void closeGattQuietly(BluetoothGatt gatt) {
        try {
            gatt.close();
        } catch (SecurityException exception) {
            Log.w(TAG, "Unable to close GATT client", exception);
        }
    }

    private void failBleTarget(BleTarget target) {
        closeBleTarget(target,
                shouldAutoconnectDevice(target.deviceIndex) ? STATE_ERROR : STATE_DISABLED);
        scheduleBleScanRetry();
    }

    private void scheduleBleScanRetry() {
        if (!started || !autoconnect || !hasEnabledBleDevice()) {
            return;
        }
        handler.postDelayed(() -> {
            if (shouldAutoconnectDevice(DEVICE_MVAVE)
                    && !hasMvaveConnection() && !isMvaveOpening()) {
                setDeviceState(DEVICE_MVAVE, STATE_SEARCHING);
            }
            startBleScanIfAllowed();
        }, BLE_RETRY_DELAY_MILLIS);
    }

    private void writeNext(BleTarget target) {
        if (target.writing || target.gatt == null || target.characteristic == null) {
            return;
        }
        byte[] value = target.writeQueue.pollFirst();
        if (value == null) {
            return;
        }
        int properties = target.characteristic.getProperties();
        boolean noResponse = (properties & BluetoothGattCharacteristic.PROPERTY_WRITE_NO_RESPONSE) != 0;
        int writeType = noResponse
                ? BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE
                : BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT;
        boolean accepted;
        try {
            target.writing = true;
            target.writeWithoutResponse = noResponse;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                accepted = target.gatt.writeCharacteristic(target.characteristic, value, writeType)
                        == android.bluetooth.BluetoothStatusCodes.SUCCESS;
            } else {
                target.characteristic.setWriteType(writeType);
                target.characteristic.setValue(value);
                accepted = target.gatt.writeCharacteristic(target.characteristic);
            }
        } catch (SecurityException exception) {
            accepted = false;
        }
        if (!accepted) {
            target.writing = false;
            target.writeQueue.clear();
            failBleTarget(target);
            return;
        }
        if (noResponse) {
            handler.postDelayed(() -> {
                if (target.gatt == null) {
                    return;
                }
                target.writing = false;
                writeNext(target);
            }, WRITE_WITHOUT_RESPONSE_DELAY_MILLIS);
        }
    }

    private void queuePacket(BleTarget target, byte[] packet) {
        if (target.gatt == null || target.characteristic == null || packet == null || packet.length == 0) {
            return;
        }
        target.writeQueue.clear();
        if (!target.chunkWrites) {
            target.writeQueue.add(Arrays.copyOf(packet, packet.length));
        } else {
            for (int offset = 0; offset < packet.length; offset += BLE_CHUNK_BYTES) {
                int end = Math.min(packet.length, offset + BLE_CHUNK_BYTES);
                target.writeQueue.add(Arrays.copyOfRange(packet, offset, end));
            }
        }
        writeNext(target);
    }

    private void refreshOutputs(boolean force) {
        if (!started || nativeHandle == 0) {
            return;
        }
        long revision = MusicAnalyzerNative.nativeGetControlRevision(nativeHandle);
        if (!force && revision == lastOutputRevision) {
            return;
        }
        lastOutputRevision = revision;
        if (apcConnection != null && apcConnection.inputPort != null) {
            sendMidi(apcConnection.inputPort, MusicAnalyzerNative.nativeGetApcLedMessages(nativeHandle));
        }
        if (liteJam.characteristic != null) {
            queuePacket(liteJam, MusicAnalyzerNative.nativeGetLiteJamPacket(nativeHandle));
        }
        refreshFretZealotOutput(force);
        if (auphySct86Pro.isReady()) {
            auphySct86Pro.sendScalePixels(
                    MusicAnalyzerNative.nativeGetAuphyScalePixels(nativeHandle, auphySct86Pro.maxFret()));
        }
        invalidateDisplay.run();
    }

    private void refreshFretZealotOutput(boolean force) {
        if (!fretZealot.isReady()) {
            return;
        }
        byte[] packet = MusicAnalyzerNative.nativeGetFretZealotPacket(nativeHandle);
        if (packet == null || packet.length == 0) {
            return;
        }
        if (!force && Arrays.equals(packet, lastFretZealotPacket)) {
            // A device-state revision can refresh outputs without changing the
            // scale. Preserve the delayed AUTO reconciliation in that case:
            // cancelling it leaves a first-generation board showing only the
            // portion of its preceding LED delta that it happened to apply.
            return;
        }
        lastFretZealotPacket = Arrays.copyOf(packet, packet.length);
        if (!MusicAnalyzerNative.nativeIsAutomaticRootMode(nativeHandle)) {
            handler.removeCallbacks(sendStableFretZealotPacket);
            pendingFretZealotPacket = null;
            fretZealotAutoReconciliationScheduled = false;
            // The controller clears the board once after each connection, then
            // writes this delta. Manual root changes consequently never blink.
            fretZealot.sendPacket(packet, false);
            return;
        }
        if (force) {
            // The first render after a new connection has no previous complete
            // AUTO scale to preserve. Send it directly; the controller's
            // session reset handles the board's initial blank state.
            handler.removeCallbacks(sendStableFretZealotPacket);
            pendingFretZealotPacket = null;
            fretZealotAutoReconciliationScheduled = false;
            fretZealot.sendPacket(packet, true);
            return;
        }
        pendingFretZealotPacket = Arrays.copyOf(packet, packet.length);
        // Preserve the last complete scale until the root has been quiet long
        // enough for the slow first-generation controller to apply one full
        // replacement. A constantly changing estimate must not stream frames
        // to the board: partial scales are worse than a briefly older root.
        handler.removeCallbacks(sendStableFretZealotPacket);
        fretZealotAutoReconciliationScheduled = true;
        handler.postDelayed(sendStableFretZealotPacket, FRET_ZEALOT_AUTO_ROOT_STABLE_MILLIS);
    }

    private void retryFretZealotAutoReconciliation() {
        handler.postDelayed(sendStableFretZealotPacket,
                FRET_ZEALOT_FRAME_IDLE_RETRY_MILLIS);
    }

    private void sendMidi(MidiInputPort inputPort, byte[] messages) {
        if (messages == null || messages.length == 0) {
            return;
        }
        try {
            inputPort.send(messages, 0, messages.length);
        } catch (IOException exception) {
            Log.w(TAG, "Unable to update APC LEDs", exception);
            setDeviceState(DEVICE_APC_MINI, STATE_ERROR);
        }
    }

    private void startMidiDiscovery() {
        if (!started || !autoconnect
                || (!deviceAutoconnect[DEVICE_APC_MINI] && !deviceAutoconnect[DEVICE_MVAVE])) {
            return;
        }
        if (midiManager == null) {
            midiManager = context.getSystemService(MidiManager.class);
        }
        if (midiManager == null) {
            if (deviceAutoconnect[DEVICE_APC_MINI]) {
                setDeviceState(DEVICE_APC_MINI, STATE_ERROR);
            }
            if (deviceAutoconnect[DEVICE_MVAVE]) {
                setDeviceState(DEVICE_MVAVE, STATE_ERROR);
            }
            return;
        }
        if (!midiCallbackRegistered) {
            midiManager.registerDeviceCallback(midiDeviceCallback, handler);
            midiCallbackRegistered = true;
        }
        setDisconnectedDevicesSearching();
        for (MidiDeviceInfo info : midiManager.getDevices()) {
            maybeOpenMidiDevice(info);
        }
    }

    private String midiDeviceName(MidiDeviceInfo info) {
        StringBuilder name = new StringBuilder();
        Bundle properties = info.getProperties();
        appendProperty(name, properties.getString(MidiDeviceInfo.PROPERTY_NAME));
        appendProperty(name, properties.getString(MidiDeviceInfo.PROPERTY_MANUFACTURER));
        appendProperty(name, properties.getString(MidiDeviceInfo.PROPERTY_PRODUCT));
        for (MidiDeviceInfo.PortInfo port : info.getPorts()) {
            appendProperty(name, port.getName());
        }
        return name.toString().toLowerCase(Locale.ROOT);
    }

    private void appendProperty(StringBuilder output, String value) {
        if (value != null && !value.trim().isEmpty()) {
            output.append(' ').append(value);
        }
    }

    private boolean isApcName(String name) {
        return name.contains("apc mini mk2") || (name.contains("apc") && name.contains("mini"));
    }

    private boolean isMvaveName(String name) {
        return name.contains("chocolate") || name.contains("m-vave") || name.contains("mvave")
                || name.contains("footctrl");
    }

    private void maybeOpenMidiDevice(MidiDeviceInfo info) {
        if (!started || !autoconnect) {
            return;
        }
        String name = midiDeviceName(info);
        if (isApcName(name) && shouldAutoconnectDevice(DEVICE_APC_MINI)
                && apcConnection == null && !apcOpening) {
            openMidiDevice(info, true);
        } else if (isMvaveName(name) && shouldAutoconnectDevice(DEVICE_MVAVE)
                && info.getType() != MidiDeviceInfo.TYPE_BLUETOOTH
                && !hasMvaveConnection()
                && !isMvaveOpening()) {
            openMidiDevice(info, false);
        }
    }

    private void openMidiDevice(MidiDeviceInfo info, boolean apc) {
        if (apc) {
            apcOpening = true;
            setDeviceState(DEVICE_APC_MINI, STATE_CONNECTING);
        } else {
            mvaveOpening = true;
            setDeviceState(DEVICE_MVAVE, STATE_CONNECTING);
        }
        midiManager.openDevice(info, device -> finishOpenMidiDevice(device, apc), handler);
    }

    private void finishOpenMidiDevice(MidiDevice device, boolean apc) {
        if (apc) {
            apcOpening = false;
        } else {
            mvaveOpening = false;
        }
        int deviceIndex = apc ? DEVICE_APC_MINI : DEVICE_MVAVE;
        if (device == null || !shouldAutoconnectDevice(deviceIndex)) {
            Log.w(TAG, (apc ? "APC" : "M-VAVE") + " MIDI device open returned no usable device");
            closeQuietly(device);
            setDeviceState(deviceIndex,
                    shouldAutoconnectDevice(deviceIndex) ? STATE_ERROR : STATE_DISABLED);
            return;
        }
        MidiConnection connection = createMidiConnection(device, apc);
        if (connection == null) {
            Log.w(TAG, (apc ? "APC" : "M-VAVE") + " MIDI device has no readable output port");
            closeQuietly(device);
            setDeviceState(apc ? DEVICE_APC_MINI : DEVICE_MVAVE, STATE_ERROR);
            return;
        }
        if (apc) {
            closeMidiConnection(true, STATE_CONNECTED);
            apcConnection = connection;
            setDeviceState(DEVICE_APC_MINI, STATE_CONNECTED);
        } else {
            closeMidiConnection(false, STATE_CONNECTED);
            mvaveConnection = connection;
            setDeviceState(DEVICE_MVAVE, STATE_CONNECTED);
            Log.i(TAG, "M-VAVE MIDI connected: " + midiDeviceName(device.getInfo()));
        }
        refreshOutputs(true);
        if (allEnabledBleDevicesConnected()) {
            stopBleScan();
        }
    }

    private MidiConnection createMidiConnection(MidiDevice device, boolean apc) {
        MidiInputPort inputPort = null;
        MidiOutputPort outputPort = null;
        for (MidiDeviceInfo.PortInfo portInfo : device.getInfo().getPorts()) {
            if (outputPort == null && portInfo.getType() == MidiDeviceInfo.PortInfo.TYPE_OUTPUT) {
                outputPort = device.openOutputPort(portInfo.getPortNumber());
            }
            if (apc && inputPort == null && portInfo.getType() == MidiDeviceInfo.PortInfo.TYPE_INPUT) {
                inputPort = device.openInputPort(portInfo.getPortNumber());
            }
        }
        if (outputPort == null) {
            closeQuietly(inputPort);
            return null;
        }
        MidiStreamReceiver receiver = new MidiStreamReceiver(apc);
        outputPort.connect(receiver);
        return new MidiConnection(device, inputPort, outputPort, receiver);
    }

    private void closeMidiConnection(boolean apc, int finalState) {
        MidiConnection connection = apc ? apcConnection : mvaveConnection;
        if (connection != null) {
            connection.close();
        }
        if (apc) {
            apcConnection = null;
            apcOpening = false;
        } else {
            mvaveConnection = null;
            mvaveOpening = false;
            Arrays.fill(mvavePressed, false);
        }
        setDeviceState(apc ? DEVICE_APC_MINI : DEVICE_MVAVE, finalState);
    }

    private void handleApcMessage(int status, int data1, int data2) {
        if ((status & 0xf0) != 0x90 || data2 <= 0 || data1 < 0 || data1 >= 64) {
            return;
        }
        if (MusicAnalyzerNative.nativeHandleApcPad(nativeHandle, data1, data2)) {
            refreshOutputs(true);
        }
    }

    private int mvaveNoteToSwitch(int note) {
        if (note >= 0 && note <= 3) {
            return note;
        }
        if (note >= 36 && note <= 39) {
            return note - 36;
        }
        if (note >= 60 && note <= 63) {
            return note - 60;
        }
        return note % 4;
    }

    private int mvaveProgramToSwitch(int program) {
        int displayedSuffix = (program + 1) % 10;
        if (displayedSuffix >= 1 && displayedSuffix <= 4) {
            return displayedSuffix - 1;
        }
        if (displayedSuffix == 5 || displayedSuffix == 6) {
            return -1;
        }
        return program % 4;
    }

    private int mvaveControlToSwitch(int controller) {
        if (controller >= 32 && controller <= 35) {
            return controller - 32;
        }
        return controller % 4;
    }

    private void mvaveTap(int switchIndex) {
        if (switchIndex >= 0 && switchIndex < mvavePressed.length
                && MusicAnalyzerNative.nativeHandleMvaveSwitch(nativeHandle, switchIndex, false)) {
            refreshOutputs(true);
        }
    }

    private void mvavePress(int switchIndex) {
        if (switchIndex < 0 || switchIndex >= mvavePressed.length) {
            return;
        }
        mvavePressed[switchIndex] = true;
        mvavePressedAt[switchIndex] = SystemClock.uptimeMillis();
        mvaveTap(switchIndex);
    }

    private void mvaveRelease(int switchIndex) {
        if (switchIndex < 0 || switchIndex >= mvavePressed.length || !mvavePressed[switchIndex]) {
            return;
        }
        mvavePressed[switchIndex] = false;
        boolean held = SystemClock.uptimeMillis() - mvavePressedAt[switchIndex] >= MVAVE_HOLD_MILLIS;
        boolean changed = false;
        if (held && (switchIndex == 0 || switchIndex == 1)) {
            changed = MusicAnalyzerNative.nativeHandleMvaveSwitch(nativeHandle, switchIndex, false);
        }
        if (changed) {
            refreshOutputs(true);
        }
    }

    private void handleMvaveMessage(int status, int data1, int data2) {
        Log.d(TAG, String.format(Locale.ROOT, "M-VAVE MIDI %02X %d %d", status, data1, data2));
        int message = status & 0xf0;
        if (message == 0x90 || message == 0x80) {
            int switchIndex = mvaveNoteToSwitch(data1);
            if (message == 0x90 && data2 > 0) {
                mvavePress(switchIndex);
            } else {
                mvaveRelease(switchIndex);
            }
        } else if (message == 0xb0) {
            int switchIndex = mvaveControlToSwitch(data1);
            if (data2 >= 64) {
                mvavePress(switchIndex);
            } else if (mvavePressed[switchIndex]) {
                mvaveRelease(switchIndex);
            } else {
                // Some M-VAVE custom-control presets emit one low-valued CC on press,
                // rather than a high-value press followed by a zero-value release.
                mvaveTap(switchIndex);
            }
        } else if (message == 0xc0) {
            int switchIndex = mvaveProgramToSwitch(data1);
            mvaveTap(switchIndex);
        }
    }

    private static void closeQuietly(Closeable closeable) {
        if (closeable == null) {
            return;
        }
        try {
            closeable.close();
        } catch (IOException ignored) {
        }
    }

    private final ScanCallback scanCallback = new ScanCallback() {
        @Override
        public void onScanResult(int callbackType, ScanResult result) {
            String name = scanName(result);
            if (isLiteJamName(name)) {
                connectBle(liteJam, result.getDevice());
            } else if (isFretZealotName(name)) {
                if (shouldAutoconnectDevice(DEVICE_FRET_ZEALOT)) {
                    fretZealot.connect(result.getDevice());
                }
            } else if (isAuphySct86ProName(name)) {
                if (shouldAutoconnectDevice(DEVICE_AUPHY_SCT_86PRO)) {
                    auphySct86Pro.connect(result.getDevice());
                }
            } else if (isMvaveBleName(name)) {
                connectMvaveGatt(result.getDevice());
            }
        }

        @Override
        public void onScanFailed(int errorCode) {
            scanning = false;
            Log.w(TAG, "BLE scan failed: " + errorCode);
            if (shouldAutoconnectDevice(DEVICE_LITEJAM) && liteJam.gatt == null) {
                setDeviceState(DEVICE_LITEJAM, STATE_ERROR);
            }
            if (shouldAutoconnectDevice(DEVICE_FRET_ZEALOT) && !fretZealot.isActive()) {
                setDeviceState(DEVICE_FRET_ZEALOT, STATE_ERROR);
            }
            if (shouldAutoconnectDevice(DEVICE_AUPHY_SCT_86PRO) && !auphySct86Pro.isActive()) {
                setDeviceState(DEVICE_AUPHY_SCT_86PRO, STATE_ERROR);
            }
            if (shouldAutoconnectDevice(DEVICE_MVAVE) && !hasMvaveConnection()) {
                setDeviceState(DEVICE_MVAVE, STATE_ERROR);
            }
            scheduleBleScanRetry();
        }
    };

    private final BluetoothGattCallback mvaveGattCallback = new BluetoothGattCallback() {
        @Override
        public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
            handler.post(() -> {
                if (gatt != mvaveGatt) {
                    closeGattQuietly(gatt);
                    return;
                }
                if (status == BluetoothGatt.GATT_SUCCESS && newState == BluetoothProfile.STATE_CONNECTED) {
                    mvaveGattConnecting = true;
                    setDeviceState(DEVICE_MVAVE, STATE_CONNECTING);
                    discoverMvaveServices(gatt);
                } else if (newState == BluetoothProfile.STATE_DISCONNECTED
                        || status != BluetoothGatt.GATT_SUCCESS) {
                    failMvaveGatt();
                }
            });
        }

        @Override
        public void onServicesDiscovered(BluetoothGatt gatt, int status) {
            handler.post(() -> {
                if (gatt != mvaveGatt) {
                    return;
                }
                if (status == BluetoothGatt.GATT_SUCCESS) {
                    configureMvaveGatt(gatt);
                } else {
                    failMvaveGatt();
                }
            });
        }

        @Override
        public void onDescriptorWrite(BluetoothGatt gatt, BluetoothGattDescriptor descriptor, int status) {
            handler.post(() -> {
                if (gatt != mvaveGatt
                        || !CLIENT_CHARACTERISTIC_CONFIG.equals(descriptor.getUuid())) {
                    return;
                }
                if (status != BluetoothGatt.GATT_SUCCESS || mvaveGattCharacteristic == null) {
                    failMvaveGatt();
                    return;
                }
                mvaveGattConnecting = false;
                mvaveGattSubscribed = true;
                mvaveBleRunningStatus = 0;
                setDeviceState(DEVICE_MVAVE, STATE_CONNECTED);
                Log.i(TAG, "M-VAVE direct BLE-MIDI connected");
                if (allEnabledBleDevicesConnected()) {
                    stopBleScan();
                }
            });
        }

        @Override
        public void onCharacteristicChanged(
                BluetoothGatt gatt, BluetoothGattCharacteristic characteristic, byte[] value) {
            if (gatt == mvaveGatt && BLE_MIDI_IO.equals(characteristic.getUuid())) {
                byte[] packet = Arrays.copyOf(value, value.length);
                handler.post(() -> handleMvaveBlePacket(packet));
            }
        }

        @Override
        public void onCharacteristicChanged(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                return;
            }
            byte[] value = characteristic.getValue();
            if (gatt == mvaveGatt && BLE_MIDI_IO.equals(characteristic.getUuid()) && value != null) {
                byte[] packet = Arrays.copyOf(value, value.length);
                handler.post(() -> handleMvaveBlePacket(packet));
            }
        }
    };

    private final BluetoothGattCallback bleGattCallback = new BluetoothGattCallback() {
        @Override
        public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
            handler.post(() -> {
                BleTarget target = targetForGatt(gatt);
                if (target == null) {
                    closeGattQuietly(gatt);
                    return;
                }
                if (status == BluetoothGatt.GATT_SUCCESS && newState == BluetoothProfile.STATE_CONNECTED) {
                    target.connecting = true;
                    setDeviceState(target.deviceIndex, STATE_CONNECTING);
                    try {
                        if (!gatt.requestMtu(REQUESTED_MTU)) {
                            discoverServices(gatt);
                        }
                    } catch (SecurityException exception) {
                        discoverServices(gatt);
                    }
                } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                    target.clear();
                    closeGattQuietly(gatt);
                    setDeviceState(target.deviceIndex,
                            shouldAutoconnectDevice(target.deviceIndex) ? STATE_SEARCHING : STATE_DISABLED);
                    startBleScanIfAllowed();
                } else if (status != BluetoothGatt.GATT_SUCCESS) {
                    closeBleTarget(target,
                            shouldAutoconnectDevice(target.deviceIndex) ? STATE_SEARCHING : STATE_DISABLED);
                    startBleScanIfAllowed();
                }
            });
        }

        @Override
        public void onMtuChanged(BluetoothGatt gatt, int mtu, int status) {
            handler.post(() -> {
                BleTarget target = targetForGatt(gatt);
                if (target != null && status == BluetoothGatt.GATT_SUCCESS) {
                    target.mtu = mtu;
                }
                discoverServices(gatt);
            });
        }

        @Override
        public void onServicesDiscovered(BluetoothGatt gatt, int status) {
            handler.post(() -> {
                BleTarget target = targetForGatt(gatt);
                if (target == null) {
                    return;
                }
                if (status == BluetoothGatt.GATT_SUCCESS) {
                    configureBleTarget(target, gatt);
                } else {
                    failBleTarget(target);
                }
            });
        }

        @Override
        public void onCharacteristicWrite(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic, int status) {
            handler.post(() -> {
                BleTarget target = targetForGatt(gatt);
                if (target == null || target.writeWithoutResponse) {
                    return;
                }
                target.writing = false;
                if (status == BluetoothGatt.GATT_SUCCESS) {
                    writeNext(target);
                } else {
                    target.writeQueue.clear();
                    failBleTarget(target);
                }
            });
        }
    };

    private final MidiManager.DeviceCallback midiDeviceCallback = new MidiManager.DeviceCallback() {
        @Override
        public void onDeviceAdded(MidiDeviceInfo device) {
            maybeOpenMidiDevice(device);
        }

        @Override
        public void onDeviceRemoved(MidiDeviceInfo device) {
            if (apcConnection != null && apcConnection.device.getInfo().getId() == device.getId()) {
                closeMidiConnection(true,
                        shouldAutoconnectDevice(DEVICE_APC_MINI) ? STATE_SEARCHING : STATE_DISABLED);
            }
            if (mvaveConnection != null && mvaveConnection.device.getInfo().getId() == device.getId()) {
                closeMidiConnection(false,
                        shouldAutoconnectDevice(DEVICE_MVAVE) ? STATE_SEARCHING : STATE_DISABLED);
            }
        }

        @Override
        public void onDeviceStatusChanged(MidiDeviceStatus status) {
            // Port availability changes are handled by add/remove callbacks and the open-device result.
        }
    };

    private final class MidiStreamReceiver extends MidiReceiver {
        private final boolean apc;
        private int runningStatus;
        private int firstData = -1;

        MidiStreamReceiver(boolean apc) {
            this.apc = apc;
        }

        @Override
        public void onSend(byte[] data, int offset, int count, long timestamp) {
            int end = offset + count;
            if (!apc && count > 0) {
                StringBuilder raw = new StringBuilder();
                for (int index = offset; index < end; ++index) {
                    if (raw.length() > 0) {
                        raw.append(' ');
                    }
                    raw.append(String.format(Locale.ROOT, "%02X", data[index] & 0xff));
                }
                Log.d(TAG, "M-VAVE raw: " + raw);
            }
            for (int index = offset; index < end; ++index) {
                int value = data[index] & 0xff;
                if ((value & 0x80) != 0) {
                    if (value < 0xf0) {
                        runningStatus = value;
                    } else if (value >= 0xf8) {
                        continue;
                    } else {
                        runningStatus = 0;
                    }
                    firstData = -1;
                    continue;
                }
                if (runningStatus == 0) {
                    continue;
                }
                int message = runningStatus & 0xf0;
                int dataBytes = (message == 0xc0 || message == 0xd0) ? 1 : 2;
                if (dataBytes == 1) {
                    dispatch(runningStatus, value, 0);
                } else if (firstData < 0) {
                    firstData = value;
                } else {
                    dispatch(runningStatus, firstData, value);
                    firstData = -1;
                }
            }
        }

        private void dispatch(int status, int data1, int data2) {
            handler.post(() -> {
                if (apc) {
                    handleApcMessage(status, data1, data2);
                } else {
                    handleMvaveMessage(status, data1, data2);
                }
            });
        }
    }

    private static final class MidiConnection implements Closeable {
        final MidiDevice device;
        final MidiInputPort inputPort;
        final MidiOutputPort outputPort;
        final MidiReceiver receiver;

        MidiConnection(
                MidiDevice device, MidiInputPort inputPort, MidiOutputPort outputPort, MidiReceiver receiver) {
            this.device = device;
            this.inputPort = inputPort;
            this.outputPort = outputPort;
            this.receiver = receiver;
        }

        @Override
        public void close() {
            if (outputPort != null) {
                outputPort.disconnect(receiver);
            }
            closeQuietly(inputPort);
            closeQuietly(outputPort);
            closeQuietly(device);
        }
    }

    private static final class BleTarget {
        final int deviceIndex;
        final boolean chunkWrites;
        final ArrayDeque<byte[]> writeQueue = new ArrayDeque<>();
        BluetoothGatt gatt;
        BluetoothGattCharacteristic characteristic;
        boolean connecting;
        boolean writing;
        boolean writeWithoutResponse;
        int mtu = 23;

        BleTarget(int deviceIndex, boolean chunkWrites) {
            this.deviceIndex = deviceIndex;
            this.chunkWrites = chunkWrites;
        }

        void clear() {
            gatt = null;
            characteristic = null;
            connecting = false;
            writing = false;
            writeWithoutResponse = false;
            writeQueue.clear();
            mtu = 23;
        }
    }
}
