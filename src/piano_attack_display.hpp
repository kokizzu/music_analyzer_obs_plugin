#pragma once
#include "joint_grace_restore.hpp"

namespace mao::joint {
// Display-only recovery. Tracking remains const and occupied visible rows are
// never replaced. Call after analytical/chord/routing decisions are complete.
inline unsigned recover_first_hit_display(NoteGrid &display, const NoteGrid &raw,
    const std::array<NoteTrackingState,kNoteProbeCount> &tracking,
    const std::array<bool,88> &supported)
{
    unsigned recovered=0;
    for (std::size_t i=0;i<supported.size();++i) {
        const auto &state=tracking[i];
        if (!supported[i] || state.confirmed || state.consecutive_hits!=1 || state.consecutive_misses!=0)
            continue;
        recovered+=restore_erased_note(display,raw,static_cast<int>(i)+21);
    }
    return recovered;
}
}
