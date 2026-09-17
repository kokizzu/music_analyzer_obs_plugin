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

extern "C" {
HRESULT WINAPI BluetoothGATTGetServices(HANDLE, USHORT, MAO_BTH_LE_GATT_SERVICE *, USHORT *, ULONG);
HRESULT WINAPI BluetoothGATTGetCharacteristics(HANDLE, MAO_BTH_LE_GATT_SERVICE *, USHORT,
								MAO_BTH_LE_GATT_CHARACTERISTIC *, USHORT *, ULONG);
HRESULT WINAPI BluetoothGATTSetCharacteristicValue(HANDLE, MAO_BTH_LE_GATT_CHARACTERISTIC *,
								MAO_BTH_LE_GATT_CHARACTERISTIC_VALUE *, ULONG, ULONG);
}

namespace mao {
namespace windows_bluetooth {

constexpr ULONG kGattFlagNone = 0x00000000;
constexpr ULONG kGattFlagWriteWithoutResponse = 0x00000020;

const GUID kBluetoothLeDeviceInterface = {
	0x781aee18,
	0x7733,
	0x4ce4,
	{0xad, 0xd0, 0x91, 0xf4, 0x1c, 0x67, 0xb5, 0x92},
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
