#pragma once

#if defined(_WIN32)

#include <windows.h>

// The MinGW runtime used for the portable build does not ship the Windows SDK
// bluetoothleapis.h/bthledef.h headers. Keep the ABI declarations local and
// use the system BluetoothAPIs.dll at runtime.
typedef struct _MAO_BTH_LE_UUID {
	BOOLEAN IsShortUuid;
	union {
		USHORT ShortUuid;
		GUID LongUuid;
	} Value;
} MAO_BTH_LE_UUID;

typedef struct _MAO_BTH_LE_GATT_SERVICE {
	MAO_BTH_LE_UUID ServiceUuid;
	USHORT AttributeHandle;
} MAO_BTH_LE_GATT_SERVICE;

typedef struct _MAO_BTH_LE_GATT_CHARACTERISTIC {
	USHORT ServiceHandle;
	MAO_BTH_LE_UUID CharacteristicUuid;
	USHORT AttributeHandle;
	USHORT CharacteristicValueHandle;
	BOOLEAN IsBroadcastable;
	BOOLEAN IsReadable;
	BOOLEAN IsWritable;
	BOOLEAN IsWritableWithoutResponse;
	BOOLEAN IsSignedWritable;
	BOOLEAN IsNotifiable;
	BOOLEAN IsIndicatable;
	BOOLEAN HasExtendedProperties;
} MAO_BTH_LE_GATT_CHARACTERISTIC;

typedef struct _MAO_BTH_LE_GATT_CHARACTERISTIC_VALUE {
	ULONG DataSize;
	UCHAR Data[1];
} MAO_BTH_LE_GATT_CHARACTERISTIC_VALUE;

typedef ULONG64 MAO_BTH_LE_GATT_RELIABLE_WRITE_CONTEXT;

extern "C" {
HRESULT WINAPI BluetoothGATTGetServices(HANDLE, USHORT, MAO_BTH_LE_GATT_SERVICE *, USHORT *, ULONG);
HRESULT WINAPI BluetoothGATTGetCharacteristics(HANDLE, MAO_BTH_LE_GATT_SERVICE *, USHORT,
								MAO_BTH_LE_GATT_CHARACTERISTIC *, USHORT *, ULONG);
HRESULT WINAPI BluetoothGATTSetCharacteristicValue(HANDLE, MAO_BTH_LE_GATT_CHARACTERISTIC *,
								MAO_BTH_LE_GATT_CHARACTERISTIC_VALUE *,
								MAO_BTH_LE_GATT_RELIABLE_WRITE_CONTEXT, ULONG);
}

namespace mao {
namespace windows_bluetooth {

constexpr ULONG kGattFlagNone = 0x00000000;
constexpr ULONG kGattFlagWriteWithoutResponse = 0x00000020;

// SetupDi enumeration must use the GATT service interface. The generic LE
// device interface does not yield handles accepted by BluetoothGATTGetServices.
const GUID kBluetoothGattServiceInterface = {
	0x6e3bb679,
	0x4372,
	0x40c8,
	{0x9e, 0xaa, 0x45, 0x09, 0xdf, 0x26, 0x0c, 0xd8},
};

const GUID kFretZealotService = {
	0x6e400001,
	0xb5a3,
	0xf393,
	{0xe0, 0xa9, 0xe5, 0x0e, 0x24, 0xdc, 0xca, 0x9e},
};

const GUID kFretZealotWriteCharacteristic = {
	0x6e400002,
	0xb5a3,
	0xf393,
	{0xe0, 0xa9, 0xe5, 0x0e, 0x24, 0xdc, 0xca, 0x9e},
};

const GUID kFretZealot2Service = {
	0xfb1e4001,
	0x54ae,
	0x4a28,
	{0x9f, 0x74, 0xdf, 0xcc, 0xb2, 0x48, 0x60, 0x1d},
};

const GUID kFretZealot2WriteCharacteristic = {
	0xfb1e4002,
	0x54ae,
	0x4a28,
	{0x9f, 0x74, 0xdf, 0xcc, 0xb2, 0x48, 0x60, 0x1d},
};

constexpr USHORT kLiteJamServiceShortUuid = 0x00ee;
constexpr USHORT kLiteJamLedCharacteristicShortUuid = 0xee04;

const GUID kLiteJamService = {
	0x000000ee,
	0x0000,
	0x1000,
	{0x80, 0x00, 0x00, 0x80, 0x5f, 0x9b, 0x34, 0xfb},
};

const GUID kLiteJamLedCharacteristic = {
	0x0000ee04,
	0x0000,
	0x1000,
	{0x80, 0x00, 0x00, 0x80, 0x5f, 0x9b, 0x34, 0xfb},
};

} // namespace windows_bluetooth
} // namespace mao

#endif
