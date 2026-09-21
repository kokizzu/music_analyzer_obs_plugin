#pragma once

namespace mao {

enum class HardwareWriteResult {
	Succeeded,
	Stale,
	Failed,
};

template <typename IsCurrent, typename Writer>
HardwareWriteResult hardware_write_if_current(IsCurrent is_current, Writer writer)
{
	if (!is_current())
		return HardwareWriteResult::Stale;
	return writer() ? HardwareWriteResult::Succeeded : HardwareWriteResult::Failed;
}

} // namespace mao
