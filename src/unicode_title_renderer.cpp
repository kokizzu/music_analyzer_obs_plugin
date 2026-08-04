#include "unicode_title_renderer.hpp"
#include "visualizer_renderer.hpp"

#include <algorithm>
#include <cstdint>
#include <cstring>
#include <mutex>

#if defined(__linux__)
#include <dlfcn.h>
#endif

namespace mao {
namespace {

#if defined(__linux__)

struct _cairo;
struct _cairo_surface;
struct _PangoLayout;
struct _PangoFontDescription;
using cairo_t = _cairo;
using cairo_surface_t = _cairo_surface;
using PangoLayout = _PangoLayout;
using PangoFontDescription = _PangoFontDescription;

constexpr int kCairoFormatArgb32 = 0;
constexpr int kCairoOperatorSource = 1;
constexpr int kCairoOperatorOver = 2;
constexpr int kPangoScale = 1024;

struct UnicodeTextApi {
	void *cairo_library = nullptr;
	void *pango_library = nullptr;
	void *pangocairo_library = nullptr;
	void *gobject_library = nullptr;

	cairo_surface_t *(*cairo_image_surface_create)(int, int, int) = nullptr;
	int (*cairo_surface_status)(cairo_surface_t *) = nullptr;
	cairo_t *(*cairo_create)(cairo_surface_t *) = nullptr;
	int (*cairo_status)(cairo_t *) = nullptr;
	void (*cairo_set_operator)(cairo_t *, int) = nullptr;
	void (*cairo_set_source_rgba)(cairo_t *, double, double, double, double) = nullptr;
	void (*cairo_paint)(cairo_t *) = nullptr;
	void (*cairo_move_to)(cairo_t *, double, double) = nullptr;
	void (*cairo_destroy)(cairo_t *) = nullptr;
	void (*cairo_surface_flush)(cairo_surface_t *) = nullptr;
	unsigned char *(*cairo_image_surface_get_data)(cairo_surface_t *) = nullptr;
	int (*cairo_image_surface_get_stride)(cairo_surface_t *) = nullptr;
	void (*cairo_surface_destroy)(cairo_surface_t *) = nullptr;

	PangoLayout *(*pango_cairo_create_layout)(cairo_t *) = nullptr;
	void (*pango_cairo_show_layout)(cairo_t *, PangoLayout *) = nullptr;
	PangoFontDescription *(*pango_font_description_new)() = nullptr;
	void (*pango_font_description_set_family)(PangoFontDescription *, const char *) = nullptr;
	void (*pango_font_description_set_absolute_size)(PangoFontDescription *, double) = nullptr;
	void (*pango_font_description_free)(PangoFontDescription *) = nullptr;
	void (*pango_layout_set_font_description)(PangoLayout *, const PangoFontDescription *) = nullptr;
	void (*pango_layout_set_text)(PangoLayout *, const char *, int) = nullptr;
	void (*pango_layout_set_single_paragraph_mode)(PangoLayout *, int) = nullptr;
	void (*pango_layout_get_pixel_size)(PangoLayout *, int *, int *) = nullptr;
	void (*g_object_unref)(void *) = nullptr;
	bool available = false;
};

void *open_runtime_library(const char *versioned_name, const char *fallback_name)
{
	void *handle = dlopen(versioned_name, RTLD_LAZY | RTLD_LOCAL);
	if (!handle && fallback_name)
		handle = dlopen(fallback_name, RTLD_LAZY | RTLD_LOCAL);
	return handle;
}

template <typename T>
bool load_runtime_symbol(void *library, const char *name, T &target)
{
	target = reinterpret_cast<T>(dlsym(library, name));
	return target != nullptr;
}

UnicodeTextApi &unicode_text_api()
{
	static UnicodeTextApi api;
	static std::once_flag once;
	std::call_once(once, [&]() {
		api.cairo_library = open_runtime_library("libcairo.so.2", "libcairo.so");
		api.pango_library = open_runtime_library("libpango-1.0.so.0", "libpango-1.0.so");
		api.pangocairo_library =
			open_runtime_library("libpangocairo-1.0.so.0", "libpangocairo-1.0.so");
		api.gobject_library = open_runtime_library("libgobject-2.0.so.0", "libgobject-2.0.so");
		if (!api.cairo_library || !api.pango_library || !api.pangocairo_library || !api.gobject_library)
			return;

		bool loaded = true;
		loaded &= load_runtime_symbol(api.cairo_library, "cairo_image_surface_create",
					      api.cairo_image_surface_create);
		loaded &= load_runtime_symbol(api.cairo_library, "cairo_surface_status", api.cairo_surface_status);
		loaded &= load_runtime_symbol(api.cairo_library, "cairo_create", api.cairo_create);
		loaded &= load_runtime_symbol(api.cairo_library, "cairo_status", api.cairo_status);
		loaded &= load_runtime_symbol(api.cairo_library, "cairo_set_operator", api.cairo_set_operator);
		loaded &= load_runtime_symbol(api.cairo_library, "cairo_set_source_rgba", api.cairo_set_source_rgba);
		loaded &= load_runtime_symbol(api.cairo_library, "cairo_paint", api.cairo_paint);
		loaded &= load_runtime_symbol(api.cairo_library, "cairo_move_to", api.cairo_move_to);
		loaded &= load_runtime_symbol(api.cairo_library, "cairo_destroy", api.cairo_destroy);
		loaded &= load_runtime_symbol(api.cairo_library, "cairo_surface_flush", api.cairo_surface_flush);
		loaded &= load_runtime_symbol(api.cairo_library, "cairo_image_surface_get_data",
					      api.cairo_image_surface_get_data);
		loaded &= load_runtime_symbol(api.cairo_library, "cairo_image_surface_get_stride",
					      api.cairo_image_surface_get_stride);
		loaded &= load_runtime_symbol(api.cairo_library, "cairo_surface_destroy", api.cairo_surface_destroy);

		loaded &= load_runtime_symbol(api.pangocairo_library, "pango_cairo_create_layout",
					      api.pango_cairo_create_layout);
		loaded &= load_runtime_symbol(api.pangocairo_library, "pango_cairo_show_layout",
					      api.pango_cairo_show_layout);
		loaded &= load_runtime_symbol(api.pango_library, "pango_font_description_new",
					      api.pango_font_description_new);
		loaded &= load_runtime_symbol(api.pango_library, "pango_font_description_set_family",
					      api.pango_font_description_set_family);
		loaded &= load_runtime_symbol(api.pango_library, "pango_font_description_set_absolute_size",
					      api.pango_font_description_set_absolute_size);
		loaded &= load_runtime_symbol(api.pango_library, "pango_font_description_free",
					      api.pango_font_description_free);
		loaded &= load_runtime_symbol(api.pango_library, "pango_layout_set_font_description",
					      api.pango_layout_set_font_description);
		loaded &= load_runtime_symbol(api.pango_library, "pango_layout_set_text", api.pango_layout_set_text);
		loaded &= load_runtime_symbol(api.pango_library, "pango_layout_set_single_paragraph_mode",
					      api.pango_layout_set_single_paragraph_mode);
		loaded &= load_runtime_symbol(api.pango_library, "pango_layout_get_pixel_size",
					      api.pango_layout_get_pixel_size);
		loaded &= load_runtime_symbol(api.gobject_library, "g_object_unref", api.g_object_unref);
		api.available = loaded;
	});
	return api;
}

#endif

} // namespace

bool render_unicode_header_title(VisualizerRenderer *visualizer, const std::string &text, int x, int y,
				 int max_width, int target_height)
{
#if defined(__linux__)
	UnicodeTextApi &api = unicode_text_api();
	if (!api.available || !visualizer || text.empty() || max_width <= 0 || target_height <= 0 ||
	    visualizer->pixels.empty())
		return false;

	cairo_surface_t *surface = api.cairo_image_surface_create(kCairoFormatArgb32, max_width, target_height);
	if (!surface || api.cairo_surface_status(surface) != 0)
		return false;

	cairo_t *context = api.cairo_create(surface);
	if (!context || api.cairo_status(context) != 0) {
		if (context)
			api.cairo_destroy(context);
		api.cairo_surface_destroy(surface);
		return false;
	}

	api.cairo_set_operator(context, kCairoOperatorSource);
	api.cairo_set_source_rgba(context, 0.0, 0.0, 0.0, 0.0);
	api.cairo_paint(context);
	api.cairo_set_operator(context, kCairoOperatorOver);

	PangoLayout *layout = api.pango_cairo_create_layout(context);
	PangoFontDescription *font = api.pango_font_description_new();
	if (!layout || !font) {
		if (font)
			api.pango_font_description_free(font);
		if (layout)
			api.g_object_unref(layout);
		api.cairo_destroy(context);
		api.cairo_surface_destroy(surface);
		return false;
	}

	constexpr double kInitialFontPixels = 24.0;
	constexpr double kMinimumFontPixels = 14.0;
	api.pango_font_description_set_family(font, "Sans");
	api.pango_font_description_set_absolute_size(font, kInitialFontPixels * kPangoScale);
	api.pango_layout_set_font_description(layout, font);
	api.pango_layout_set_text(layout, text.c_str(), -1);
	api.pango_layout_set_single_paragraph_mode(layout, 1);

	int text_width = 0;
	int text_height = 0;
	api.pango_layout_get_pixel_size(layout, &text_width, &text_height);
	if (text_width > 0 && text_height > 0 && (text_width > max_width || text_height > target_height)) {
		const double width_ratio = static_cast<double>(max_width) / static_cast<double>(text_width);
		const double height_ratio = static_cast<double>(target_height) / static_cast<double>(text_height);
		const double adjusted_size =
			std::max(kMinimumFontPixels, kInitialFontPixels * std::min(width_ratio, height_ratio));
		api.pango_font_description_set_absolute_size(font, adjusted_size * kPangoScale);
		api.pango_layout_set_font_description(layout, font);
		api.pango_layout_get_pixel_size(layout, &text_width, &text_height);
	}

	const int text_y = std::max(0, (target_height - text_height) / 2);
	api.cairo_move_to(context, 0.0, static_cast<double>(text_y));
	api.cairo_set_source_rgba(context, 246.0 / 255.0, 248.0 / 255.0, 251.0 / 255.0, 1.0);
	api.pango_cairo_show_layout(context, layout);
	api.cairo_surface_flush(surface);

	unsigned char *source = api.cairo_image_surface_get_data(surface);
	const int stride = api.cairo_image_surface_get_stride(surface);
	bool painted = false;
	if (source && stride > 0) {
		for (int source_y = 0; source_y < target_height; ++source_y) {
			const int destination_y = y + source_y;
			if (destination_y < 0 || destination_y >= static_cast<int>(visualizer->height))
				continue;
			const unsigned char *row = source + source_y * stride;
			for (int source_x = 0; source_x < max_width; ++source_x) {
				const int destination_x = x + source_x;
				if (destination_x < 0 || destination_x >= static_cast<int>(visualizer->width))
					continue;

				uint32_t argb = 0;
				std::memcpy(&argb, row + source_x * 4, sizeof(argb));
				const uint8_t alpha = static_cast<uint8_t>((argb >> 24) & 0xffu);
				if (alpha == 0)
					continue;
				const uint8_t red = static_cast<uint8_t>((argb >> 16) & 0xffu);
				const uint8_t green = static_cast<uint8_t>((argb >> 8) & 0xffu);
				const uint8_t blue = static_cast<uint8_t>(argb & 0xffu);
				const uint16_t inverse_alpha = static_cast<uint16_t>(255 - alpha);
				const std::size_t destination =
					(static_cast<std::size_t>(destination_y) * visualizer->width +
					 static_cast<std::size_t>(destination_x)) *
					4;
				visualizer->pixels[destination + 0] = static_cast<uint8_t>(std::min(
					255, static_cast<int>(red) +
						     (static_cast<int>(visualizer->pixels[destination + 0]) * inverse_alpha +
						      127) /
							     255));
				visualizer->pixels[destination + 1] = static_cast<uint8_t>(std::min(
					255, static_cast<int>(green) +
						     (static_cast<int>(visualizer->pixels[destination + 1]) * inverse_alpha +
						      127) /
							     255));
				visualizer->pixels[destination + 2] = static_cast<uint8_t>(std::min(
					255, static_cast<int>(blue) +
						     (static_cast<int>(visualizer->pixels[destination + 2]) * inverse_alpha +
						      127) /
							     255));
				visualizer->pixels[destination + 3] = 255;
				painted = true;
			}
		}
	}

	api.pango_font_description_free(font);
	api.g_object_unref(layout);
	api.cairo_destroy(context);
	api.cairo_surface_destroy(surface);
	return painted;
#else
	(void)visualizer;
	(void)text;
	(void)x;
	(void)y;
	(void)max_width;
	(void)target_height;
	return false;
#endif
}

} // namespace mao
