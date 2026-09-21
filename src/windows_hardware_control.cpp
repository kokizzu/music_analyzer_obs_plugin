#include "windows_hardware_control.hpp"
#include "windows_hardware_retry.hpp"
#include "windows_hardware_write.hpp"

#if defined(_WIN32)

#include "windows_bluetooth_gatt.hpp"

#include <windows.h>
#include <mmsystem.h>
#include <setupapi.h>

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <cwctype>
#include <cstring>
#include <exception>
#include <mutex>
#include <string>
#include <thread>
#include <utility>
#include <vector>

namespace mao {
namespace {

constexpr DWORD kBluetoothDeviceEnumerationFlags = DIGCF_PRESENT | DIGCF_DEVICEINTERFACE;
constexpr DWORD kFretZealotFriendlyNameProperty = SPDRP_FRIENDLYNAME;
constexpr DWORD kFretZealotDeviceDescriptionProperty = SPDRP_DEVICEDESC;
constexpr DWORD kFretZealotHardwareIdProperty = SPDRP_HARDWAREID;
constexpr std::size_t kFretZealotChunkBytes = 20;
constexpr std::size_t kFretZealot2ChunkBytes = 500;
constexpr DWORD kFretZealotLegacyWriteDelayMs = 20;
constexpr DWORD kFretZealotModernWriteDelayMs = 1;
constexpr DWORD kGattWriteRetryDelayMs = 50;
constexpr int kGattWriteAttempts = 3;
constexpr auto kHardwareRetryInterval = std::chrono::seconds(2);

using HardwareClock = HardwareRetryState::clock;

void log_hardware_hresult(const char *device, const char *operation, HRESULT result)
{
	std::fprintf(stderr, "Windows hardware %s %s failed hr=0x%08lX\n", device, operation,
		     static_cast<unsigned long>(result));
}

void log_hardware_win32_error(const char *device, const char *operation, DWORD error)
{
	std::fprintf(stderr, "Windows hardware %s %s failed win32=%lu\n", device, operation,
		     static_cast<unsigned long>(error));
}

void log_hardware_midi_error(const char *device, const char *operation, MMRESULT result)
{
	std::fprintf(stderr, "Windows hardware %s %s failed midi=%u\n", device, operation,
		     static_cast<unsigned int>(result));
}

void publish_hardware_status(const char *device, std::atomic<bool> &status, bool connected,
				     const char *reason = nullptr)
{
	const bool previous = status.exchange(connected, std::memory_order_acq_rel);
	if (previous == connected)
		return;
	std::fprintf(stderr, "Windows hardware status: %s=%s", device,
		     connected ? "connected" : "disconnected");
	if (reason && *reason)
		std::fprintf(stderr, " reason=%s", reason);
	std::fputc('\n', stderr);
}

bool is_transient_gatt_error(HRESULT result)
{
	switch (HRESULT_CODE(result)) {
	case ERROR_BUSY:
	case ERROR_DEVICE_NOT_CONNECTED:
	case ERROR_INVALID_HANDLE:
	case ERROR_IO_PENDING:
	case ERROR_OPERATION_ABORTED:
	case ERROR_SEM_TIMEOUT:
	case ERROR_TIMEOUT:
		return true;
	default:
		return false;
	}
}

template <typename Writer>
HRESULT write_gatt_with_retry(const char *device, Writer writer)
{
	HRESULT result = E_FAIL;
	for (int attempt = 0; attempt < kGattWriteAttempts; ++attempt) {
		result = writer();
		if (SUCCEEDED(result) || !is_transient_gatt_error(result) || attempt + 1 == kGattWriteAttempts)
			return result;
		std::fprintf(stderr, "Windows hardware %s transient GATT write failure; retry=%d/%d hr=0x%08lX\n",
			     device, attempt + 1, kGattWriteAttempts - 1,
			     static_cast<unsigned long>(result));
		Sleep(kGattWriteRetryDelayMs);
	}
	return result;
}

std::wstring lowercase_wide(std::wstring value)
{
	for (wchar_t &character : value)
		character = static_cast<wchar_t>(std::towlower(character));
	return value;
}

std::string narrow_utf8(const std::wstring &value)
{
	if (value.empty())
		return {};
	const int required = WideCharToMultiByte(CP_UTF8, 0, value.data(), static_cast<int>(value.size()),
								 nullptr, 0, nullptr, nullptr);
	if (required <= 0)
		return {};
	std::string result(static_cast<std::size_t>(required), '\0');
	WideCharToMultiByte(CP_UTF8, 0, value.data(), static_cast<int>(value.size()), result.data(), required,
				    nullptr, nullptr);
	return result;
}

std::wstring property_string(HDEVINFO device_set, PSP_DEVINFO_DATA device, DWORD property)
{
	std::vector<BYTE> buffer(1024, 0);
	DWORD type = 0;
	DWORD required = 0;
	if (!SetupDiGetDeviceRegistryPropertyW(device_set, device, property, &type, buffer.data(),
								 static_cast<DWORD>(buffer.size()), &required)) {
		if (GetLastError() != ERROR_INSUFFICIENT_BUFFER || required == 0)
			return {};
		buffer.assign(required, 0);
		if (!SetupDiGetDeviceRegistryPropertyW(device_set, device, property, &type, buffer.data(),
								       static_cast<DWORD>(buffer.size()), &required))
			return {};
	}
	if (type != REG_SZ && type != REG_EXPAND_SZ && type != REG_MULTI_SZ)
		return {};
	return std::wstring(reinterpret_cast<const wchar_t *>(buffer.data()));
}

std::wstring device_metadata(HDEVINFO device_set, PSP_DEVINFO_DATA device)
{
	std::wstring result = property_string(device_set, device, kFretZealotFriendlyNameProperty);
	for (DWORD property : {kFretZealotDeviceDescriptionProperty, kFretZealotHardwareIdProperty}) {
		const std::wstring value = property_string(device_set, device, property);
		if (!value.empty()) {
			if (!result.empty())
				result.push_back(L'\n');
			result += value;
		}
	}
	return result;
}

template <typename Visitor>
void enumerate_bluetooth_le_interfaces(Visitor visitor)
{
	const HDEVINFO device_set = SetupDiGetClassDevsW(&windows_bluetooth::kBluetoothGattServiceInterface, nullptr,
									 nullptr, kBluetoothDeviceEnumerationFlags);
	if (device_set == INVALID_HANDLE_VALUE)
		return;

	for (DWORD index = 0;; ++index) {
		SP_DEVICE_INTERFACE_DATA interface_data = {};
		interface_data.cbSize = sizeof(interface_data);
		if (!SetupDiEnumDeviceInterfaces(device_set, nullptr, &windows_bluetooth::kBluetoothGattServiceInterface,
									 index, &interface_data)) {
			if (GetLastError() == ERROR_NO_MORE_ITEMS)
				break;
			continue;
		}

		SP_DEVINFO_DATA device_data = {};
		device_data.cbSize = sizeof(device_data);
		DWORD required = 0;
		(void)SetupDiGetDeviceInterfaceDetailW(device_set, &interface_data, nullptr, 0, &required, &device_data);
		if (required < sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA_W))
			continue;

		std::vector<BYTE> detail_storage(required, 0);
		PSP_DEVICE_INTERFACE_DETAIL_DATA_W detail =
			reinterpret_cast<PSP_DEVICE_INTERFACE_DETAIL_DATA_W>(detail_storage.data());
		detail->cbSize = sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA_W);
		if (!SetupDiGetDeviceInterfaceDetailW(device_set, &interface_data, detail, required, &required, &device_data))
			continue;

		if (!visitor(device_metadata(device_set, &device_data), detail->DevicePath))
			break;
	}

	SetupDiDestroyDeviceInfoList(device_set);
}

bool fret_zealot_name_matches(const std::wstring &metadata, const std::string &preferred)
{
	const std::wstring lower_metadata = lowercase_wide(metadata);
	if (!preferred.empty()) {
		std::wstring lower_preferred;
		lower_preferred.reserve(preferred.size());
		for (unsigned char character : preferred)
			lower_preferred.push_back(static_cast<wchar_t>(std::towlower(character)));
		return lower_metadata.find(lower_preferred) != std::wstring::npos;
	}
	return lower_metadata.find(L"fret zealot") != std::wstring::npos ||
		lower_metadata.find(L"fretzealot") != std::wstring::npos;
}

bool litejam_name_matches(const std::wstring &metadata, const std::string &preferred)
{
	const std::wstring lower_metadata = lowercase_wide(metadata);
	if (!preferred.empty()) {
		std::wstring lower_preferred;
		lower_preferred.reserve(preferred.size());
		for (unsigned char character : preferred)
			lower_preferred.push_back(static_cast<wchar_t>(std::towlower(character)));
		return lower_metadata.find(lower_preferred) != std::wstring::npos;
	}
	return lower_metadata.find(L"litejam") != std::wstring::npos ||
		lower_metadata.find(L"lite jam") != std::wstring::npos;
}

bool uuid_matches(const MAO_BTH_LE_UUID &uuid, const GUID &expected)
{
	return uuid.IsShortUuid == FALSE && std::memcmp(&uuid.Value.LongUuid, &expected, sizeof(GUID)) == 0;
}

bool short_uuid_matches(const MAO_BTH_LE_UUID &uuid, USHORT expected)
{
	return uuid.IsShortUuid != FALSE && uuid.Value.ShortUuid == expected;
}

class WindowsMidiOutput {
public:
	~WindowsMidiOutput()
	{
		close();
	}

	bool active() const
	{
		return handle_ != nullptr;
	}

	bool open(const std::string &preferred, const std::string &protocol)
	{
		if (active())
			return true;

		const UINT count = midiOutGetNumDevs();
		for (UINT index = 0; index < count; ++index) {
			MIDIOUTCAPSA caps = {};
			if (midiOutGetDevCapsA(index, &caps, sizeof(caps)) != MMSYSERR_NOERROR)
				continue;
			const std::string name = caps.szPname;
			if (!windows_midi_output_name_matches(name, preferred))
				continue;
			HMIDIOUT handle = nullptr;
			const MMRESULT open_result = midiOutOpen(&handle, index, 0, 0, CALLBACK_NULL);
			if (open_result != MMSYSERR_NOERROR) {
				log_hardware_midi_error("MIDI", "open", open_result);
				continue;
			}
			const MMRESULT reset_result = midiOutReset(handle);
			if (reset_result != MMSYSERR_NOERROR) {
				log_hardware_midi_error("MIDI", "reset after open", reset_result);
				midiOutClose(handle);
				continue;
			}
			handle_ = handle;
			name_ = name;
			manufacturer_id_ = caps.wMid;
			product_id_ = caps.wPid;
			pad_note_feedback_ = windows_midi_uses_pad_note_feedback(name_, protocol);
			std::fprintf(stderr, "Windows MIDI pad output: %s mid=%u pid=%u protocol=%s\n", name_.c_str(),
				     static_cast<unsigned int>(manufacturer_id_), static_cast<unsigned int>(product_id_),
				     pad_note_feedback_ ? "mpc-notes" : "apc-grid");
			return true;
		}
		return false;
	}

	bool still_present(const std::string &preferred)
	{
		if (!active())
			return false;
		const UINT count = midiOutGetNumDevs();
		for (UINT index = 0; index < count; ++index) {
			MIDIOUTCAPSA caps = {};
			if (midiOutGetDevCapsA(index, &caps, sizeof(caps)) != MMSYSERR_NOERROR)
				continue;
			const std::string name = caps.szPname;
			if (name == name_ && caps.wMid == manufacturer_id_ && caps.wPid == product_id_ &&
			    windows_midi_output_name_matches(name, preferred))
				return true;
		}
		close();
		return false;
	}

	template <typename ShouldContinue>
	bool send_scale(int root_pitch_class, RootControlMode mode, ShouldContinue should_continue)
	{
		if (!active())
			return false;
		const std::vector<std::uint8_t> messages = pad_note_feedback_
			? build_mpc_pad_note_messages(root_pitch_class)
			: build_apc_led_messages(root_pitch_class, mode);
		for (std::size_t offset = 0; offset + 2 < messages.size(); offset += 3) {
			const DWORD message = pack_windows_midi_short_message(messages[offset], messages[offset + 1],
											      messages[offset + 2]);
			MMRESULT result = MMSYSERR_NOERROR;
			const HardwareWriteResult write_result = hardware_write_if_current(should_continue, [&]() {
				result = midiOutShortMsg(handle_, message);
				if (result != MMSYSERR_NOERROR) {
					log_hardware_midi_error("MIDI", "send", result);
					return false;
				}
				return true;
			});
			if (write_result == HardwareWriteResult::Stale)
				return true;
			if (write_result == HardwareWriteResult::Failed)
				return false;
		}
		return true;
	}

	void close()
	{
		if (handle_) {
			midiOutReset(handle_);
			midiOutClose(handle_);
			handle_ = nullptr;
		}
		name_.clear();
		manufacturer_id_ = 0;
		product_id_ = 0;
		pad_note_feedback_ = false;
	}

private:
	HMIDIOUT handle_ = nullptr;
	std::string name_;
	WORD manufacturer_id_ = 0;
	WORD product_id_ = 0;
	bool pad_note_feedback_ = false;
};

class FretZealotGatt {
public:
	~FretZealotGatt()
	{
		close();
	}

	template <typename ShouldContinue>
	bool send_scale(int root_pitch_class, const std::string &preferred_device, ShouldContinue should_continue)
	{
		if (!active() && !open(preferred_device))
			return false;
		if (!should_continue())
			return true;
		const std::vector<std::uint8_t> packet = build_fret_zealot_major_scale_packet(root_pitch_class);
		for (std::size_t offset = 0; offset < packet.size(); offset += chunk_bytes_) {
			const std::size_t chunk_size = std::min(chunk_bytes_, packet.size() - offset);
			std::vector<BYTE> storage(sizeof(MAO_BTH_LE_GATT_CHARACTERISTIC_VALUE) + chunk_bytes_ - 1, 0);
			MAO_BTH_LE_GATT_CHARACTERISTIC_VALUE *value =
				reinterpret_cast<MAO_BTH_LE_GATT_CHARACTERISTIC_VALUE *>(storage.data());
			value->DataSize = static_cast<ULONG>(chunk_size);
			std::memcpy(value->Data, packet.data() + offset, chunk_size);
			HRESULT result = S_OK;
			const HardwareWriteResult write_result = hardware_write_if_current(should_continue, [&]() {
				result = write_gatt_with_retry("Fret Zealot", [&]() {
					return BluetoothGATTSetCharacteristicValue(handle_, &characteristic_, value, 0, write_flags_);
				});
				return true;
			});
			if (write_result == HardwareWriteResult::Stale)
				return true;
			if (FAILED(result)) {
				log_hardware_hresult("Fret Zealot", "write scale packet", result);
				close();
				return false;
			}
			if (offset + chunk_size < packet.size())
				Sleep(write_delay_ms_);
		}
		return true;
	}

	bool active() const
	{
		return handle_ != INVALID_HANDLE_VALUE && handle_ != nullptr;
	}

	void close()
	{
		if (active())
			CloseHandle(handle_);
		handle_ = INVALID_HANDLE_VALUE;
		services_.clear();
		characteristics_.clear();
		service_ = {};
		characteristic_ = {};
		write_flags_ = windows_bluetooth::kGattFlagNone;
		chunk_bytes_ = kFretZealotChunkBytes;
		write_delay_ms_ = kFretZealotLegacyWriteDelayMs;
	}

	bool still_present()
	{
		if (!active())
			return false;
		USHORT service_count = 0;
		const HRESULT result = BluetoothGATTGetServices(handle_, 0, nullptr, &service_count,
									 windows_bluetooth::kGattFlagNone);
		if (result == HRESULT_FROM_WIN32(ERROR_MORE_DATA) && service_count > 0)
			return true;
		log_hardware_hresult("Fret Zealot", "probe services", result);
		close();
		return false;
	}

private:
	bool open(const std::string &preferred_device)
	{
		close();
		bool connected = false;
		auto enumerate_matches = [&](bool exact_path_only) {
			enumerate_bluetooth_le_interfaces([&](const std::wstring &metadata, const std::wstring &path) {
				if (!fret_zealot_name_matches(metadata, preferred_device) ||
				    (exact_path_only && path != last_path_))
					return true;
				HANDLE candidate = CreateFileW(path.c_str(), GENERIC_READ | GENERIC_WRITE,
								       FILE_SHARE_READ | FILE_SHARE_WRITE, nullptr, OPEN_EXISTING, 0, nullptr);
				if (candidate == INVALID_HANDLE_VALUE) {
					log_hardware_win32_error("Fret Zealot", "open BLE interface", GetLastError());
					return true;
				}
				if (!discover(candidate)) {
					CloseHandle(candidate);
					return true;
				}
				handle_ = candidate;
				last_path_ = path;
				device_name_ = narrow_utf8(metadata);
				std::replace(device_name_.begin(), device_name_.end(), '\n', ' ');
				std::fprintf(stderr, "Fret Zealot Windows BLE output: %s\n", device_name_.c_str());
				connected = true;
				return false;
			});
		};
		if (!last_path_.empty())
			enumerate_matches(true);
		if (!connected)
			enumerate_matches(false);
		return connected;
	}

	bool discover(HANDLE candidate)
	{
		USHORT service_count = 0;
		HRESULT result = BluetoothGATTGetServices(candidate, 0, nullptr, &service_count,
								 windows_bluetooth::kGattFlagNone);
		if (result != HRESULT_FROM_WIN32(ERROR_MORE_DATA) || service_count == 0) {
			log_hardware_hresult("Fret Zealot", "discover service count", result);
			return false;
		}
		services_.assign(service_count, {});
		USHORT returned_services = service_count;
		result = BluetoothGATTGetServices(candidate, service_count, services_.data(), &returned_services,
							 windows_bluetooth::kGattFlagNone);
		if (FAILED(result)) {
			log_hardware_hresult("Fret Zealot", "discover services", result);
			return false;
		}

		bool found_service = false;
		const GUID *write_characteristic_uuid = nullptr;
		std::size_t chunk_bytes = kFretZealotChunkBytes;
		DWORD write_delay_ms = kFretZealotLegacyWriteDelayMs;
		for (USHORT index = 0; index < returned_services; ++index) {
			if (uuid_matches(services_[index].ServiceUuid, windows_bluetooth::kFretZealotService)) {
				service_ = services_[index];
				write_characteristic_uuid = &windows_bluetooth::kFretZealotWriteCharacteristic;
				found_service = true;
				break;
			}
			if (uuid_matches(services_[index].ServiceUuid, windows_bluetooth::kFretZealot2Service)) {
				service_ = services_[index];
				write_characteristic_uuid = &windows_bluetooth::kFretZealot2WriteCharacteristic;
				chunk_bytes = kFretZealot2ChunkBytes;
				write_delay_ms = kFretZealotModernWriteDelayMs;
				found_service = true;
				break;
			}
		}
		if (!found_service || !write_characteristic_uuid) {
			std::fprintf(stderr, "Windows hardware Fret Zealot service not found\n");
			return false;
		}

		USHORT characteristic_count = 0;
		result = BluetoothGATTGetCharacteristics(candidate, &service_, 0, nullptr, &characteristic_count,
								 windows_bluetooth::kGattFlagNone);
		if (result != HRESULT_FROM_WIN32(ERROR_MORE_DATA) || characteristic_count == 0) {
			log_hardware_hresult("Fret Zealot", "discover characteristic count", result);
			return false;
		}
		characteristics_.assign(characteristic_count, {});
		USHORT returned_characteristics = characteristic_count;
		result = BluetoothGATTGetCharacteristics(candidate, &service_, characteristic_count,
							 characteristics_.data(), &returned_characteristics,
							 windows_bluetooth::kGattFlagNone);
		if (FAILED(result)) {
			log_hardware_hresult("Fret Zealot", "discover characteristics", result);
			return false;
		}

		for (USHORT index = 0; index < returned_characteristics; ++index) {
			const MAO_BTH_LE_GATT_CHARACTERISTIC &candidate_characteristic = characteristics_[index];
			if (!uuid_matches(candidate_characteristic.CharacteristicUuid, *write_characteristic_uuid))
				continue;
			if (!candidate_characteristic.IsWritable && !candidate_characteristic.IsWritableWithoutResponse) {
				std::fprintf(stderr, "Windows hardware Fret Zealot write characteristic is not writable\n");
				return false;
			}
			characteristic_ = candidate_characteristic;
			write_flags_ = candidate_characteristic.IsWritable
				? windows_bluetooth::kGattFlagNone
				: windows_bluetooth::kGattFlagWriteWithoutResponse;
			chunk_bytes_ = chunk_bytes;
			write_delay_ms_ = write_delay_ms;
			return true;
		}
		std::fprintf(stderr, "Windows hardware Fret Zealot write characteristic not found\n");
		return false;
	}

	HANDLE handle_ = INVALID_HANDLE_VALUE;
	std::wstring last_path_;
	std::string device_name_;
	std::vector<MAO_BTH_LE_GATT_SERVICE> services_;
	std::vector<MAO_BTH_LE_GATT_CHARACTERISTIC> characteristics_;
	MAO_BTH_LE_GATT_SERVICE service_ = {};
	MAO_BTH_LE_GATT_CHARACTERISTIC characteristic_ = {};
	ULONG write_flags_ = windows_bluetooth::kGattFlagNone;
	std::size_t chunk_bytes_ = kFretZealotChunkBytes;
	DWORD write_delay_ms_ = kFretZealotLegacyWriteDelayMs;
};

class LiteJamGatt {
public:
	~LiteJamGatt()
	{
		close();
	}

	template <typename ShouldContinue>
	bool send_scale(int root_pitch_class, const std::string &preferred_device, ShouldContinue should_continue)
	{
		if (!active() && !open(preferred_device))
			return false;
		if (!should_continue())
			return true;
		const std::vector<std::uint8_t> packet = build_litejam_major_scale_packet(root_pitch_class);
		std::vector<BYTE> storage(sizeof(MAO_BTH_LE_GATT_CHARACTERISTIC_VALUE) + packet.size() - 1, 0);
		MAO_BTH_LE_GATT_CHARACTERISTIC_VALUE *value =
			reinterpret_cast<MAO_BTH_LE_GATT_CHARACTERISTIC_VALUE *>(storage.data());
		value->DataSize = static_cast<ULONG>(packet.size());
		std::memcpy(value->Data, packet.data(), packet.size());
		HRESULT result = S_OK;
		const HardwareWriteResult write_result = hardware_write_if_current(should_continue, [&]() {
			result = write_gatt_with_retry("LiteJam", [&]() {
				return BluetoothGATTSetCharacteristicValue(handle_, &characteristic_, value, 0, write_flags_);
			});
			return true;
		});
		if (write_result == HardwareWriteResult::Stale)
			return true;
		if (FAILED(result)) {
			log_hardware_hresult("LiteJam", "write scale packet", result);
			close();
			return false;
		}
		return true;
	}

	bool active() const
	{
		return handle_ != INVALID_HANDLE_VALUE && handle_ != nullptr;
	}

	void close()
	{
		if (active())
			CloseHandle(handle_);
		handle_ = INVALID_HANDLE_VALUE;
		services_.clear();
		characteristics_.clear();
		service_ = {};
		characteristic_ = {};
		write_flags_ = windows_bluetooth::kGattFlagNone;
	}

	bool still_present()
	{
		if (!active())
			return false;
		USHORT service_count = 0;
		const HRESULT result = BluetoothGATTGetServices(handle_, 0, nullptr, &service_count,
									 windows_bluetooth::kGattFlagNone);
		if (result == HRESULT_FROM_WIN32(ERROR_MORE_DATA) && service_count > 0)
			return true;
		log_hardware_hresult("LiteJam", "probe services", result);
		close();
		return false;
	}

private:
	bool open(const std::string &preferred_device)
	{
		close();
		bool connected = false;
		auto enumerate_matches = [&](bool exact_path_only) {
			enumerate_bluetooth_le_interfaces([&](const std::wstring &metadata, const std::wstring &path) {
				if (!litejam_name_matches(metadata, preferred_device) ||
				    (exact_path_only && path != last_path_))
					return true;
				HANDLE candidate = CreateFileW(path.c_str(), GENERIC_READ | GENERIC_WRITE,
								       FILE_SHARE_READ | FILE_SHARE_WRITE, nullptr, OPEN_EXISTING, 0, nullptr);
				if (candidate == INVALID_HANDLE_VALUE) {
					log_hardware_win32_error("LiteJam", "open BLE interface", GetLastError());
					return true;
				}
				if (!discover(candidate)) {
					CloseHandle(candidate);
					return true;
				}
				handle_ = candidate;
				last_path_ = path;
				device_name_ = narrow_utf8(metadata);
				std::replace(device_name_.begin(), device_name_.end(), '\n', ' ');
				std::fprintf(stderr, "LiteJam Windows BLE output: %s\n", device_name_.c_str());
				connected = true;
				return false;
			});
		};
		if (!last_path_.empty())
			enumerate_matches(true);
		if (!connected)
			enumerate_matches(false);
		return connected;
	}

	bool discover(HANDLE candidate)
	{
		USHORT service_count = 0;
		HRESULT result = BluetoothGATTGetServices(candidate, 0, nullptr, &service_count,
								 windows_bluetooth::kGattFlagNone);
		if (result != HRESULT_FROM_WIN32(ERROR_MORE_DATA) || service_count == 0) {
			log_hardware_hresult("LiteJam", "discover service count", result);
			return false;
		}
		services_.assign(service_count, {});
		USHORT returned_services = service_count;
		result = BluetoothGATTGetServices(candidate, service_count, services_.data(), &returned_services,
							windows_bluetooth::kGattFlagNone);
		if (FAILED(result)) {
			log_hardware_hresult("LiteJam", "discover services", result);
			return false;
		}

		bool found_service = false;
		for (USHORT index = 0; index < returned_services; ++index) {
			const MAO_BTH_LE_UUID &uuid = services_[index].ServiceUuid;
			if (short_uuid_matches(uuid, windows_bluetooth::kLiteJamServiceShortUuid) ||
			    uuid_matches(uuid, windows_bluetooth::kLiteJamService)) {
				service_ = services_[index];
				found_service = true;
				break;
			}
		}
		if (!found_service) {
			std::fprintf(stderr, "Windows hardware LiteJam service not found\n");
			return false;
		}

		USHORT characteristic_count = 0;
		result = BluetoothGATTGetCharacteristics(candidate, &service_, 0, nullptr, &characteristic_count,
								 windows_bluetooth::kGattFlagNone);
		if (result != HRESULT_FROM_WIN32(ERROR_MORE_DATA) || characteristic_count == 0) {
			log_hardware_hresult("LiteJam", "discover characteristic count", result);
			return false;
		}
		characteristics_.assign(characteristic_count, {});
		USHORT returned_characteristics = characteristic_count;
		result = BluetoothGATTGetCharacteristics(candidate, &service_, characteristic_count,
								 characteristics_.data(), &returned_characteristics,
								 windows_bluetooth::kGattFlagNone);
		if (FAILED(result)) {
			log_hardware_hresult("LiteJam", "discover characteristics", result);
			return false;
		}

		for (USHORT index = 0; index < returned_characteristics; ++index) {
			const MAO_BTH_LE_GATT_CHARACTERISTIC &candidate_characteristic = characteristics_[index];
			if (!short_uuid_matches(candidate_characteristic.CharacteristicUuid,
					    windows_bluetooth::kLiteJamLedCharacteristicShortUuid) &&
			    !uuid_matches(candidate_characteristic.CharacteristicUuid,
					       windows_bluetooth::kLiteJamLedCharacteristic))
				continue;
			if (!candidate_characteristic.IsWritable && !candidate_characteristic.IsWritableWithoutResponse) {
				std::fprintf(stderr, "Windows hardware LiteJam write characteristic is not writable\n");
				return false;
			}
			characteristic_ = candidate_characteristic;
			write_flags_ = candidate_characteristic.IsWritable
				? windows_bluetooth::kGattFlagNone
				: windows_bluetooth::kGattFlagWriteWithoutResponse;
			return true;
		}
		std::fprintf(stderr, "Windows hardware LiteJam write characteristic not found\n");
		return false;
	}

	HANDLE handle_ = INVALID_HANDLE_VALUE;
	std::wstring last_path_;
	std::string device_name_;
	std::vector<MAO_BTH_LE_GATT_SERVICE> services_;
	std::vector<MAO_BTH_LE_GATT_CHARACTERISTIC> characteristics_;
	MAO_BTH_LE_GATT_SERVICE service_ = {};
	MAO_BTH_LE_GATT_CHARACTERISTIC characteristic_ = {};
	ULONG write_flags_ = windows_bluetooth::kGattFlagNone;
};

} // namespace

struct WindowsHardwareController::Impl {
	explicit Impl(const WindowsHardwareOptions &options_value) : options(options_value)
	{
	}

	void start()
	{
		if (!options.enabled)
			return;
		{
			std::lock_guard<std::mutex> lock(mutex);
			if (started)
				return;
			stop_requested = false;
			started = true;
		}
		midi_worker = std::thread(&Impl::run_midi_guarded, this);
		litejam_worker = std::thread(&Impl::run_litejam_guarded, this);
		fret_zealot_worker = std::thread(&Impl::run_fret_zealot_guarded, this);
	}

	void update(int root_pitch_class, RootControlMode mode)
	{
		if (!options.enabled || root_pitch_class < 0 || root_pitch_class >= 12)
			return;
		std::lock_guard<std::mutex> lock(mutex);
		if (desired_root == root_pitch_class && desired_mode == mode)
			return;
		desired_root = root_pitch_class;
		desired_mode = mode;
		++desired_revision;
		condition.notify_all();
	}

	void stop()
	{
		{
			std::lock_guard<std::mutex> lock(mutex);
			if (!started)
				return;
			stop_requested = true;
			condition.notify_all();
		}
		if (midi_worker.joinable())
			midi_worker.join();
		if (litejam_worker.joinable())
			litejam_worker.join();
		if (fret_zealot_worker.joinable())
			fret_zealot_worker.join();
		{
			std::lock_guard<std::mutex> lock(mutex);
			started = false;
		}
	}

	bool wait_for_state(std::uint64_t &attempted_revision, int &root, RootControlMode &mode,
				   std::uint64_t &revision)
	{
		std::unique_lock<std::mutex> lock(mutex);
		condition.wait_for(lock, kHardwareRetryInterval, [&]() {
			return stop_requested || desired_revision != attempted_revision;
		});
		if (stop_requested)
			return false;
		root = desired_root;
		mode = desired_mode;
		revision = desired_revision;
		attempted_revision = revision;
		return true;
	}

	bool revision_is_current(std::uint64_t revision)
	{
		std::lock_guard<std::mutex> lock(mutex);
		return !stop_requested && desired_revision == revision;
	}

	void run_midi_guarded()
	{
		try {
			run_midi();
		} catch (const std::exception &error) {
			std::fprintf(stderr, "Windows hardware MIDI worker exception: %s\n", error.what());
			midi.close();
			publish_hardware_status("midi", midi_connected, false, "worker-exception");
		} catch (...) {
			std::fprintf(stderr, "Windows hardware MIDI worker exception: unknown\n");
			midi.close();
			publish_hardware_status("midi", midi_connected, false);
		}
	}

	void run_litejam_guarded()
	{
		try {
			run_litejam();
		} catch (const std::exception &error) {
			std::fprintf(stderr, "Windows hardware LiteJam worker exception: %s\n", error.what());
			litejam.close();
			publish_hardware_status("litejam", litejam_connected, false, "worker-exception");
		} catch (...) {
			std::fprintf(stderr, "Windows hardware LiteJam worker exception: unknown\n");
			litejam.close();
			publish_hardware_status("litejam", litejam_connected, false);
		}
	}

	void run_fret_zealot_guarded()
	{
		try {
			run_fret_zealot();
		} catch (const std::exception &error) {
			std::fprintf(stderr, "Windows hardware Fret Zealot worker exception: %s\n", error.what());
			fret_zealot.close();
			publish_hardware_status("fret-zealot", fret_zealot_connected, false, "worker-exception");
		} catch (...) {
			std::fprintf(stderr, "Windows hardware Fret Zealot worker exception: unknown\n");
			fret_zealot.close();
			publish_hardware_status("fret-zealot", fret_zealot_connected, false);
		}
	}

	void run_midi()
	{
		std::uint64_t attempted_revision = 0;
		std::uint64_t sent_revision = 0;
		std::uint64_t last_revision = 0;
		HardwareRetryState retry;
		for (;;) {
			int root = -1;
			RootControlMode mode = RootControlMode::Auto;
			std::uint64_t revision = 0;
			if (!wait_for_state(attempted_revision, root, mode, revision))
				break;
			if (root < 0)
				continue;

			const auto now = HardwareClock::now();
			if (revision != last_revision) {
				last_revision = revision;
				retry.force(now);
			}
			if (!retry.ready(now))
				continue;

			const bool present = midi.still_present(options.midi_output);
			if (!present)
				publish_hardware_status("midi", midi_connected, false, "device-missing");
			if (sent_revision != revision || !present) {
				if (!revision_is_current(revision))
					continue;
				if (!midi.active())
					(void)midi.open(options.midi_output, options.midi_protocol);
				const auto current_revision = [&]() { return revision_is_current(revision); };
				const bool write_succeeded = midi.active() && midi.send_scale(root, mode, current_revision);
				if (write_succeeded) {
					sent_revision = revision_is_current(revision) ? revision : 0;
					publish_hardware_status("midi", midi_connected, true, "output-sent");
					retry.succeeded(HardwareClock::now());
				} else {
					midi.close();
					sent_revision = 0;
					publish_hardware_status("midi", midi_connected, false, "output-failed");
					retry.failed(HardwareClock::now());
				}
			} else {
				retry.succeeded(HardwareClock::now());
			}
		}
		midi.close();
		publish_hardware_status("midi", midi_connected, false, "worker-stopped");
	}

	void run_litejam()
	{
		std::uint64_t attempted_revision = 0;
		std::uint64_t sent_revision = 0;
		std::uint64_t last_revision = 0;
		HardwareRetryState retry;
		for (;;) {
			int root = -1;
			RootControlMode mode = RootControlMode::Auto;
			std::uint64_t revision = 0;
			if (!wait_for_state(attempted_revision, root, mode, revision))
				break;
			if (root < 0)
				continue;

			const auto now = HardwareClock::now();
			if (revision != last_revision) {
				last_revision = revision;
				retry.force(now);
			}
			if (!retry.ready(now))
				continue;

			const bool present = litejam.still_present();
			if (!present)
				publish_hardware_status("litejam", litejam_connected, false, "device-missing");
			if (sent_revision != revision || !present) {
				if (!revision_is_current(revision))
					continue;
				const auto current_revision = [&]() { return revision_is_current(revision); };
				const bool write_succeeded = litejam.send_scale(root, options.litejam_device, current_revision);
				if (write_succeeded) {
					sent_revision = revision_is_current(revision) ? revision : 0;
					publish_hardware_status("litejam", litejam_connected, true, "output-sent");
					retry.succeeded(HardwareClock::now());
				} else {
					sent_revision = 0;
					publish_hardware_status("litejam", litejam_connected, false, "output-failed");
					retry.failed(HardwareClock::now());
				}
			} else {
				retry.succeeded(HardwareClock::now());
			}
		}
		litejam.close();
		publish_hardware_status("litejam", litejam_connected, false, "worker-stopped");
	}

	void run_fret_zealot()
	{
		std::uint64_t attempted_revision = 0;
		std::uint64_t sent_revision = 0;
		std::uint64_t last_revision = 0;
		HardwareRetryState retry;
		for (;;) {
			int root = -1;
			RootControlMode mode = RootControlMode::Auto;
			std::uint64_t revision = 0;
			if (!wait_for_state(attempted_revision, root, mode, revision))
				break;
			if (root < 0)
				continue;

			const auto now = HardwareClock::now();
			if (revision != last_revision) {
				last_revision = revision;
				retry.force(now);
			}
			if (!retry.ready(now))
				continue;

			const bool present = fret_zealot.still_present();
			if (!present)
				publish_hardware_status("fret-zealot", fret_zealot_connected, false, "device-missing");
			if (sent_revision != revision || !present) {
				if (!revision_is_current(revision))
					continue;
				const auto current_revision = [&]() { return revision_is_current(revision); };
				const bool write_succeeded = fret_zealot.send_scale(root, options.fret_zealot_device, current_revision);
				if (write_succeeded) {
					sent_revision = revision_is_current(revision) ? revision : 0;
					publish_hardware_status("fret-zealot", fret_zealot_connected, true, "output-sent");
					retry.succeeded(HardwareClock::now());
				} else {
					sent_revision = 0;
					publish_hardware_status("fret-zealot", fret_zealot_connected, false, "output-failed");
					retry.failed(HardwareClock::now());
				}
			} else {
				retry.succeeded(HardwareClock::now());
			}
		}
		fret_zealot.close();
		publish_hardware_status("fret-zealot", fret_zealot_connected, false, "worker-stopped");
	}

	WindowsHardwareOptions options;
	WindowsMidiOutput midi;
	LiteJamGatt litejam;
	FretZealotGatt fret_zealot;
	std::mutex mutex;
	std::condition_variable condition;
	std::thread midi_worker;
	std::thread litejam_worker;
	std::thread fret_zealot_worker;
	bool started = false;
	bool stop_requested = false;
	int desired_root = -1;
	RootControlMode desired_mode = RootControlMode::Auto;
	std::uint64_t desired_revision = 0;
	std::atomic<bool> midi_connected{false};
	std::atomic<bool> litejam_connected{false};
	std::atomic<bool> fret_zealot_connected{false};
};

WindowsHardwareController::WindowsHardwareController(const WindowsHardwareOptions &options)
	: impl_(std::make_unique<Impl>(options))
{
}

WindowsHardwareController::~WindowsHardwareController()
{
	stop();
}

void WindowsHardwareController::start()
{
	if (impl_)
		impl_->start();
}

void WindowsHardwareController::update(int root_pitch_class, RootControlMode mode)
{
	if (impl_)
		impl_->update(root_pitch_class, mode);
}

void WindowsHardwareController::stop()
{
	if (impl_)
		impl_->stop();
}

WindowsHardwareStatus WindowsHardwareController::status() const
{
	if (!impl_)
		return {};
	return WindowsHardwareStatus{
		impl_->midi_connected.load(std::memory_order_acquire),
		impl_->litejam_connected.load(std::memory_order_acquire),
		impl_->fret_zealot_connected.load(std::memory_order_acquire),
	};
}

void WindowsHardwareController::print_midi_devices()
{
	const UINT count = midiOutGetNumDevs();
	if (count == 0) {
		std::fprintf(stderr, "No Windows MIDI output devices\n");
		return;
	}
	for (UINT index = 0; index < count; ++index) {
		MIDIOUTCAPSA caps = {};
		if (midiOutGetDevCapsA(index, &caps, sizeof(caps)) == MMSYSERR_NOERROR)
			std::fprintf(stderr, "MIDI %u\t%s\n", index, caps.szPname);
	}
}

void WindowsHardwareController::print_litejam_devices()
{
	bool found = false;
	enumerate_bluetooth_le_interfaces([&](const std::wstring &metadata, const std::wstring &) {
		if (!litejam_name_matches(metadata, {}))
			return true;
		std::string name = narrow_utf8(metadata);
		std::replace(name.begin(), name.end(), '\n', ' ');
		std::fprintf(stderr, "LiteJam\t%s\n", name.c_str());
		found = true;
		return true;
	});
	if (!found)
		std::fprintf(stderr, "No paired LiteJam BLE interfaces\n");
}

void WindowsHardwareController::print_fret_zealot_devices()
{
	bool found = false;
	enumerate_bluetooth_le_interfaces([&](const std::wstring &metadata, const std::wstring &) {
		if (!fret_zealot_name_matches(metadata, {}))
			return true;
		std::string name = narrow_utf8(metadata);
		std::replace(name.begin(), name.end(), '\n', ' ');
		std::fprintf(stderr, "Fret Zealot\t%s\n", name.c_str());
		found = true;
		return true;
	});
	if (!found)
		std::fprintf(stderr, "No paired Fret Zealot BLE interfaces\n");
}

} // namespace mao

#endif
