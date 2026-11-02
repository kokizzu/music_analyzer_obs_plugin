#include "piano_attack_continuity.hpp"
#include <cassert>

int main()
{
    mao::joint::AttackDisplayContinuity cache;
    mao::NoteGrid display{},raw{};
    std::array<mao::NoteTrackingState,mao::kNoteProbeCount> tracking{};
    std::array<bool,88> seed{},continuing{};
    constexpr int i=60-21;
    auto &cell=raw.rows[0][0];cell.active=true;cell.midi=60;cell.level=.1f;cell.visual_level=.1f;
    const auto original_cell=cell;
    tracking[i].consecutive_hits=1;
    continuing[i]=true;
    assert(cache.apply(display,raw,tracking,seed,continuing)==0);
    seed[i]=true;
    assert(cache.apply(display,raw,tracking,seed,continuing)==1);
    seed[i]=false;raw={};tracking={};display={};
    assert(cache.apply(display,raw,tracking,seed,continuing)==1);
    display={};
    assert(cache.apply(display,raw,tracking,seed,continuing)==1);
    display={};
    assert(cache.apply(display,raw,tracking,seed,continuing)==0);
    // Support loss retires a seed immediately; later support cannot resurrect it.
    raw.rows[0][0]=original_cell;
    tracking[i].consecutive_hits=1;seed[i]=true;
    assert(cache.apply(display,raw,tracking,seed,continuing)==1);
    raw={};tracking={};seed[i]=false;continuing[i]=false;display={};
    assert(cache.apply(display,raw,tracking,seed,continuing)==0);
    continuing[i]=true;
    assert(cache.apply(display,raw,tracking,seed,continuing)==0);
    // Reset/source handoff and occupied columns never retain an overlay.
    raw.rows[0][0]=original_cell;
    tracking[i].consecutive_hits=1;seed[i]=true;
    assert(cache.apply(display,raw,tracking,seed,continuing)==1);
    cache.reset();raw={};tracking={};seed[i]=false;display={};
    assert(cache.apply(display,raw,tracking,seed,continuing)==0);
    raw.rows[0][0].active=true;raw.rows[0][0].midi=60;raw.rows[0][0].level=.1f;raw.rows[0][0].visual_level=.1f;
    tracking[i].consecutive_hits=1;seed[i]=true;
    for (std::size_t r=0;r<display.rows.size();++r) {
        display.rows[r][0]=raw.rows[0][0];display.rows[r][0].midi=72+12*static_cast<int>(r);
    }
    assert(cache.apply(display,raw,tracking,seed,continuing)==0);
    for (std::size_t r=0;r<display.rows.size();++r)
        assert(display.rows[r][0].midi==72+12*static_cast<int>(r));
    display={};raw={};tracking={};seed[i]=false;
    assert(cache.apply(display,raw,tracking,seed,continuing)==0);
}
