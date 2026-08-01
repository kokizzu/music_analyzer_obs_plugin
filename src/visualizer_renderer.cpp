#include "visualizer_renderer.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstring>

namespace mao {
namespace {

constexpr std::size_t kMatrixRowCount = 2;
constexpr float kVisualizerAudibleRms = 0.0025f;

struct Color {
	uint8_t r = 255;
	uint8_t g = 255;
	uint8_t b = 255;
	uint8_t a = 255;
};

static constexpr Color kLabelColor{148, 163, 184, 255};
static constexpr Color kValueTextColor{199, 210, 224, 255};
static constexpr Color kWhiteTextColor{248, 250, 252, 255};
static constexpr int kCompleteContentShiftY = -10;
static constexpr int kBassGuitarContentShiftY = -8;
static constexpr int kHalfMusicKeyboardFirstRow = 1;
static constexpr int kHalfMusicKeyboardRowCount = 2;
static constexpr int kHalfMusicGuitarY = 284;

uint8_t blend_channel(uint8_t from, uint8_t to, float amount)
{
	const float value = static_cast<float>(from) + (static_cast<float>(to) - static_cast<float>(from)) * amount;
	return static_cast<uint8_t>(std::clamp(static_cast<int>(value + 0.5f), 0, 255));
}

Color blend_color(Color from, Color to, float amount)
{
	amount = std::clamp(amount, 0.0f, 1.0f);
	return Color{blend_channel(from.r, to.r, amount), blend_channel(from.g, to.g, amount),
		     blend_channel(from.b, to.b, amount), blend_channel(from.a, to.a, amount)};
}

float display_highlight_level(float level)
{
	constexpr float kFullHighlightLevel = 0.25f;
	if (level <= 0.0f)
		return 0.0f;

	return std::clamp(level / kFullHighlightLevel, 0.0f, 1.0f);
}

float note_cell_render_level(const NoteCell &cell)
{
	if (!cell.active)
		return 0.0f;
	return cell.visual_level >= 0.0f ? cell.visual_level : cell.level;
}

struct VisualLayout {
	int label_x = 28;
	int note_x = 150;
	int note_w = 480;
	int chord_x = 654;
	int stable_x = 782;
	int count_x = 822;
	int chord_w = 72;
	int stable_w = 92;
	int count_w = 64;
};

VisualLayout visual_layout(const VisualizerRenderer *visualizer)
{
	VisualLayout layout;
	const int width = static_cast<int>(visualizer->width);
	static constexpr int kMinNoteWidth = 420;
	static constexpr int kNoteToChordGap = 24;
	static constexpr int kColumnGap = 12;
	static constexpr int kRightMargin = 28;

	layout.count_x = std::max(layout.note_x + kMinNoteWidth + kNoteToChordGap + layout.chord_w + kColumnGap +
					  layout.stable_w + kColumnGap,
				  width - kRightMargin - layout.count_w);
	layout.stable_x = layout.count_x - kColumnGap - layout.stable_w;
	layout.chord_x = layout.stable_x - kColumnGap - layout.chord_w;
	layout.note_w = std::max(kMinNoteWidth, layout.chord_x - layout.note_x - kNoteToChordGap);
	return layout;
}

VisualLayout bass_guitar_visual_layout(const VisualizerRenderer *visualizer)
{
	VisualLayout layout;
	const int width = static_cast<int>(visualizer->width);
	static constexpr int kRightMargin = 28;
	static constexpr int kNoteToChordGap = 24;
	static constexpr int kColumnGap = 12;
	layout.stable_x = width - kRightMargin - layout.stable_w;
	layout.chord_x = layout.stable_x - kColumnGap - layout.chord_w;
	layout.note_w = std::max(420, layout.chord_x - layout.note_x - kNoteToChordGap);
	return layout;
}

const std::array<const char *, 7> glyph_rows(char c)
{
	switch (c) {
	case 'a':
		return {"00000", "00000", "01110", "00001", "01111", "10001", "01111"};
	case 'j':
		return {"00010", "00000", "00110", "00010", "00010", "10010", "01100"};
	case 'm':
		return {"00000", "00000", "11010", "10101", "10101", "10101", "10101"};
	case 'o':
		return {"00000", "00000", "01110", "10001", "10001", "10001", "01110"};
	case 'p':
		return {"00000", "00000", "11110", "10001", "11110", "10000", "10000"};
	case 's':
		return {"00000", "00000", "01111", "10000", "01110", "00001", "11110"};
	case 'u':
		return {"00000", "00000", "10001", "10001", "10001", "10011", "01101"};
	case 'w':
		return {"00000", "00000", "10001", "10101", "10101", "10101", "01010"};
	case 'A':
		return {"01110", "10001", "10001", "11111", "10001", "10001", "10001"};
	case 'B':
		return {"11110", "10001", "10001", "11110", "10001", "10001", "11110"};
	case 'C':
		return {"01111", "10000", "10000", "10000", "10000", "10000", "01111"};
	case 'D':
		return {"11110", "10001", "10001", "10001", "10001", "10001", "11110"};
	case 'E':
		return {"11111", "10000", "10000", "11110", "10000", "10000", "11111"};
	case 'F':
		return {"11111", "10000", "10000", "11110", "10000", "10000", "10000"};
	case 'G':
		return {"01111", "10000", "10000", "10011", "10001", "10001", "01111"};
	case 'H':
		return {"10001", "10001", "10001", "11111", "10001", "10001", "10001"};
	case 'I':
		return {"11111", "00100", "00100", "00100", "00100", "00100", "11111"};
	case 'J':
		return {"00111", "00010", "00010", "00010", "00010", "10010", "01100"};
	case 'K':
		return {"10001", "10010", "10100", "11000", "10100", "10010", "10001"};
	case 'L':
		return {"10000", "10000", "10000", "10000", "10000", "10000", "11111"};
	case 'M':
		return {"10001", "11011", "10101", "10101", "10001", "10001", "10001"};
	case 'N':
		return {"10001", "11001", "10101", "10011", "10001", "10001", "10001"};
	case 'O':
		return {"01110", "10001", "10001", "10001", "10001", "10001", "01110"};
	case 'P':
		return {"11110", "10001", "10001", "11110", "10000", "10000", "10000"};
	case 'Q':
		return {"01110", "10001", "10001", "10001", "10101", "10010", "01101"};
	case 'R':
		return {"11110", "10001", "10001", "11110", "10100", "10010", "10001"};
	case 'S':
		return {"01111", "10000", "10000", "01110", "00001", "00001", "11110"};
	case 'T':
		return {"11111", "00100", "00100", "00100", "00100", "00100", "00100"};
	case 'U':
		return {"10001", "10001", "10001", "10001", "10001", "10001", "01110"};
	case 'V':
		return {"10001", "10001", "10001", "10001", "10001", "01010", "00100"};
	case 'W':
		return {"10001", "10001", "10001", "10101", "10101", "10101", "01010"};
	case 'X':
		return {"10001", "10001", "01010", "00100", "01010", "10001", "10001"};
	case 'Y':
		return {"10001", "10001", "01010", "00100", "00100", "00100", "00100"};
	case 'Z':
		return {"11111", "00001", "00010", "00100", "01000", "10000", "11111"};
	case '0':
		return {"01110", "10001", "10011", "10101", "11001", "10001", "01110"};
	case '1':
		return {"00100", "01100", "00100", "00100", "00100", "00100", "01110"};
	case '2':
		return {"01110", "10001", "00001", "00010", "00100", "01000", "11111"};
	case '3':
		return {"11110", "00001", "00001", "01110", "00001", "00001", "11110"};
	case '4':
		return {"00010", "00110", "01010", "10010", "11111", "00010", "00010"};
	case '5':
		return {"11111", "10000", "10000", "11110", "00001", "00001", "11110"};
	case '6':
		return {"01111", "10000", "10000", "11110", "10001", "10001", "01110"};
	case '7':
		return {"11111", "00001", "00010", "00100", "01000", "01000", "01000"};
	case '8':
		return {"01110", "10001", "10001", "01110", "10001", "10001", "01110"};
	case '9':
		return {"01110", "10001", "10001", "01111", "00001", "00001", "11110"};
	case '#':
		return {"01010", "01010", "11111", "01010", "11111", "01010", "01010"};
	case '+':
		return {"00000", "00100", "00100", "11111", "00100", "00100", "00000"};
	case '?':
		return {"01110", "10001", "00001", "00010", "00100", "00000", "00100"};
	case '~':
		return {"00000", "00000", "01001", "10110", "00000", "00000", "00000"};
	case '!':
		return {"00100", "00100", "00100", "00100", "00100", "00000", "00100"};
	case '-':
		return {"00000", "00000", "00000", "11111", "00000", "00000", "00000"};
	case '.':
		return {"00000", "00000", "00000", "00000", "00000", "01100", "01100"};
	case ':':
		return {"00000", "01100", "01100", "00000", "01100", "01100", "00000"};
	case '%':
		return {"11001", "11010", "00100", "01000", "10110", "00110", "00000"};
	case '/':
		return {"00001", "00010", "00010", "00100", "01000", "01000", "10000"};
	case ' ':
		return {"00000", "00000", "00000", "00000", "00000", "00000", "00000"};
	default:
		return {"11111", "00001", "00010", "00100", "00100", "00000", "00100"};
	}
}

void put_pixel(VisualizerRenderer *visualizer, int x, int y, Color color)
{
	if (x < 0 || y < 0 || x >= static_cast<int>(visualizer->width) || y >= static_cast<int>(visualizer->height))
		return;

	const std::size_t offset = (static_cast<std::size_t>(y) * visualizer->width + static_cast<std::size_t>(x)) * 4;
	visualizer->pixels[offset + 0] = color.r;
	visualizer->pixels[offset + 1] = color.g;
	visualizer->pixels[offset + 2] = color.b;
	visualizer->pixels[offset + 3] = color.a;
}

void fill_rect(VisualizerRenderer *visualizer, int x, int y, int w, int h, Color color)
{
	const int x0 = std::max(0, x);
	const int y0 = std::max(0, y);
	const int x1 = std::min(static_cast<int>(visualizer->width), x + w);
	const int y1 = std::min(static_cast<int>(visualizer->height), y + h);

	for (int yy = y0; yy < y1; ++yy) {
		for (int xx = x0; xx < x1; ++xx)
			put_pixel(visualizer, xx, yy, color);
	}
}

void draw_text_impl(VisualizerRenderer *visualizer, int x, int y, const char *text, uint32_t scale, Color color,
		    bool preserve_chord_lowercase)
{
	if (!text)
		return;

	int cursor = x;
	for (const char *p = text; *p; ++p) {
		char c = *p;
		const bool chord_lowercase =
			c == 'a' || c == 'j' || c == 'm' || c == 'o' || c == 'p' || c == 's' || c == 'u' || c == 'w';
		if (c >= 'a' && c <= 'z' && (!preserve_chord_lowercase || !chord_lowercase))
			c = static_cast<char>(c - 'a' + 'A');

		const auto rows = glyph_rows(c);
		for (int row = 0; row < 7; ++row) {
			for (int col = 0; col < 5; ++col) {
				if (rows[row][col] != '1')
					continue;
				fill_rect(visualizer, cursor + col * static_cast<int>(scale),
					  y + row * static_cast<int>(scale), static_cast<int>(scale),
					  static_cast<int>(scale), color);
			}
		}
		cursor += static_cast<int>(scale) * 6;
	}
}

void draw_text(VisualizerRenderer *visualizer, int x, int y, const char *text, uint32_t scale, Color color)
{
	draw_text_impl(visualizer, x, y, text, scale, color, false);
}

void draw_chord_text(VisualizerRenderer *visualizer, int x, int y, const char *text, uint32_t scale, Color color)
{
	if (!text || !*text) {
		draw_text_impl(visualizer, x, y, "--", scale, color, true);
		return;
	}

	int line_y = y;
	const int line_pitch = static_cast<int>(scale) * 8;
	const char *start = text;
	while (*start) {
		const char *end = start;
		while (*end && *end != '=')
			++end;

		char line[32] = {};
		const std::size_t len = std::min<std::size_t>(sizeof(line) - 1, static_cast<std::size_t>(end - start));
		std::memcpy(line, start, len);
		line[len] = '\0';
		if (line[0])
			draw_text_impl(visualizer, x, line_y, line, scale, color, true);
		line_y += line_pitch;

		start = *end == '=' ? end + 1 : end;
	}
}

int text_width(const char *text, uint32_t scale)
{
	return text ? static_cast<int>(std::strlen(text)) * static_cast<int>(scale) * 6 : 0;
}

bool is_pitch_class_token(const char *token)
{
	if (!token || token[0] < 'A' || token[0] > 'G')
		return false;
	return token[1] == '\0' || (token[1] == '#' && token[2] == '\0');
}

bool root_token_matches(const char *token, const char *root)
{
	return is_pitch_class_token(token) && is_pitch_class_token(root) && std::strcmp(token, root) == 0;
}

void draw_root_candidates(VisualizerRenderer *visualizer, int x, int y, const char *candidates, const char *root)
{
	constexpr uint32_t kScale = 2;
	draw_text(visualizer, x, y, "ROOT", kScale, kLabelColor);
	x += text_width("ROOT ", kScale);

	const char *text = candidates && candidates[0] ? candidates : "-- 0%";
	while (*text) {
		if (*text == ' ') {
			x += static_cast<int>(kScale) * 6;
			++text;
			continue;
		}

		char token[16] = {};
		std::size_t len = 0;
		while (text[len] && text[len] != ' ' && len + 1 < sizeof(token)) {
			token[len] = text[len];
			++len;
		}
		token[len] = '\0';
		const int token_w = text_width(token, kScale);
		const bool selected_root = root_token_matches(token, root);
		if (selected_root) {
			fill_rect(visualizer, x - 4, y - 2, token_w + 8, 18, Color{20, 48, 116, 230});
			draw_text(visualizer, x, y, token, kScale, Color{147, 197, 253, 255});
		} else {
			const Color color = is_pitch_class_token(token) ? kWhiteTextColor : kLabelColor;
			draw_text(visualizer, x, y, token, kScale, color);
		}
		x += token_w;
		text += len;
		while (*text && *text != ' ') {
			++text;
		}
	}
}

int draw_status_pair(VisualizerRenderer *visualizer, int x, int y, const char *label, const char *value)
{
	constexpr uint32_t kScale = 2;
	constexpr int kPairGap = 8;
	static constexpr Color kStatusLabelColor{104, 116, 132, 255};
	draw_text(visualizer, x, y, label, kScale, kStatusLabelColor);
	x += text_width(label, kScale);
	draw_text(visualizer, x, y, value, kScale, kValueTextColor);
	x += text_width(value, kScale);
	return x + kPairGap;
}

void format_band_percentage(char *output, std::size_t output_size, float energy)
{
	const float percentage = std::max(0.0f, energy * 100.0f);
	if (percentage > 99.0f)
		std::snprintf(output, output_size, "MAX");
	else
		std::snprintf(output, output_size, "%.0f%%", percentage);
}

void draw_status_line(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot, float snapshot_age,
		      int y_offset = 0)
{
	char rms[8] = {};
	char low[8] = {};
	char mid[8] = {};
	char high[8] = {};
	char age[8] = {};
	char drop[24] = {};
	std::snprintf(rms, sizeof(rms), "%4.2f", std::clamp(snapshot.rms, 0.0f, 9.99f));
	format_band_percentage(low, sizeof(low), snapshot.low_energy);
	format_band_percentage(mid, sizeof(mid), snapshot.mid_energy);
	format_band_percentage(high, sizeof(high), snapshot.high_energy);
	std::snprintf(age, sizeof(age), "%.1fs", std::clamp(snapshot_age, 0.0f, 99.9f));
	std::snprintf(drop, sizeof(drop), "%llu", static_cast<unsigned long long>(snapshot.dropped_windows));

	int x = 28;
	const int y = std::max(0, 58 + y_offset);
	x = draw_status_pair(visualizer, x, y, "LOW ", low);
	x = draw_status_pair(visualizer, x, y, "MID ", mid);
	x = draw_status_pair(visualizer, x, y, "HIGH ", high);
	x = draw_status_pair(visualizer, x, y, "AGE ", age);
	x = draw_status_pair(visualizer, x, y, "DROP ", drop);
	if (snapshot.battery_percent >= 0.0f) {
		char battery[8] = {};
		std::snprintf(battery, sizeof(battery), "%.0f",
			      std::clamp(snapshot.battery_percent, 0.0f, 100.0f));
		x = draw_status_pair(visualizer, x, y, snapshot.battery_charging ? "BAT+ " : "BAT ", battery);
	}
	if (snapshot.ram_mb >= 0.0f) {
		char ram[8] = {};
		std::snprintf(ram, sizeof(ram), "%.0fMB", std::clamp(snapshot.ram_mb, 0.0f, 999.0f));
		x = draw_status_pair(visualizer, x, y, "RAM ", ram);
	}
	if (snapshot.cpu_percent >= 0.0f) {
		char cpu[16] = {};
		std::snprintf(cpu, sizeof(cpu), "%.0f", std::max(snapshot.cpu_percent, 0.0f));
		x = draw_status_pair(visualizer, x, y, "CPU ", cpu);
	}
	(void)draw_status_pair(visualizer, x, y, "RMS ", rms);
}

void draw_muted_mic_indicator(VisualizerRenderer *visualizer)
{
	const int size = 34;
	const int x = std::max(8, static_cast<int>(visualizer->width) - size - 18);
	const int y = 22;
	const Color panel{12, 16, 22, 230};
	const Color border{58, 68, 82, 230};
	const Color icon{248, 250, 252, 255};
	const Color slash{248, 113, 113, 255};

	fill_rect(visualizer, x, y, size, size, panel);
	fill_rect(visualizer, x, y, size, 1, border);
	fill_rect(visualizer, x, y + size - 1, size, 1, border);
	fill_rect(visualizer, x, y, 1, size, border);
	fill_rect(visualizer, x + size - 1, y, 1, size, border);

	const int mic_x = x + 13;
	const int mic_y = y + 6;
	fill_rect(visualizer, mic_x + 2, mic_y, 6, 2, icon);
	fill_rect(visualizer, mic_x, mic_y + 2, 10, 12, icon);
	fill_rect(visualizer, mic_x + 2, mic_y + 14, 6, 2, icon);
	fill_rect(visualizer, mic_x + 4, mic_y + 16, 2, 5, icon);
	fill_rect(visualizer, mic_x, mic_y + 21, 10, 2, icon);
	fill_rect(visualizer, mic_x - 4, mic_y + 9, 2, 7, icon);
	fill_rect(visualizer, mic_x + 12, mic_y + 9, 2, 7, icon);
	fill_rect(visualizer, mic_x - 2, mic_y + 15, 2, 2, icon);
	fill_rect(visualizer, mic_x + 10, mic_y + 15, 2, 2, icon);

	for (int i = 0; i < 22; ++i)
		fill_rect(visualizer, x + 7 + i, y + 25 - i, 3, 3, slash);
}

void draw_drum_chart(VisualizerRenderer *visualizer, int x, int y, int w, const DrumState &drum,
		     const std::vector<DrumBar> &history, uint32_t label_scale = 2)
{
	const int label_h = 18;
	const int chart_y = y + label_h + 4;
	const int chart_h = 28;
	const Color bg{24, 30, 38, 210};
	const Color active_bg{242, 149, 40, 235};
	const Color border{86, 96, 111, 230};
	const Color text{240, 244, 248, 255};
	const int label_bar_w = std::clamp(static_cast<int>(drum.level * static_cast<float>(w) + 0.5f), 0, w);

	fill_rect(visualizer, x, y, w, label_h, bg);
	if (label_bar_w > 0)
		fill_rect(visualizer, x, y, label_bar_w, label_h, active_bg);
	fill_rect(visualizer, x, y, w, 1, border);
	fill_rect(visualizer, x, y + label_h - 1, w, 1, border);
	draw_text(visualizer, x + 5, y + (label_scale == 1 ? 5 : 3), drum.label, label_scale, text);

	fill_rect(visualizer, x, chart_y, w, chart_h, bg);
	fill_rect(visualizer, x, chart_y, w, 1, border);
	fill_rect(visualizer, x, chart_y + chart_h - 1, w, 1, border);

	for (const DrumBar &bar : history) {
		if (bar.age < 0.0f || bar.age > 1.0f || bar.level <= 0.0f)
			continue;
		const int bar_x = x + std::clamp(static_cast<int>((1.0f - bar.age) * static_cast<float>(w - 4)), 0, w - 4);
		const int bar_h = std::clamp(static_cast<int>(bar.level * static_cast<float>(chart_h - 4)), 2, chart_h - 4);
		fill_rect(visualizer, bar_x, chart_y + chart_h - 2 - bar_h, 3, bar_h, active_bg);
	}
}

Color octave_color_from_midi(int midi, Color fallback)
{
	if (midi < 0)
		return fallback;

	const int octave = std::clamp(midi / 12 - 1, 0, 8);
	static constexpr Color kOctaveColors[9] = {
		{255, 59, 48, 255},   {255, 59, 48, 255},   {255, 149, 0, 255},
		{255, 214, 10, 255},  {48, 209, 88, 255},   {64, 200, 255, 255},
		{10, 132, 255, 255},  {191, 90, 242, 255},  {255, 55, 180, 255},
	};
	return kOctaveColors[octave];
}

void draw_note_cell(VisualizerRenderer *visualizer, int x, int y, int w, int h, const NoteCell &cell, Color accent)
{
	const Color idle_bg{24, 30, 38, 210};
	const Color border{58, 68, 82, 220};
	const Color idle_text{91, 106, 124, 255};
	const Color active_color = octave_color_from_midi(cell.midi, accent);
	const float level = display_highlight_level(note_cell_render_level(cell));
	const Color bg = cell.active ? blend_color(idle_bg, active_color, level * 0.42f) : idle_bg;
	const Color stroke = cell.active ? blend_color(border, active_color, level * 0.82f) : border;

	fill_rect(visualizer, x, y, w, h, bg);
	fill_rect(visualizer, x, y, w, 1, stroke);
	fill_rect(visualizer, x, y + h - 1, w, 1, stroke);
	fill_rect(visualizer, x, y, 1, h, stroke);
	fill_rect(visualizer, x + w - 1, y, 1, h, stroke);
	if (!cell.label[0])
		return;

	const int text_width = static_cast<int>(std::strlen(cell.label)) * 12;
	const Color active_text = blend_color(active_color, Color{255, 255, 255, 255}, 0.20f + level * 0.18f);
	draw_text(visualizer, x + std::max(2, (w - text_width) / 2), y + std::max(2, (h - 14) / 2),
		  cell.label, 2, cell.active ? active_text : idle_text);
}

int note_grid_active_count(const NoteGrid &notes);

enum StableSlot : std::size_t {
	StableBass = 0,
	StableVocal = 1,
	StableOther = 2,
	StableKeyboard = 3,
	StableGuitar = 4,
};

bool has_display_label(const char *label)
{
	return label && label[0] && std::strcmp(label, "--") != 0;
}

void copy_label(char *dst, std::size_t dst_size, const char *src)
{
	if (!dst || dst_size == 0)
		return;
	std::snprintf(dst, dst_size, "%s", src ? src : "");
}

const char *pitch_class_name_from_midi(int midi)
{
	static constexpr const char *kNames[12] = {"C", "C#", "D", "D#", "E", "F",
						   "F#", "G", "G#", "A", "A#", "B"};
	return kNames[((midi % 12) + 12) % 12];
}

struct StableCandidate {
	char label[64] = {};
	float score = 0.0f;
};

bool suffix_equals(const char *suffix, std::size_t suffix_len, const char *expected)
{
	return std::strlen(expected) == suffix_len && std::strncmp(suffix, expected, suffix_len) == 0;
}

bool simplify_major_minor_chord_component(const char *start, std::size_t len, char *dst, std::size_t dst_size)
{
	if (!start || len == 0 || dst_size == 0)
		return false;
	if (start[0] < 'A' || start[0] > 'G')
		return false;

	std::size_t root_len = 1;
	if (len > 1 && start[1] == '#')
		root_len = 2;
	const char *suffix = start + root_len;
	const std::size_t suffix_len = len - root_len;

	char root[4] = {};
	std::memcpy(root, start, root_len);
	root[root_len] = '\0';

	if (suffix_len == 0 || suffix_equals(suffix, suffix_len, "6") ||
	    suffix_equals(suffix, suffix_len, "7") || suffix_equals(suffix, suffix_len, "9") ||
	    suffix_equals(suffix, suffix_len, "maj7") || suffix_equals(suffix, suffix_len, "maj9") ||
	    suffix_equals(suffix, suffix_len, "add9")) {
		std::snprintf(dst, dst_size, "%s", root);
		return true;
	}

	if (suffix_equals(suffix, suffix_len, "m") || suffix_equals(suffix, suffix_len, "m6") ||
	    suffix_equals(suffix, suffix_len, "m7") || suffix_equals(suffix, suffix_len, "m9")) {
		std::snprintf(dst, dst_size, "%sm", root);
		return true;
	}

	return false;
}

bool simplify_major_minor_chord_label(const char *label, char *dst, std::size_t dst_size)
{
	if (!has_display_label(label) || !dst || dst_size == 0)
		return false;
	const char *end = label;
	while (*end && *end != '=')
		++end;
	return simplify_major_minor_chord_component(label, static_cast<std::size_t>(end - label), dst, dst_size);
}

const NoteCell *strongest_note_cell(const NoteGrid &notes, float min_level)
{
	const NoteCell *best = nullptr;
	for (const auto &row : notes.rows) {
		for (const NoteCell &cell : row) {
			if (!cell.active || !has_display_label(cell.label) || cell.level < min_level)
				continue;
			if (!best || cell.level > best->level)
				best = &cell;
		}
	}
	return best;
}

StableCandidate stable_candidate_label(const NoteGrid &notes, const InstrumentState *chord)
{
	StableCandidate candidate;
	if (chord && has_display_label(chord->label) && chord->confidence >= 0.42f) {
		char simplified[64] = {};
		if (simplify_major_minor_chord_label(chord->label, simplified, sizeof(simplified))) {
			copy_label(candidate.label, sizeof(candidate.label), simplified);
			candidate.score = std::clamp(chord->confidence * 1.35f, 0.0f, 1.0f);
			return candidate;
		}
	}

	const NoteCell *note = strongest_note_cell(notes, 0.46f);
	if (note && note->midi >= 0) {
		copy_label(candidate.label, sizeof(candidate.label), pitch_class_name_from_midi(note->midi));
		candidate.score = std::clamp(note->level, 0.0f, 1.0f);
	}
	return candidate;
}

void clear_stable_state(StableDisplayState &state)
{
	state.label[0] = '\0';
	state.vote_pos = 0;
	state.vote_count = 0;
	for (auto &vote : state.votes)
		vote = {};
}

void add_stable_vote(StableDisplayState &state, const StableCandidate &candidate, uint64_t sequence)
{
	auto &vote = state.votes[state.vote_pos];
	copy_label(vote.label, sizeof(vote.label), candidate.label);
	vote.score = candidate.score;
	vote.sequence = sequence;
	state.vote_pos = (state.vote_pos + 1) % state.votes.size();
	state.vote_count = std::min<std::size_t>(state.vote_count + 1, state.votes.size());
}

void choose_stable_vote_label(StableDisplayState &state, bool prefer_frequency)
{
	char best_label[64] = {};
	float best_score = 0.0f;
	int best_hits = 0;
	uint64_t best_latest_sequence = 0;

	for (std::size_t i = 0; i < state.vote_count; ++i) {
		const auto &vote = state.votes[i];
		if (!has_display_label(vote.label) || vote.score <= 0.0f)
			continue;

		float score = 0.0f;
		int hits = 0;
		uint64_t latest_sequence = 0;
		for (std::size_t j = 0; j < state.vote_count; ++j) {
			const auto &other = state.votes[j];
			if (std::strcmp(vote.label, other.label) != 0)
				continue;
			score += other.score;
			++hits;
			latest_sequence = std::max(latest_sequence, other.sequence);
		}

		const bool better = prefer_frequency
					    ? (hits > best_hits ||
					       (hits == best_hits && latest_sequence > best_latest_sequence) ||
					       (hits == best_hits && latest_sequence == best_latest_sequence &&
						score > best_score + 0.001f))
					    : (score > best_score + 0.001f ||
					       (std::abs(score - best_score) <= 0.001f && hits > best_hits) ||
					       (std::abs(score - best_score) <= 0.001f && hits == best_hits &&
						latest_sequence > best_latest_sequence));
		if (better) {
			best_score = score;
			best_hits = hits;
			best_latest_sequence = latest_sequence;
			copy_label(best_label, sizeof(best_label), vote.label);
		}
	}

	if (best_score > 0.0f)
		copy_label(state.label, sizeof(state.label), best_label);
}

void update_stable_label(VisualizerRenderer *visualizer, StableSlot slot, const AnalysisSnapshot &snapshot,
			 const NoteGrid &notes, const InstrumentState *chord, bool prefer_frequency)
{
	StableDisplayState &state = visualizer->stable_labels[slot];
	if (snapshot.sequence != 0 && state.last_sequence == snapshot.sequence)
		return;
	state.last_sequence = snapshot.sequence;

	if (!snapshot.audio_seen || snapshot.rms < 0.006f) {
		clear_stable_state(state);
		return;
	}

	const StableCandidate candidate = stable_candidate_label(notes, chord);
	if (!has_display_label(candidate.label))
		return;

	add_stable_vote(state, candidate, snapshot.sequence);
	choose_stable_vote_label(state, prefer_frequency);
}

void draw_stable_label(VisualizerRenderer *visualizer, const VisualLayout &layout, int y, const char *label,
		       Color color)
{
	if (!has_display_label(label))
		return;

	std::size_t max_line = 0;
	std::size_t line_count = 1;
	std::size_t current = 0;
	for (const char *p = label; *p; ++p) {
		if (*p == '=') {
			max_line = std::max(max_line, current);
			current = 0;
			++line_count;
		} else {
			++current;
		}
	}
	max_line = std::max(max_line, current);

	const bool equivalent_fits = line_count <= 2 && max_line <= 6;
	const bool compact = !equivalent_fits && (std::strlen(label) > 5 || std::strchr(label, '=') != nullptr);
	draw_chord_text(visualizer, layout.stable_x, y + (compact ? 4 : 2), label, compact ? 1 : 2, color);
}

int draw_instrument_rows(VisualizerRenderer *visualizer, const VisualLayout &layout, int y, const char *name,
			 const NoteGrid &notes, const InstrumentState *chord, const char *stable_label, Color accent,
			 std::size_t row_count, bool draw_note_count = true)
{
	const int cell_w = std::max(30, layout.note_w / 12);
	const int cell_h = 17;
	const int row_pitch = 18;
	const Color dim = kLabelColor;
	const Color chord_text = kWhiteTextColor;
	const Color count_text = kValueTextColor;
	const char *chord_label = chord && chord->label[0] ? chord->label : "--";

	draw_text(visualizer, layout.label_x, y + 2, name, 2, dim);
	row_count = std::clamp<std::size_t>(row_count, 1, notes.rows.size());
	for (std::size_t row = 0; row < row_count; ++row) {
		for (int i = 0; i < 12; ++i) {
			draw_note_cell(visualizer, layout.note_x + i * cell_w, y + static_cast<int>(row) * row_pitch,
				       cell_w - 2, cell_h, notes.rows[row][i], accent);
		}
	}
	if (chord)
		draw_chord_text(visualizer, layout.chord_x, y + 2, chord_label, 2, chord_text);
	draw_stable_label(visualizer, layout, y, stable_label, chord_text);
	if (draw_note_count) {
		char note_count[12] = {};
		std::snprintf(note_count, sizeof(note_count), "%d", note_grid_active_count(notes));
		draw_text(visualizer, layout.count_x, y + 2, note_count, 2, count_text);
	}
	return y + static_cast<int>(row_count) * row_pitch + 4;
}

int note_grid_active_count(const NoteGrid &notes)
{
	int count = 0;
	for (const auto &row : notes.rows) {
		for (const NoteCell &cell : row) {
			if (cell.active)
				++count;
		}
	}
	return count;
}

float note_grid_midi_level(const NoteGrid &notes, int midi)
{
	float level = 0.0f;
	for (const auto &row : notes.rows) {
		for (const NoteCell &cell : row) {
			if (cell.active && cell.midi == midi)
				level = std::max(level, note_cell_render_level(cell));
		}
	}
	return std::clamp(level, 0.0f, 1.0f);
}

float note_grid_lower_same_pitch_level(const NoteGrid &notes, int midi)
{
	float level = 0.0f;
	const int pitch_class = ((midi % 12) + 12) % 12;
	for (const auto &row : notes.rows) {
		for (const NoteCell &cell : row) {
			if (!cell.active || cell.midi < 0 || cell.midi >= midi)
				continue;
			if (((cell.midi % 12) + 12) % 12 != pitch_class)
				continue;
			const int interval = midi - cell.midi;
			if (interval != 12 && interval != 24 && interval != 36)
				continue;
			level = std::max(level, note_cell_render_level(cell));
		}
	}
	return std::clamp(level, 0.0f, 1.0f);
}

float guitar_note_grid_midi_level(const NoteGrid &notes, int midi)
{
	const float raw_level = note_grid_midi_level(notes, midi);
	const float lower_level = note_grid_lower_same_pitch_level(notes, midi);
	if (raw_level > 0.0f && lower_level >= raw_level * 0.55f)
		return raw_level * 0.14f;
	return raw_level;
}

int fold_midi_to_piano_range(int midi)
{
	constexpr int kFirstPianoMidi = 24;
	constexpr int kLastPianoMidi = 95;
	constexpr int kFirstHighOctaveMidi = 84;
	const int pitch_class = ((midi % 12) + 12) % 12;
	if (midi < kFirstPianoMidi)
		return kFirstPianoMidi + pitch_class;
	if (midi > kLastPianoMidi)
		return kFirstHighOctaveMidi + pitch_class;
	return midi;
}

float piano_key_level(const NoteGrid &notes, int midi)
{
	float level = 0.0f;
	for (const auto &row : notes.rows) {
		for (const NoteCell &cell : row) {
			if (cell.active && cell.midi >= 0 && fold_midi_to_piano_range(cell.midi) == midi)
				level = std::max(level, note_cell_render_level(cell));
		}
	}
	const float lower_level = note_grid_lower_same_pitch_level(notes, midi);
	if (level > 0.0f && lower_level >= level * 0.55f)
		level *= 0.18f;
	return std::clamp(level, 0.0f, 1.0f);
}

void write_note_name_with_octave(char *dst, std::size_t dst_size, int midi)
{
	if (!dst || dst_size == 0)
		return;
	static constexpr const char *kNames[12] = {"C", "C#", "D", "D#", "E", "F",
						   "F#", "G", "G#", "A", "A#", "B"};
	const int pitch_class = ((midi % 12) + 12) % 12;
	const int octave = std::clamp(midi / 12 - 1, 0, 9);
	std::snprintf(dst, dst_size, "%s%d", kNames[pitch_class], octave);
}

int pitch_class_from_note_label(const char *label)
{
	if (!label || !label[0] || label[0] == '-')
		return -1;

	int pitch_class = -1;
	switch (label[0]) {
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
		pitch_class = (pitch_class + 1) % 12;
	return pitch_class;
}

Color pitch_class_color(int pitch_class)
{
	static constexpr Color kColors[12] = {
		{255, 59, 48, 255},	{255, 128, 0, 255},    {255, 214, 10, 255},
		{180, 255, 30, 255},	{48, 209, 88, 255},    {0, 220, 190, 255},
		{64, 200, 255, 255},	{10, 132, 255, 255},   {94, 92, 230, 255},
		{191, 90, 242, 255},	{255, 55, 180, 255},   {255, 105, 120, 255},
	};
	return kColors[((pitch_class % 12) + 12) % 12];
}

void write_scale_degree(char *dst, std::size_t dst_size, int root_pitch_class, int pitch_class)
{
	if (!dst || dst_size == 0) {
		return;
	}
	dst[0] = '\0';
	if (root_pitch_class < 0) {
		return;
	}

	static constexpr const char *kDegrees[12] = {
		"1", "1#", "2", "2#", "3", "4", "4#", "5", "5#", "6", "6#", "7",
	};
	const int offset = (pitch_class - root_pitch_class + 12) % 12;
	std::snprintf(dst, dst_size, "%s", kDegrees[offset]);
}

void draw_centered_text(VisualizerRenderer *visualizer, int x, int y, int w, int h, const char *text, uint32_t scale,
			Color color)
{
	if (!text || !text[0])
		return;
	const int text_width = static_cast<int>(std::strlen(text)) * static_cast<int>(scale) * 6;
	const int text_height = static_cast<int>(scale) * 7;
	draw_text(visualizer, x + std::max(1, (w - text_width) / 2), y + std::max(1, (h - text_height) / 2), text,
		  scale, color);
}

int draw_piano_keyboard(VisualizerRenderer *visualizer, const VisualLayout &layout, int y, const NoteGrid &notes,
			const InstrumentState &chord, const char *stable_label, int degree_root_pitch_class,
			int first_row = 0, int row_count = 3, bool draw_note_count = true)
{
	static constexpr int kTotalRowCount = 3;
	static constexpr int kOctavesPerRow = 2;
	static constexpr int kWhiteKeysPerRow = 14;
	static constexpr int kWhiteOffsets[kWhiteKeysPerRow] = {0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23};
	static constexpr int kBlackOffsets[10] = {1, 3, 6, 8, 10, 13, 15, 18, 20, 22};
	static constexpr int kBlackAfterWhite[10] = {0, 1, 3, 4, 5, 7, 8, 10, 11, 12};

	const int header_h = 16;
	const int row_h = 30;
	const int row_gap = 6;
	const int max_keyboard_w = std::max(280, layout.note_w);
	const int white_w = std::clamp(max_keyboard_w / kWhiteKeysPerRow, 18, 42);
	const int white_h = 28;
	const int black_w = std::max(10, white_w * 3 / 5);
	const int black_h = 16;
	const Color dim = kLabelColor;
	const Color label_text = kLabelColor;
	const Color white_key{218, 225, 235, 235};
	const Color black_key{20, 25, 32, 245};
	const Color border{58, 68, 82, 230};
	const Color chord_text = kWhiteTextColor;
	const Color count_text = kValueTextColor;
	const Color active_text{10, 15, 22, 255};
	const char *chord_label = chord.label[0] ? chord.label : "--";
	first_row = std::clamp(first_row, 0, kTotalRowCount - 1);
	row_count = std::clamp(row_count, 1, kTotalRowCount - first_row);
	if (degree_root_pitch_class < 0)
		degree_root_pitch_class = pitch_class_from_note_label(chord_label);

	draw_text(visualizer, layout.label_x, y + 38, "KEYS", 2, dim);
	draw_chord_text(visualizer, layout.chord_x, y + 16, chord_label, 2, chord_text);
	draw_stable_label(visualizer, layout, y + 14, stable_label, chord_text);
	if (draw_note_count) {
		char note_count[12] = {};
		std::snprintf(note_count, sizeof(note_count), "%d", note_grid_active_count(notes));
		draw_text(visualizer, layout.count_x, y + 16, note_count, 2, count_text);
	}

	for (int visible_row = 0; visible_row < row_count; ++visible_row) {
		const int row = first_row + visible_row;
		const int base_midi = 24 + row * kOctavesPerRow * 12;
		const int row_y = y + header_h + visible_row * (row_h + row_gap);
		char range_label[8] = {};
		std::snprintf(range_label, sizeof(range_label), "C%d-B%d", row * 2 + 1, row * 2 + 2);
		draw_text(visualizer, layout.note_x - 48, row_y + 10, range_label, 1, label_text);

		for (int i = 0; i < kWhiteKeysPerRow; ++i) {
			const int midi = base_midi + kWhiteOffsets[i];
			const float raw_level = piano_key_level(notes, midi);
			const float level = display_highlight_level(raw_level);
			const int x = layout.note_x + i * white_w;
			const int pitch_class = ((midi % 12) + 12) % 12;
			const Color note_color = pitch_class_color(pitch_class);
			Color fill = blend_color(white_key, note_color, level);
			if (raw_level > 0.0f)
				fill = blend_color(fill, Color{255, 255, 255, 255}, level * 0.26f);
			fill_rect(visualizer, x, row_y, white_w - 1, white_h, fill);
			fill_rect(visualizer, x, row_y, white_w - 1, 1, border);
			fill_rect(visualizer, x, row_y + white_h - 1, white_w - 1, 1, border);
			fill_rect(visualizer, x, row_y, 1, white_h, border);
			fill_rect(visualizer, x + white_w - 2, row_y, 1, white_h, border);
			if (raw_level > 0.0f) {
				char degree[4] = {};
				write_scale_degree(degree, sizeof(degree), degree_root_pitch_class, pitch_class);
				draw_centered_text(visualizer, x, row_y + 8, white_w - 1, white_h - 8, degree, 1,
						   active_text);
			}
		}

		for (std::size_t i = 0; i < sizeof(kBlackOffsets) / sizeof(kBlackOffsets[0]); ++i) {
			const int midi = base_midi + kBlackOffsets[i];
			const float raw_level = piano_key_level(notes, midi);
			const float level = display_highlight_level(raw_level);
			const int x = layout.note_x + (kBlackAfterWhite[i] + 1) * white_w - black_w / 2;
			const int pitch_class = ((midi % 12) + 12) % 12;
			const Color note_color = pitch_class_color(pitch_class);
			Color fill = blend_color(black_key, note_color, level);
			if (raw_level > 0.0f)
				fill = blend_color(fill, Color{255, 255, 255, 255}, level * 0.18f);
			fill_rect(visualizer, x, row_y, black_w, black_h, fill);
			fill_rect(visualizer, x, row_y, black_w, 1, border);
			fill_rect(visualizer, x, row_y + black_h - 1, black_w, 1, border);
			fill_rect(visualizer, x, row_y, 1, black_h, border);
			fill_rect(visualizer, x + black_w - 1, row_y, 1, black_h, border);
			if (raw_level > 0.0f) {
				char degree[4] = {};
				write_scale_degree(degree, sizeof(degree), degree_root_pitch_class, pitch_class);
				draw_centered_text(visualizer, x, row_y + 1, black_w, black_h, degree, 1,
						   Color{248, 250, 252, 255});
			}
		}
	}

	return y + header_h + row_count * row_h + (row_count - 1) * row_gap + 10;
}

int draw_guitar_fretboard(VisualizerRenderer *visualizer, const VisualLayout &layout, int y, const NoteGrid &notes,
			  const InstrumentState &chord, const char *stable_label, int degree_root_pitch_class,
			  bool draw_summary_columns = true, bool draw_note_count = true)
{
	static constexpr int kStringCount = 6;
	static constexpr int kFretCount = 16;
	static constexpr int kOpenMidis[kStringCount] = {64, 59, 55, 50, 45, 40};

	const int row_pitch = 14;
	const int cell_h = 13;
	const int header_h = 15;
	const int max_board_w = std::max(288, layout.note_w);
	const int max_fret_w = draw_summary_columns ? 38 : 96;
	const int fret_w = std::clamp(max_board_w / kFretCount, 18, max_fret_w);
	const int row_y = y + header_h;
	const Color dim = kLabelColor;
	const Color fret_bg{24, 30, 38, 210};
	const Color border{58, 68, 82, 220};
	const Color nut{148, 163, 184, 230};
	const Color text = kLabelColor;
	const Color chord_text = kWhiteTextColor;
	const Color count_text = kValueTextColor;
	const Color active_text{10, 15, 22, 255};
	const char *chord_label = chord.label[0] ? chord.label : "--";
	if (degree_root_pitch_class < 0)
		degree_root_pitch_class = pitch_class_from_note_label(chord_label);

	draw_text(visualizer, layout.label_x, y + 24, "GUITAR", 2, dim);
	for (int fret = 0; fret < kFretCount; ++fret) {
		char fret_label[4] = {};
		std::snprintf(fret_label, sizeof(fret_label), "%d", fret);
		const int label_w = static_cast<int>(std::strlen(fret_label)) * 6;
		draw_text(visualizer, layout.note_x + fret * fret_w + std::max(1, (fret_w - label_w) / 2), y,
			  fret_label, 1, text);
	}
	if (draw_summary_columns) {
		draw_chord_text(visualizer, layout.chord_x, y + 16, chord_label, 2, chord_text);
		draw_stable_label(visualizer, layout, y + 14, stable_label, chord_text);
	}
	if (draw_note_count) {
		char note_count[12] = {};
		std::snprintf(note_count, sizeof(note_count), "%d", note_grid_active_count(notes));
		draw_text(visualizer, layout.count_x, y + 16, note_count, 2, count_text);
	}

	for (int string = 0; string < kStringCount; ++string) {
		const int cell_y = row_y + string * row_pitch;
		char string_label[8] = {};
		write_note_name_with_octave(string_label, sizeof(string_label), kOpenMidis[string]);
		draw_text(visualizer, layout.note_x - 32, cell_y + 2, string_label, 1, text);
		for (int fret = 0; fret < kFretCount; ++fret) {
			const int cell_x = layout.note_x + fret * fret_w;
			const int midi = kOpenMidis[string] + fret;
			const int pitch_class = ((midi % 12) + 12) % 12;
			const float raw_level = guitar_note_grid_midi_level(notes, midi);
			const float level = display_highlight_level(raw_level);
			fill_rect(visualizer, cell_x, cell_y, fret_w - 1, cell_h, fret_bg);
			if (raw_level > 0.0f) {
				const Color note_color = pitch_class == degree_root_pitch_class ? Color{255, 59, 48, 255} :
										    pitch_class_color(pitch_class);
				Color marker = blend_color(fret_bg, note_color, level);
				marker = blend_color(marker, Color{255, 255, 255, 255}, level * 0.26f);
				fill_rect(visualizer, cell_x + 2, cell_y + 2, fret_w - 5, cell_h - 4, marker);
				char note_label[8] = {};
				write_note_name_with_octave(note_label, sizeof(note_label), midi);
				if (text_width(note_label, 1) > fret_w - 3)
					write_scale_degree(note_label, sizeof(note_label), degree_root_pitch_class,
							   pitch_class);
				draw_centered_text(visualizer, cell_x, cell_y, fret_w - 1, cell_h, note_label, 1,
						   active_text);
			}
			fill_rect(visualizer, cell_x, cell_y, fret_w - 1, 1, border);
			fill_rect(visualizer, cell_x, cell_y + cell_h - 1, fret_w - 1, 1, border);
			fill_rect(visualizer, cell_x, cell_y, 1, cell_h, fret == 1 ? nut : border);
			fill_rect(visualizer, cell_x + fret_w - 2, cell_y, 1, cell_h, border);
		}
	}

	return row_y + kStringCount * row_pitch + 6;
}

void draw_visualizer_header(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot, float snapshot_age,
			    const char *mode_label, int y_offset = 0)
{
	char title[128];
	if (mode_label && mode_label[0]) {
		std::snprintf(title, sizeof(title), "MUSIC ANALYZER  %s  %s", mode_label,
			      snapshot.source[0] ? snapshot.source : "WAITING");
	} else {
		std::snprintf(title, sizeof(title), "MUSIC ANALYZER  %s",
			      snapshot.source[0] ? snapshot.source : "WAITING");
	}
	draw_text(visualizer, 28, std::max(0, 24 + y_offset), title, 3, Color{246, 248, 251, 255});

	draw_status_line(visualizer, snapshot, snapshot_age, y_offset);
}

void draw_drum_row(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot, int label_y, int chart_y,
		   int min_drum_w = 106, int max_drum_w = 150, uint32_t label_scale = 2)
{
	draw_text(visualizer, 28, label_y, "DRUMS", 3, kLabelColor);
	const int drum_start_x = 150;
	const int drum_gap = 6;
	const int drum_right_margin = 22;
	const int available_w = static_cast<int>(visualizer->width) - drum_start_x - drum_right_margin -
				static_cast<int>(snapshot.drums.size() - 1) * drum_gap;
	const int raw_drum_w = std::max(1, available_w / static_cast<int>(snapshot.drums.size()));
	const bool tight = raw_drum_w < min_drum_w;
	const int drum_w = tight ? raw_drum_w : std::clamp(raw_drum_w, min_drum_w, max_drum_w);
	const uint32_t effective_label_scale = tight ? 1 : label_scale;
	int tag_x = drum_start_x;
	for (std::size_t i = 0; i < snapshot.drums.size(); ++i) {
		draw_drum_chart(visualizer, tag_x, chart_y, drum_w, snapshot.drums[i],
				visualizer->drum_history[i], effective_label_scale);
		tag_x += drum_w + drum_gap;
	}
}

void draw_note_column_headers(VisualizerRenderer *visualizer, const VisualLayout &layout, int y,
			      bool draw_chord_columns = true, bool draw_note_count = true)
{
	static constexpr const char *kNoteNames[12] = {"C", "C#", "D", "D#", "E", "F",
						       "F#", "G", "G#", "A", "A#", "B"};
	const int cell_w = std::max(30, layout.note_w / 12);
	for (int i = 0; i < 12; ++i)
		draw_text(visualizer, layout.note_x + i * cell_w + 7, y, kNoteNames[i], 2, kLabelColor);
	if (draw_chord_columns) {
		draw_text(visualizer, layout.chord_x, y, "CHORD", 2, kLabelColor);
		draw_text(visualizer, layout.stable_x, y, "SUSTAIN", 2, kLabelColor);
	}
	if (draw_note_count)
		draw_text(visualizer, layout.count_x, y, "NOTES", 2, kLabelColor);
}

void draw_root_and_bpm(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot, int root_y,
		       int bpm_y_override = -1)
{
	draw_root_candidates(visualizer, 28, root_y, snapshot.root_candidates, snapshot.root.label);

	char bpm_value[16] = {};
	char bpm_confidence[16] = {};
	if (snapshot.estimated_bpm > 0.0f && snapshot.bpm_confidence > 0.05f) {
		std::snprintf(bpm_value, sizeof(bpm_value), "%.0f", snapshot.estimated_bpm);
		std::snprintf(bpm_confidence, sizeof(bpm_confidence), "%.0f%%",
			      snapshot.bpm_confidence * 100.0f);
	} else {
		std::snprintf(bpm_value, sizeof(bpm_value), "--");
		bpm_confidence[0] = '\0';
	}
	const int bpm_y = bpm_y_override >= 0 ? bpm_y_override : std::max(0, static_cast<int>(visualizer->height) - 18);
	const int total_width = text_width("BPM ", 2) + text_width(bpm_value, 2) +
				(bpm_confidence[0] ? text_width(" ", 2) + text_width(bpm_confidence, 2) : 0);
	int bpm_x = std::max(28, static_cast<int>(visualizer->width) - 28 - total_width);
	if (visualizer->external_control.visible) {
		constexpr std::array<const char *, 12> kRootNames = {
			"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
		};
		constexpr std::array<const char *, 4> kDeviceNames = {"LJ", "FZ", "APC", "MV"};
		const auto state_color = [](DeviceConnectionState state) {
			switch (state) {
			case DeviceConnectionState::Connected:
				return Color{52, 211, 153, 255};
			case DeviceConnectionState::Searching:
				return Color{250, 204, 21, 255};
			case DeviceConnectionState::Connecting:
				return Color{251, 146, 60, 255};
			case DeviceConnectionState::Error:
				return Color{248, 113, 113, 255};
			case DeviceConnectionState::Disabled:
				return Color{100, 116, 139, 255};
			}
			return Color{100, 116, 139, 255};
		};
		const auto state_suffix = [](DeviceConnectionState state) {
			switch (state) {
			case DeviceConnectionState::Connected:
				return "+";
			case DeviceConnectionState::Searching:
				return "?";
			case DeviceConnectionState::Connecting:
				return "~";
			case DeviceConnectionState::Error:
				return "!";
			case DeviceConnectionState::Disabled:
				return "-";
			}
			return "-";
		};

		char mode_root[24] = {};
		const int root = std::max(0, std::min(11, visualizer->external_control.effective_root));
		std::snprintf(mode_root, sizeof(mode_root), "%s %s%s",
			      visualizer->external_control.mode == RootControlMode::Auto ? "AUTO" : "MAN",
			      kRootNames[static_cast<std::size_t>(root)],
			      visualizer->external_control.autoconnect ? "" : " OFF");
		int control_width = text_width(mode_root, 2);
		for (std::size_t i = 0; i < kDeviceNames.size(); ++i)
			control_width += text_width(" ", 2) + text_width(kDeviceNames[i], 2) + text_width("+", 2);
		int control_x = std::max(28, bpm_x - 14 - control_width);
		draw_text(visualizer, control_x, bpm_y, mode_root, 2, kWhiteTextColor);
		control_x += text_width(mode_root, 2);
		for (std::size_t i = 0; i < kDeviceNames.size(); ++i) {
			control_x += text_width(" ", 2);
			const DeviceConnectionState state = visualizer->external_control.devices[i];
			draw_text(visualizer, control_x, bpm_y, kDeviceNames[i], 2, state_color(state));
			control_x += text_width(kDeviceNames[i], 2);
			draw_text(visualizer, control_x, bpm_y, state_suffix(state), 2, state_color(state));
			control_x += text_width("+", 2);
		}
	}
	draw_text(visualizer, bpm_x, bpm_y, "BPM", 2, kLabelColor);
	bpm_x += text_width("BPM ", 2);
	draw_text(visualizer, bpm_x, bpm_y, bpm_value, 2, kWhiteTextColor);
	bpm_x += text_width(bpm_value, 2);
	if (bpm_confidence[0]) {
		bpm_x += text_width(" ", 2);
		draw_text(visualizer, bpm_x, bpm_y, bpm_confidence, 2, kLabelColor);
	}
}

void draw_waiting_status(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot, float snapshot_age, int x, int y)
{
	if (snapshot.sequence == 0)
		draw_text(visualizer, x, y, "ADD MUSIC ANALYZER FILTER TO AN AUDIO SOURCE", 2,
			  Color{248, 250, 252, 255});
	else if (!snapshot.audio_seen)
		draw_text(visualizer, x, y, "FILTER READY - WAITING FOR AUDIO", 2, Color{248, 250, 252, 255});
	else if (snapshot_age > 1.5f)
		draw_muted_mic_indicator(visualizer);
}

void render_complete_pixels(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot, float snapshot_age)
{
	constexpr int y_shift = kCompleteContentShiftY;
	draw_visualizer_header(visualizer, snapshot, snapshot_age, nullptr, y_shift);
	draw_drum_row(visualizer, snapshot, 96 + y_shift, 88 + y_shift);

	const VisualLayout layout = visual_layout(visualizer);
	update_stable_label(visualizer, StableBass, snapshot, snapshot.bass_notes, nullptr, true);
	update_stable_label(visualizer, StableVocal, snapshot, snapshot.vocal_notes, nullptr, true);
	update_stable_label(visualizer, StableOther, snapshot, snapshot.other_notes, &snapshot.other_chord, false);
	update_stable_label(visualizer, StableKeyboard, snapshot, snapshot.keyboard_notes, &snapshot.keyboard_chord, false);
	update_stable_label(visualizer, StableGuitar, snapshot, snapshot.guitar_notes, &snapshot.guitar_chord, false);
	draw_note_column_headers(visualizer, layout, 144 + y_shift);
	int row_y = 164 + y_shift;
	row_y = draw_instrument_rows(visualizer, layout, row_y, "BASS", snapshot.bass_notes, nullptr,
				     visualizer->stable_labels[StableBass].label,
				     Color{255, 59, 48, 245}, 1);
	row_y += 6;
	row_y = draw_instrument_rows(visualizer, layout, row_y, "VOCAL", snapshot.vocal_notes, nullptr,
				     visualizer->stable_labels[StableVocal].label,
				     Color{10, 132, 255, 245}, kMatrixRowCount);
	row_y += 6;
	row_y = draw_instrument_rows(visualizer, layout, row_y, "OTHERS", snapshot.other_notes, &snapshot.other_chord,
				     visualizer->stable_labels[StableOther].label,
				     Color{191, 90, 242, 245}, kMatrixRowCount);
	const int degree_root_pitch_class = pitch_class_from_note_label(snapshot.root.label);
	row_y = draw_piano_keyboard(visualizer, layout, row_y + 4, snapshot.keyboard_notes, snapshot.keyboard_chord,
				    visualizer->stable_labels[StableKeyboard].label, degree_root_pitch_class);
	row_y = draw_guitar_fretboard(visualizer, layout, row_y + 4, snapshot.guitar_notes, snapshot.guitar_chord,
				      visualizer->stable_labels[StableGuitar].label, degree_root_pitch_class);

	const int root_y = std::min(row_y + 6, std::max(0, static_cast<int>(visualizer->height) - 14 + y_shift));
	draw_root_and_bpm(visualizer, snapshot, root_y);

	draw_waiting_status(visualizer, snapshot, snapshot_age, 230, 145 + y_shift);
}

void render_bass_guitar_pixels(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot, float snapshot_age)
{
	constexpr int y_shift = kBassGuitarContentShiftY;
	draw_visualizer_header(visualizer, snapshot, snapshot_age, nullptr, y_shift);
	draw_drum_row(visualizer, snapshot, 104 + y_shift, 98 + y_shift, 106, 150, 2);

	const VisualLayout layout = bass_guitar_visual_layout(visualizer);
	update_stable_label(visualizer, StableBass, snapshot, snapshot.bass_notes, nullptr, true);
	update_stable_label(visualizer, StableKeyboard, snapshot, snapshot.keyboard_notes, &snapshot.keyboard_chord, false);
	update_stable_label(visualizer, StableGuitar, snapshot, snapshot.guitar_notes, &snapshot.guitar_chord, false);
	draw_note_column_headers(visualizer, layout, 158 + y_shift, true, false);

	int row_y = 178 + y_shift;
	row_y = draw_instrument_rows(visualizer, layout, row_y, "BASS", snapshot.bass_notes, nullptr,
				     visualizer->stable_labels[StableBass].label, Color{255, 59, 48, 245}, 1, false);
	const int degree_root_pitch_class = pitch_class_from_note_label(snapshot.root.label);
	row_y = draw_piano_keyboard(visualizer, layout, row_y - 8, snapshot.keyboard_notes, snapshot.keyboard_chord,
				    visualizer->stable_labels[StableKeyboard].label, degree_root_pitch_class,
				    kHalfMusicKeyboardFirstRow, kHalfMusicKeyboardRowCount, false);
	row_y = draw_guitar_fretboard(visualizer, layout, kHalfMusicGuitarY + y_shift, snapshot.guitar_notes,
				      snapshot.guitar_chord,
				      visualizer->stable_labels[StableGuitar].label, degree_root_pitch_class, true, false);

	const int root_y = std::max(row_y + 6, static_cast<int>(visualizer->height) - 42 + y_shift);
	draw_root_and_bpm(visualizer, snapshot, root_y, root_y);
}

void render_pixels(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot, float snapshot_age)
{
	std::fill(visualizer->pixels.begin(), visualizer->pixels.end(), 0);

	fill_rect(visualizer, 0, 0, visualizer->width, visualizer->height, Color{12, 16, 22, 205});

	if (visualizer->layout_mode == VisualizerLayoutMode::BassGuitar)
		render_bass_guitar_pixels(visualizer, snapshot, snapshot_age);
	else
		render_complete_pixels(visualizer, snapshot, snapshot_age);
}

bool advance_drum_history(VisualizerRenderer *visualizer, float seconds)
{
	bool has_history = false;
	for (auto &history : visualizer->drum_history) {
		for (DrumBar &bar : history)
			bar.age += seconds;
		history.erase(std::remove_if(history.begin(), history.end(),
					     [](const DrumBar &bar) { return bar.age > 1.0f; }),
			      history.end());
		has_history = has_history || !history.empty();
	}
	return has_history;
}

bool append_drum_hits(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot)
{
	if (snapshot.sequence == 0 || snapshot.sequence == visualizer->drum_history_sequence)
		return false;

	visualizer->drum_history_sequence = snapshot.sequence;
	bool appended = false;
	for (std::size_t i = 0; i < snapshot.drums.size(); ++i) {
		const DrumState &drum = snapshot.drums[i];
		if (drum.level <= 0.30f)
			continue;

		auto &history = visualizer->drum_history[i];
		history.push_back(DrumBar{0.0f, std::clamp(drum.level, 0.0f, 1.0f)});
		if (history.size() > 64)
			history.erase(history.begin());
		appended = true;
	}
	return appended;
}

} // namespace

void format_visualizer_status_line(char *output, std::size_t output_size, const AnalysisSnapshot &snapshot,
				   float snapshot_age)
{
	if (!output || output_size == 0)
		return;

	char low[8] = {};
	char mid[8] = {};
	char high[8] = {};
	format_band_percentage(low, sizeof(low), snapshot.low_energy);
	format_band_percentage(mid, sizeof(mid), snapshot.mid_energy);
	format_band_percentage(high, sizeof(high), snapshot.high_energy);
	int written = std::snprintf(output, output_size,
				    "LOW %s MID %s HIGH %s AGE %.1fs DROP %llu",
				    low, mid, high,
				    std::clamp(snapshot_age, 0.0f, 99.9f),
				    static_cast<unsigned long long>(snapshot.dropped_windows));
	if (written < 0)
		return;
	std::size_t used = std::min<std::size_t>(static_cast<std::size_t>(written), output_size - 1);
	if (snapshot.battery_percent >= 0.0f && used + 1 < output_size) {
		written = std::snprintf(output + used, output_size - used,
					snapshot.battery_charging ? " BAT+ %.0f" : " BAT %.0f",
					std::clamp(snapshot.battery_percent, 0.0f, 100.0f));
		if (written > 0)
			used = std::min<std::size_t>(used + static_cast<std::size_t>(written), output_size - 1);
	}
	if (snapshot.ram_mb >= 0.0f && used + 1 < output_size) {
		written = std::snprintf(output + used, output_size - used, " RAM %.0fMB",
					std::clamp(snapshot.ram_mb, 0.0f, 999.0f));
		if (written > 0)
			used = std::min<std::size_t>(used + static_cast<std::size_t>(written), output_size - 1);
	}
	if (snapshot.cpu_percent >= 0.0f && used + 1 < output_size) {
		written = std::snprintf(output + used, output_size - used, " CPU %.0f",
					std::max(snapshot.cpu_percent, 0.0f));
		if (written > 0)
			used = std::min<std::size_t>(used + static_cast<std::size_t>(written), output_size - 1);
	}
	if (used + 1 < output_size)
		std::snprintf(output + used, output_size - used, " RMS %.2f",
			      std::clamp(snapshot.rms, 0.0f, 9.99f));
}

bool snapshot_resets_visualizer_age(const AnalysisSnapshot &snapshot)
{
	return snapshot.audio_seen && snapshot.rms >= kVisualizerAudibleRms;
}

void resize_visualizer(VisualizerRenderer *visualizer, uint32_t width, uint32_t height)
{
	if (!visualizer)
		return;

	visualizer->width = std::max<uint32_t>(1, width);
	visualizer->height = std::max<uint32_t>(1, height);
	visualizer->pixels.resize(static_cast<std::size_t>(visualizer->width) * visualizer->height * 4);
	for (auto &history : visualizer->drum_history)
		history.reserve(64);
}

void render_visualizer(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot, float snapshot_age)
{
	if (!visualizer)
		return;
	if (visualizer->pixels.size() != static_cast<std::size_t>(visualizer->width) * visualizer->height * 4)
		resize_visualizer(visualizer, visualizer->width, visualizer->height);
	render_pixels(visualizer, snapshot, snapshot_age);
}

bool advance_visualizer_drum_history(VisualizerRenderer *visualizer, float seconds)
{
	return visualizer ? advance_drum_history(visualizer, seconds) : false;
}

bool append_visualizer_drum_hits(VisualizerRenderer *visualizer, const AnalysisSnapshot &snapshot)
{
	return visualizer ? append_drum_hits(visualizer, snapshot) : false;
}

} // namespace mao
