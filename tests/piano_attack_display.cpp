#include "piano_attack_display.hpp"
#include <cassert>
#include <cstring>

static mao::NoteCell cell(int midi,float level)
{
    mao::NoteCell result{};
    result.active=true; result.midi=midi; result.level=level; result.visual_level=level;
    return result;
}

int main()
{
    std::array<mao::NoteTrackingState,mao::kNoteProbeCount> tracking{};
    std::array<bool,88> support{};
    mao::NoteGrid raw{},display{};
    constexpr int midi=60;
    constexpr auto index=midi-21;
    raw.rows[0][0]=cell(midi,.1f);
    tracking[index].consecutive_hits=1;
    auto original=tracking;
    assert(mao::joint::recover_first_hit_display(display,raw,tracking,support)==0);
    support[index]=true;
    assert(mao::joint::recover_first_hit_display(display,raw,tracking,support)==1);
    assert(display.rows[0][0].midi==midi && display.rows[0][0].level==.1f);
    assert(std::memcmp(tracking.data(),original.data(),sizeof(tracking))==0);
    assert(mao::joint::recover_first_hit_display(display,raw,tracking,support)==0);
    display={};
    for (std::size_t row=0;row<display.rows.size();++row)
        display.rows[row][0]=cell(72+12*static_cast<int>(row),.2f);
    const auto occupied=display;
    assert(mao::joint::recover_first_hit_display(display,raw,tracking,support)==0);
    for (std::size_t row=0;row<display.rows.size();++row)
        assert(display.rows[row][0].midi==occupied.rows[row][0].midi && display.rows[row][0].level==occupied.rows[row][0].level);
    display={};
    tracking[index].confirmed=true;
    assert(mao::joint::recover_first_hit_display(display,raw,tracking,support)==0);
    tracking[index].confirmed=false;tracking[index].consecutive_hits=2;
    assert(mao::joint::recover_first_hit_display(display,raw,tracking,support)==0);
    tracking[index].consecutive_hits=1;tracking[index].consecutive_misses=1;
    assert(mao::joint::recover_first_hit_display(display,raw,tracking,support)==0);
    tracking[index].consecutive_misses=0;raw={};
    assert(mao::joint::recover_first_hit_display(display,raw,tracking,support)==0);
}
