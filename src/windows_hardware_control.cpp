#include "windows_hardware_control.hpp"

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
constexpr DWORD kFretZealotWriteDelayMs = 20;
constexpr auto kHardwareRetryInterval = std::chrono::seconds(2);

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
			if (midiOutOpen(&handle, index, 0, 0, CALLBACK_NULL) != MMSYSERR_NOERROR)
				continue;
			handle_ = handle;
			name_ = name;
			pad_note_feedback_ = windows_midi_uses_pad_note_feedback(name_, protocol);
			std::fprintf(stderr, "Windows MIDI pad output: %s protocol=%s\n", name_.c_str(),
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
			if (name == name_ && windows_midi_output_name_matches(name, preferred))
				return true;
		}
		close();
		return false;
	}

	bool send_scale(int root_pitch_class, RootControlMode mode)
	{
		if (!active())
			return false;
		const std::vector<std::uint8_t> messages = pad_note_feedback_
			? build_mpc_pad_note_messages(root_pitch_class)
			: build_apc_led_messages(root_pitch_class, mode);
		for (std::size_t offset = 0; offset + 2 < messages.size(); offset += 3) {
			const DWORD message = pack_windows_midi_short_message(messages[offset], messages[offset + 1],
									      messages[offset + 2]);
			if (midiOutShortMsg(handle_, message) != MMSYSERR_NOERROR)
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
		pad_note_feedback_ = false;
	}

private:
	HMIDIOUT handle_ = nullptr;
	std::string name_;
	bool pad_note_feedback_ = false;
};

class FretZealotGatt {
public:
	~FretZealotGatt()
	{
		close();
	}

	bool send_scale(int root_pitch_class, const std::string &preferred_device)
	{
		if (!active() && !open(preferred_device))
			return false;
		const std::vector<std::uint8_t> packet = build_fret_zealot_major_scale_packet(root_pitch_class);
		for (std::size_t offset = 0; offset < packet.size(); offset += chunk_bytes_) {
			const std::size_t chunk_size = std::min(chunk_bytes_, packet.size() - offset);
			std::vector<BYTE> storage(sizeof(MAO_BTH_LE_GATT_CHARACTERISTIC_VALUE) + chunk_bytes_ - 1, 0);
			MAO_BTH_LE_GATT_CHARACTERISTIC_VALUE *value =
				reinterpret_cast<MAO_BTH_LE_GATT_CHARACTERISTIC_VALUE *>(storage.data());
			value->DataSize = static_cast<ULONG>(chunk_size);
			std::memcpy(value->Data, packet.data() + offset, chunk_size);
			const HRESULT result = BluetoothGATTSetCharacteristicValue(
				handle_, &characteristic_, value, 0, write_flags_);
			if (FAILED(result)) {
				close();
				return false;
			}
			if (offset + chunk_size < packet.size())
				Sleep(kFretZealotWriteDelayMs);
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
		close();
		return false;
	}

private:
	bool open(const std::string &preferred_device)
	{
		close();
		bool connected = false;
		enumerate_bluetooth_le_interfaces([&](const std::wstring &metadata, const std::wstring &path) {
			if (!fret_zealot_name_matches(metadata, preferred_device))
				return true;
			HANDLE candidate = CreateFileW(path.c_str(), GENERIC_READ | GENERIC_WRITE,
							       FILE_SHARE_READ | FILE_SHARE_WRITE, nullptr, OPEN_EXISTING, 0, nullptr);
			if (candidate == INVALID_HANDLE_VALUE)
				return true;
			if (!discover(candidate)) {
				CloseHandle(candidate);
				return true;
			}
				handle_ = candidate;
			device_name_ = narrow_utf8(metadata);
			std::replace(device_name_.begin(), device_name_.end(), '\n', ' ');
			std::fprintf(stderr, "Fret Zealot Windows BLE output: %s\n", device_name_.c_str());
			connected = true;
			return false;
		});
		return connected;
	}

	bool discover(HANDLE candidate)
	{
		USHORT service_count = 0;
		HRESULT result = BluetoothGATTGetServices(candidate, 0, nullptr, &service_count,
								 windows_bluetooth::kGattFlagNone);
		if (result != HRESULT_FROM_WIN32(ERROR_MORE_DATA) || service_count == 0)
			return false;
		services_.assign(service_count, {});
		USHORT returned_services = service_count;
		result = BluetoothGATTGetServices(candidate, service_count, services_.data(), &returned_services,
							 windows_bluetooth::kGattFlagNone);
		if (FAILED(result))
			return false;

		bool found_service = false;
		const GUID *write_characteristic_uuid = nullptr;
		std::size_t chunk_bytes = kFretZealotChunkBytes;
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
				found_service = true;
				break;
			}
		}
		if (!found_service || !write_characteristic_uuid)
			return false;

		USHORT characteristic_count = 0;
		result = BluetoothGATTGetCharacteristics(candidate, &service_, 0, nullptr, &characteristic_count,
								 windows_bluetooth::kGattFlagNone);
		if (result != HRESULT_FROM_WIN32(ERROR_MORE_DATA) || characteristic_count == 0)
			return false;
		characteristics_.assign(characteristic_count, {});
		USHORT returned_characteristics = characteristic_count;
		result = BluetoothGATTGetCharacteristics(candidate, &service_, characteristic_count,
							 characteristics_.data(), &returned_characteristics,
							 windows_bluetooth::kGattFlagNone);
		if (FAILED(result))
			return false;

		for (USHORT index = 0; index < returned_characteristics; ++index) {
			const MAO_BTH_LE_GATT_CHARACTERISTIC &candidate_characteristic = characteristics_[index];
			if (!uuid_matches(candidate_characteristic.CharacteristicUuid, *write_characteristic_uuid))
				continue;
			if (!candidate_characteristic.IsWritable && !candidate_characteristic.IsWritableWithoutResponse)
				return false;
			characteristic_ = candidate_characteristic;
			write_flags_ = candidate_characteristic.IsWritable
				? windows_bluetooth::kGattFlagNone
				: windows_bluetooth::kGattFlagWriteWithoutResponse;
			chunk_bytes_ = chunk_bytes;
			return true;
		}
		return false;
	}

	HANDLE handle_ = INVALID_HANDLE_VALUE;
	std::string device_name_;
	std::vector<MAO_BTH_LE_GATT_SERVICE> services_;
	std::vector<MAO_BTH_LE_GATT_CHARACTERISTIC> characteristics_;
	MAO_BTH_LE_GATT_SERVICE service_ = {};
	MAO_BTH_LE_GATT_CHARACTERISTIC characteristic_ = {};
	ULONG write_flags_ = windows_bluetooth::kGattFlagNone;
	std::size_t chunk_bytes_ = kFretZealotChunkBytes;
};

class LiteJamGatt {
public:
	~LiteJamGatt()
	{
		close();
	}

	bool send_scale(int root_pitch_class, const std::string &preferred_device)
	{
		if (!active() && !open(preferred_device))
			return false;
		const std::vector<std::uint8_t> packet = build_litejam_major_scale_packet(root_pitch_class);
		std::vector<BYTE> storage(sizeof(MAO_BTH_LE_GATT_CHARACTERISTIC_VALUE) + packet.size() - 1, 0);
		MAO_BTH_LE_GATT_CHARACTERISTIC_VALUE *value =
			reinterpret_cast<MAO_BTH_LE_GATT_CHARACTERISTIC_VALUE *>(storage.data());
		value->DataSize = static_cast<ULONG>(packet.size());
		std::memcpy(value->Data, packet.data(), packet.size());
		const HRESULT result = BluetoothGATTSetCharacteristicValue(handle_, &characteristic_, value, 0, write_flags_);
		if (FAILED(result)) {
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
		close();
		return false;
	}

private:
	bool open(const std::string &preferred_device)
	{
		close();
		bool connected = false;
		enumerate_bluetooth_le_interfaces([&](const std::wstring &metadata, const std::wstring &path) {
			if (!litejam_name_matches(metadata, preferred_device))
				return true;
			HANDLE candidate = CreateFileW(path.c_str(), GENERIC_READ | GENERIC_WRITE,
						       FILE_SHARE_READ | FILE_SHARE_WRITE, nullptr, OPEN_EXISTING, 0, nullptr);
			if (candidate == INVALID_HANDLE_VALUE)
				return true;
			if (!discover(candidate)) {
				CloseHandle(candidate);
				return true;
			}
			handle_ = candidate;
			device_name_ = narrow_utf8(metadata);
			std::replace(device_name_.begin(), device_name_.end(), '\n', ' ');
			std::fprintf(stderr, "LiteJam Windows BLE output: %s\n", device_name_.c_str());
			connected = true;
			return false;
		});
		return connected;
	}

	bool discover(HANDLE candidate)
	{
		USHORT service_count = 0;
		HRESULT result = BluetoothGATTGetServices(candidate, 0, nullptr, &service_count,
								 windows_bluetooth::kGattFlagNone);
		if (result != HRESULT_FROM_WIN32(ERROR_MORE_DATA) || service_count == 0)
			return false;
		services_.assign(service_count, {});
		USHORT returned_services = service_count;
		result = BluetoothGATTGetServices(candidate, service_count, services_.data(), &returned_services,
							windows_bluetooth::kGattFlagNone);
		if (FAILED(result))
			return false;

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
		if (!found_service)
			return false;

		USHORT characteristic_count = 0;
		result = BluetoothGATTGetCharacteristics(candidate, &service_, 0, nullptr, &characteristic_count,
								 windows_bluetooth::kGattFlagNone);
		if (result != HRESULT_FROM_WIN32(ERROR_MORE_DATA) || characteristic_count == 0)
			return false;
		characteristics_.assign(characteristic_count, {});
		USHORT returned_characteristics = characteristic_count;
		result = BluetoothGATTGetCharacteristics(candidate, &service_, characteristic_count,
								 characteristics_.data(), &returned_characteristics,
								 windows_bluetooth::kGattFlagNone);
		if (FAILED(result))
			return false;

		for (USHORT index = 0; index < returned_characteristics; ++index) {
			const MAO_BTH_LE_GATT_CHARACTERISTIC &candidate_characteristic = characteristics_[index];
			if (!short_uuid_matches(candidate_characteristic.CharacteristicUuid,
					    windows_bluetooth::kLiteJamLedCharacteristicShortUuid) &&
			    !uuid_matches(candidate_characteristic.CharacteristicUuid,
					       windows_bluetooth::kLiteJamLedCharacteristic))
				continue;
			if (!candidate_characteristic.IsWritable && !candidate_characteristic.IsWritableWithoutResponse)
				return false;
			characteristic_ = candidate_characteristic;
			write_flags_ = candidate_characteristic.IsWritable
				? windows_bluetooth::kGattFlagNone
				: windows_bluetooth::kGattFlagWriteWithoutResponse;
			return true;
		}
		return false;
	}

	HANDLE handle_ = INVALID_HANDLE_VALUE;
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
		worker = std::thread(&Impl::run, this);
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
		condition.notify_one();
	}

	void stop()
	{
		{
			std::lock_guard<std::mutex> lock(mutex);
			if (!started)
				return;
			stop_requested = true;
			condition.notify_one();
		}
		if (worker.joinable())
			worker.join();
		{
			std::lock_guard<std::mutex> lock(mutex);
			started = false;
		}
	}

	void run()
	{
		std::uint64_t attempted_revision = 0;
		std::uint64_t midi_sent_revision = 0;
		std::uint64_t litejam_sent_revision = 0;
		std::uint64_t fret_zealot_sent_revision = 0;
		for (;;) {
			int root = -1;
			RootControlMode mode = RootControlMode::Auto;
			std::uint64_t revision = 0;
			{
				std::unique_lock<std::mutex> lock(mutex);
				condition.wait_for(lock, kHardwareRetryInterval, [&]() {
					return stop_requested || desired_revision != attempted_revision;
				});
				if (stop_requested)
					break;
				root = desired_root;
				mode = desired_mode;
				revision = desired_revision;
				attempted_revision = revision;
			}

			if (root < 0)
				continue;

			const bool midi_present = midi.still_present(options.midi_output);
			if (!midi_present)
				midi_connected.store(false, std::memory_order_release);
			if (midi_sent_revision != revision || !midi_present) {
				if (!midi.active())
					(void)midi.open(options.midi_output, options.midi_protocol);
				if (midi.active() && midi.send_scale(root, mode)) {
					midi_sent_revision = revision;
					midi_connected.store(true, std::memory_order_release);
				} else {
					midi.close();
					midi_sent_revision = 0;
					midi_connected.store(false, std::memory_order_release);
				}
			}

			const bool litejam_present = litejam.still_present();
			if (!litejam_present)
				litejam_connected.store(false, std::memory_order_release);
			if (litejam_sent_revision != revision || !litejam_present) {
				if (litejam.send_scale(root, options.litejam_device)) {
					litejam_sent_revision = revision;
					litejam_connected.store(true, std::memory_order_release);
				} else {
					litejam_sent_revision = 0;
					litejam_connected.store(false, std::memory_order_release);
				}
			}

			const bool fret_zealot_present = fret_zealot.still_present();
			if (!fret_zealot_present)
				fret_zealot_connected.store(false, std::memory_order_release);
			if (fret_zealot_sent_revision != revision || !fret_zealot_present) {
				if (fret_zealot.send_scale(root, options.fret_zealot_device)) {
					fret_zealot_sent_revision = revision;
					fret_zealot_connected.store(true, std::memory_order_release);
				} else {
					fret_zealot_sent_revision = 0;
					fret_zealot_connected.store(false, std::memory_order_release);
				}
			}
		}
		midi.close();
		litejam.close();
		fret_zealot.close();
		midi_connected.store(false, std::memory_order_release);
		litejam_connected.store(false, std::memory_order_release);
		fret_zealot_connected.store(false, std::memory_order_release);
	}

	WindowsHardwareOptions options;
	WindowsMidiOutput midi;
	LiteJamGatt litejam;
	FretZealotGatt fret_zealot;
	std::mutex mutex;
	std::condition_variable condition;
	std::thread worker;
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
