#include "audacious_overlay.hpp"

#include <obs.h>

#include <cstring>

namespace mao {

void audacious_obs_register_source(::obs_source_info *info)
{
	if (info && info->id && std::strcmp(info->id, "music_analyzer_overlay") == 0)
		info->output_flags |= OBS_SOURCE_CUSTOM_DRAW;
	::obs_register_source(info);
}

} // namespace mao
