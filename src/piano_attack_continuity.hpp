#pragma once
#include "joint_grace_restore.hpp"

namespace mao::joint {
// Caller supplies 50 ms hops and resets on source/format/drop/eligibility changes.
// Family/dominance apply to the attack only. Every continuation needs current
// joint-pitch and fresh neural support; no release envelope is synthesized.
class AttackDisplayContinuity {
    struct Seed { NoteCell cell{}; unsigned age=0; bool active=false; };
    std::array<Seed,88> seeds_{};
public:
    void reset() { seeds_={}; }
    unsigned apply(NoteGrid &display,const NoteGrid &raw,
        const std::array<NoteTrackingState,kNoteProbeCount> &tracking,
        const std::array<bool,88> &seed_support,const std::array<bool,88> &continuation_support)
    {
        unsigned recovered=0;
        for (std::size_t i=0;i<seeds_.size();++i) {
            auto &seed=seeds_[i];
            const int midi=static_cast<int>(i)+21;
            const auto pc=static_cast<std::size_t>(midi%12);
            bool visible=false;
            for (const auto &row:display.rows)
                visible|=row[pc].midi==midi && visible_level(row[pc])>0;
            if (visible) { seed={}; continue; }
            if (seed.active && (++seed.age>=3 || !continuation_support[i])) seed={};
            const auto &state=tracking[i];
            if (!seed.active && seed_support[i] && !state.confirmed && state.consecutive_hits==1 && state.consecutive_misses==0) {
                for (const auto &row:raw.rows)
                    if (row[pc].midi==midi && visible_level(row[pc])>0 &&
                        (!seed.active || visible_level(row[pc])>visible_level(seed.cell))) {
                        seed.cell=row[pc];seed.age=0;seed.active=true;
                    }
            }
            if (!seed.active) continue;
            NoteGrid source{};
            source.rows[0][pc]=seed.cell;
            if (restore_erased_note(display,source,midi)) ++recovered;
            else seed={};
        }
        return recovered;
    }
};
}
