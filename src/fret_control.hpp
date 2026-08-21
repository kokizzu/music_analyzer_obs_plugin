#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace mao {

constexpr int kPitchClassCount = 12;
constexpr int kScaleDegreeCount = 7;

enum class RootControlMode : uint8_t {
	Auto,
	Manual,
};

enum class ExternalDevice : uint8_t {
	LiteJam,
	FretZealot,
	ApcMini,
	Mvave,
	AuphySct86Pro,
	Count,
};

enum class DeviceConnectionState : uint8_t {
	Disabled,
	Searching,
	Connecting,
	Connected,
	Error,
};

struct RgbColor {
	uint8_t red = 0;
	uint8_t green = 0;
	uint8_t blue = 0;
};

struct ExternalControlDisplay {
	bool visible = false;
	RootControlMode mode = RootControlMode::Auto;
	int effective_root = 0;
	bool autoconnect = true;
	std::array<DeviceConnectionState, static_cast<std::size_t>(ExternalDevice::Count)> devices = {};
};

enum class ControlActionKind : uint8_t {
	None,
	SetManualRoot,
	ShiftManualRoot,
	ToggleManualRootCG,
	ToggleMode,
	ToggleAutoconnect,
};

struct ControlAction {
	ControlActionKind kind = ControlActionKind::None;
	int value = 0;
};

int pitch_class_from_root_label(const char *label);
const char *pitch_class_name(int pitch_class);
const std::array<int, kScaleDegreeCount> &major_scale_intervals();
const std::array<RgbColor, kScaleDegreeCount> &major_scale_colors();
int major_scale_degree(int root_pitch_class, int note_pitch_class);

class FretControlState {
public:
	RootControlMode mode() const;
	int manual_root() const;
	int detected_root() const;
	int effective_root() const;
	bool autoconnect() const;
	uint64_t revision() const;
	DeviceConnectionState device_state(ExternalDevice device) const;
	ExternalControlDisplay display() const;

	bool set_detected_root(int pitch_class);
	bool set_detected_root_label(const char *label);
	bool set_manual_root(int pitch_class);
	bool shift_manual_root(int semitones);
	bool set_mode(RootControlMode mode);
	bool toggle_mode();
	bool set_autoconnect(bool enabled);
	bool toggle_autoconnect();
	bool set_device_state(ExternalDevice device, DeviceConnectionState state);
	bool apply(const ControlAction &action);

private:
	void mark_changed();

	RootControlMode mode_ = RootControlMode::Auto;
	int manual_root_ = 0;
	int detected_root_ = -1;
	bool autoconnect_ = true;
	uint64_t revision_ = 1;
	std::array<DeviceConnectionState, static_cast<std::size_t>(ExternalDevice::Count)> devices_ = {};
};

ControlAction apc_action_for_pad(uint8_t note);
ControlAction mvave_action_for_switch(int switch_index, bool held);
std::vector<uint8_t> build_apc_led_messages(int root_pitch_class, RootControlMode mode);
std::vector<uint8_t> build_litejam_major_scale_packet(int root_pitch_class);
std::vector<uint8_t> build_fret_zealot_major_scale_packet(int root_pitch_class);
// Four-byte cells: firmware LED index, red, green, blue.  The AUPHY/FretSpark
// matrix is indexed fret-major with physical strings high-E (0) to low-E (5).
std::vector<uint8_t> build_auphy_major_scale_pixels(int root_pitch_class, int max_fret);

} // namespace mao
