#include "fret_control.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <map>

namespace mao {
namespace {

constexpr std::array<int, kScaleDegreeCount> kMajorIntervals = {0, 2, 4, 5, 7, 9, 11};
constexpr std::array<RgbColor, kScaleDegreeCount> kMajorColors = {
	RgbColor{255, 0, 0},
	RgbColor{255, 96, 0},
	RgbColor{255, 255, 0},
	RgbColor{0, 255, 0},
	RgbColor{0, 255, 255},
	RgbColor{0, 0, 255},
	RgbColor{160, 0, 255},
};
constexpr std::array<int, 6> kStandardTuningLowToHigh = {40, 45, 50, 55, 59, 64};
constexpr std::array<const char *, kPitchClassCount> kPitchClassNames = {
	"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
};

constexpr std::array<std::array<const char *, 8>, 7> kLetterGlyphs = {{
	{{".###....", "#.......", "#.......", "#.......", "#.......", "#.......", ".###....", "........"}},
	{{"###.....", "#..#....", "#..#....", "#..#....", "#..#....", "#..#....", "###.....", "........"}},
	{{"####....", "#.......", "#.......", "###.....", "#.......", "#.......", "####....", "........"}},
	{{"####....", "#.......", "#.......", "###.....", "#.......", "#.......", "#.......", "........"}},
	{{".###....", "#.......", "#.......", "#.##....", "#..#....", "#..#....", ".###....", "........"}},
	{{".##.....", "#..#....", "#..#....", "####....", "#..#....", "#..#....", "#..#....", "........"}},
	{{"###.....", "#..#....", "#..#....", "###.....", "#..#....", "#..#....", "###.....", "........"}},
}};
constexpr std::array<const char *, 8> kSharpGlyph = {
	".....#.#", "........", ".....#.#", "........", "........", "........", "........", "........",
};

constexpr uint8_t kApcSolidFullBrightness = 0x96;
constexpr uint8_t kApcOff = 0;
constexpr uint8_t kApcDarkGray = 1;
constexpr uint8_t kApcLightGray = 2;
constexpr uint8_t kApcWhite = 3;
constexpr uint8_t kApcNextSemitoneColor = 98;
constexpr uint8_t kApcPreviousSemitoneColor = 101;
constexpr std::array<uint8_t, 12> kApcRootRelativeColors = {
	5, 9, 96, 109, 13, 21, 90, 37, 40, 49, 94, 57,
};
int normalize_pitch_class(int pitch_class)
{
	int normalized = pitch_class % kPitchClassCount;
	return normalized < 0 ? normalized + kPitchClassCount : normalized;
}

std::size_t device_index(ExternalDevice device)
{
	return static_cast<std::size_t>(device);
}

int natural_letter_index(int pitch_class)
{
	switch (normalize_pitch_class(pitch_class)) {
	case 0:
	case 1:
		return 0;
	case 2:
	case 3:
		return 1;
	case 4:
		return 2;
	case 5:
	case 6:
		return 3;
	case 7:
	case 8:
		return 4;
	case 9:
	case 10:
		return 5;
	case 11:
		return 6;
	default:
		return 0;
	}
}

bool is_sharp_pitch_class(int pitch_class)
{
	switch (normalize_pitch_class(pitch_class)) {
	case 1:
	case 3:
	case 6:
	case 8:
	case 10:
		return true;
	default:
		return false;
	}
}

uint8_t apc_background(int row_from_top, int column, int effective_root, RootControlMode mode)
{
	if (row_from_top < 6) {
		const int block_pitch_class = (row_from_top / 2) * 4 + (column / 2);
		const int interval = normalize_pitch_class(block_pitch_class - effective_root);
		return kApcRootRelativeColors[static_cast<std::size_t>(interval)];
	}
	if (column < 3)
		return kApcPreviousSemitoneColor;
	if (column >= 5)
		return kApcNextSemitoneColor;
	return mode == RootControlMode::Auto ? kApcLightGray : kApcDarkGray;
}

uint8_t scale_nibble(uint8_t component)
{
	return static_cast<uint8_t>((static_cast<unsigned int>(component) * 15u + 127u) / 255u);
}

} // namespace

int pitch_class_from_root_label(const char *label)
{
	if (!label || !label[0])
		return -1;

	int pitch_class = -1;
	switch (std::toupper(static_cast<unsigned char>(label[0]))) {
	case 'C':
		pitch_class = 0;
		break;
	case 'D':
		pitch_class = 2;
		break;
	case 'E':
		pitch_class = 4;
		break;
	case 'F':
		pitch_class = 5;
		break;
	case 'G':
		pitch_class = 7;
		break;
	case 'A':
		pitch_class = 9;
		break;
	case 'B':
		pitch_class = 11;
		break;
	default:
		return -1;
	}
	if (label[1] == '#')
		++pitch_class;
	else if (label[1] == 'b' || label[1] == 'B')
		--pitch_class;
	return normalize_pitch_class(pitch_class);
}

const char *pitch_class_name(int pitch_class)
{
	return kPitchClassNames[static_cast<std::size_t>(normalize_pitch_class(pitch_class))];
}

const std::array<int, kScaleDegreeCount> &major_scale_intervals()
{
	return kMajorIntervals;
}

const std::array<RgbColor, kScaleDegreeCount> &major_scale_colors()
{
	return kMajorColors;
}

int major_scale_degree(int root_pitch_class, int note_pitch_class)
{
	const int interval = normalize_pitch_class(note_pitch_class - root_pitch_class);
	for (std::size_t degree = 0; degree < kMajorIntervals.size(); ++degree) {
		if (kMajorIntervals[degree] == interval)
			return static_cast<int>(degree);
	}
	return -1;
}

RootControlMode FretControlState::mode() const
{
	return mode_;
}

int FretControlState::manual_root() const
{
	return manual_root_;
}

int FretControlState::detected_root() const
{
	return detected_root_;
}

int FretControlState::effective_root() const
{
	return mode_ == RootControlMode::Auto && detected_root_ >= 0 ? detected_root_ : manual_root_;
}

bool FretControlState::autoconnect() const
{
	return autoconnect_;
}

uint64_t FretControlState::revision() const
{
	return revision_;
}

DeviceConnectionState FretControlState::device_state(ExternalDevice device) const
{
	const std::size_t index = device_index(device);
	return index < devices_.size() ? devices_[index] : DeviceConnectionState::Error;
}

ExternalControlDisplay FretControlState::display() const
{
	ExternalControlDisplay result;
	result.visible = true;
	result.mode = mode_;
	result.effective_root = effective_root();
	result.autoconnect = autoconnect_;
	result.devices = devices_;
	return result;
}

void FretControlState::mark_changed()
{
	++revision_;
	if (revision_ == 0)
		revision_ = 1;
}

bool FretControlState::set_detected_root(int pitch_class)
{
	const int normalized = pitch_class < 0 ? -1 : normalize_pitch_class(pitch_class);
	if (detected_root_ == normalized)
		return false;
	detected_root_ = normalized;
	if (mode_ == RootControlMode::Auto)
		mark_changed();
	return true;
}

bool FretControlState::set_detected_root_label(const char *label)
{
	const int pitch_class = pitch_class_from_root_label(label);
	return pitch_class >= 0 && set_detected_root(pitch_class);
}

bool FretControlState::set_manual_root(int pitch_class)
{
	const int normalized = normalize_pitch_class(pitch_class);
	if (manual_root_ == normalized)
		return false;
	manual_root_ = normalized;
	mark_changed();
	return true;
}

bool FretControlState::shift_manual_root(int semitones)
{
	return set_manual_root(manual_root_ + semitones);
}

bool FretControlState::set_mode(RootControlMode mode)
{
	if (mode_ == mode)
		return false;
	mode_ = mode;
	mark_changed();
	return true;
}

bool FretControlState::toggle_mode()
{
	return set_mode(mode_ == RootControlMode::Auto ? RootControlMode::Manual : RootControlMode::Auto);
}

bool FretControlState::set_autoconnect(bool enabled)
{
	if (autoconnect_ == enabled)
		return false;
	autoconnect_ = enabled;
	mark_changed();
	return true;
}

bool FretControlState::toggle_autoconnect()
{
	return set_autoconnect(!autoconnect_);
}

bool FretControlState::set_device_state(ExternalDevice device, DeviceConnectionState state)
{
	const std::size_t index = device_index(device);
	if (index >= devices_.size() || devices_[index] == state)
		return false;
	devices_[index] = state;
	mark_changed();
	return true;
}

bool FretControlState::apply(const ControlAction &action)
{
	switch (action.kind) {
	case ControlActionKind::SetManualRoot:
		return set_manual_root(action.value);
	case ControlActionKind::ShiftManualRoot:
		return shift_manual_root(action.value);
	case ControlActionKind::ToggleManualRootCG:
		return set_manual_root(manual_root_ == 7 ? 0 : 7);
	case ControlActionKind::ToggleMode:
		return toggle_mode();
	case ControlActionKind::ToggleAutoconnect:
		return toggle_autoconnect();
	case ControlActionKind::None:
		return false;
	}
	return false;
}

ControlAction apc_action_for_pad(uint8_t note)
{
	if (note >= 64)
		return {};
	const int row_from_top = 7 - static_cast<int>(note / 8);
	const int column = note % 8;
	if (row_from_top < 6)
		return {ControlActionKind::SetManualRoot, (row_from_top / 2) * 4 + column / 2};
	if (column < 3)
		return {ControlActionKind::ShiftManualRoot, -1};
	if (column < 5)
		return {ControlActionKind::ToggleMode, 0};
	return {ControlActionKind::ShiftManualRoot, 1};
}

ControlAction mvave_action_for_switch(int switch_index, bool held)
{
	switch (switch_index) {
	case 0:
		return {ControlActionKind::ShiftManualRoot, held ? -2 : -1};
	case 1:
		return {ControlActionKind::ShiftManualRoot, held ? 2 : 1};
	case 2:
		return {ControlActionKind::ToggleManualRootCG, 0};
	case 3:
		return {ControlActionKind::ToggleMode, 0};
	default:
		return {};
	}
}

std::vector<uint8_t> build_apc_led_messages(int root_pitch_class, RootControlMode mode)
{
	const int root = normalize_pitch_class(root_pitch_class);
	const int letter = natural_letter_index(root);
	const bool sharp = is_sharp_pitch_class(root);
	const uint8_t glyph_color = mode == RootControlMode::Manual ? kApcWhite : kApcOff;
	std::vector<uint8_t> messages;
	messages.reserve(64 * 3);
	for (int note = 0; note < 64; ++note) {
		const int row_from_top = 7 - note / 8;
		const int column = note % 8;
		uint8_t color = apc_background(row_from_top, column, root, mode);
		if (kLetterGlyphs[static_cast<std::size_t>(letter)][static_cast<std::size_t>(row_from_top)][column] == '#')
			color = glyph_color;
		if (sharp && kSharpGlyph[static_cast<std::size_t>(row_from_top)][column] == '#')
			color = glyph_color;
		messages.push_back(kApcSolidFullBrightness);
		messages.push_back(static_cast<uint8_t>(note));
		messages.push_back(color);
	}
	return messages;
}

std::vector<uint8_t> build_litejam_major_scale_packet(int root_pitch_class)
{
	std::vector<uint8_t> packet;
	packet.reserve(192);
	packet.push_back(kScaleDegreeCount);
	for (int degree = 0; degree < kScaleDegreeCount; ++degree) {
		std::map<int, uint8_t> fret_masks;
		const int target = normalize_pitch_class(root_pitch_class + kMajorIntervals[static_cast<std::size_t>(degree)]);
		for (std::size_t string = 0; string < kStandardTuningLowToHigh.size(); ++string) {
			for (int fret = 0; fret <= 24; ++fret) {
				if (normalize_pitch_class(kStandardTuningLowToHigh[string] + fret) != target)
					continue;
				const int litejam_string = 5 - static_cast<int>(string);
				fret_masks[fret] = static_cast<uint8_t>(fret_masks[fret] | (1u << litejam_string));
			}
		}
		packet.push_back(static_cast<uint8_t>(fret_masks.size()));
		for (const auto &[fret, mask] : fret_masks) {
			packet.push_back(static_cast<uint8_t>(fret));
			packet.push_back(mask);
		}
		const RgbColor color = kMajorColors[static_cast<std::size_t>(degree)];
		packet.push_back(color.red);
		packet.push_back(color.green);
		packet.push_back(color.blue);
	}
	packet.push_back(0x45);
	packet.push_back(0x4e);
	packet.push_back(0x44);
	return packet;
}

std::vector<uint8_t> build_fret_zealot_major_scale_packet(int root_pitch_class)
{
	std::vector<uint8_t> packet = {0x40, 0x00, 0x00, 0x00};
	packet.reserve(256);
	for (std::size_t string = 0; string < kStandardTuningLowToHigh.size(); ++string) {
		for (int led_fret = 0; led_fret < 15; ++led_fret) {
			const int musical_fret = led_fret + 1;
			const int note = normalize_pitch_class(kStandardTuningLowToHigh[string] + musical_fret);
			const int degree = major_scale_degree(root_pitch_class, note);
			if (degree < 0)
				continue;
			const RgbColor color = kMajorColors[static_cast<std::size_t>(degree)];
			packet.push_back(0x00);
			packet.push_back(static_cast<uint8_t>((led_fret << 4) | scale_nibble(color.red)));
			packet.push_back(static_cast<uint8_t>((scale_nibble(color.green) << 4) | scale_nibble(color.blue)));
			packet.push_back(static_cast<uint8_t>(1u << (static_cast<int>(string) + 1)));
		}
	}
	return packet;
}

} // namespace mao
