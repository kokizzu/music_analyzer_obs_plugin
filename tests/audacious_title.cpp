#include "audacious_poll_schedule.hpp"
#include "audacious_title.hpp"

#include <cassert>
#include <iostream>
#include <string>

int main()
{
	using mao::clean_audacious_title;
	using mao::audacious_title_poll_wait;
	using mao::extract_audacious_song_title;
	using mao::find_audacious_window_title;
	using mao::make_scrolling_title;

	const std::string wmctrl_output =
		"0x03a00007  0 audacious.Audacious host Artist - Album - Song title\n"
		"0x03a00008  0 audacious.Audacious host Audacious Preferences\n";
	assert(find_audacious_window_title(wmctrl_output) == "Artist - Album - Song title");

	assert(extract_audacious_song_title("Artist - Album - Song title") == "Song title");
	assert(extract_audacious_song_title("Artist - Album - Song - Live - Audacious") == "Song - Live");
	assert(extract_audacious_song_title("Artist - filename.flac") == "filename.flac");
	assert(extract_audacious_song_title("Audacious - filename.mp3") == "filename.mp3");
	assert(extract_audacious_song_title("filename.ogg [Audacious]") == "filename.ogg");
	assert(extract_audacious_song_title("Artist - Album - Tést") == "Tést");

	// Exact window-title rule: remove Artist and Album, keep only the Title
	// field and YouTube ID, then strip recognized presentation-only tags.
	assert(extract_audacious_song_title(
		       "music-yt - flac_output - GMS Live - Sambut Sang Raja "
		       "(Official Music Video) [drKw4ogAqsAJ]") ==
	       "GMS Live - Sambut Sang Raja [drKw4ogAqsAJ]");

	assert(clean_audacious_title("GMS Live - Sambut Sang Raja (Official Video...)") ==
	       "GMS Live - Sambut Sang Raja");
	assert(clean_audacious_title("GMS Live - Sambut Sang Raja (Official Music Video)") ==
	       "GMS Live - Sambut Sang Raja");
	assert(clean_audacious_title("GMS Live - Sambut Sang Raja (Official Lyric Video)") ==
	       "GMS Live - Sambut Sang Raja");
	assert(clean_audacious_title("GMS Live - Sambut Sang Raja (Official Lyrics Video)") ==
	       "GMS Live - Sambut Sang Raja");
	assert(clean_audacious_title("GMS Live - Sambut Sang Raja (Official Video Music)") ==
	       "GMS Live - Sambut Sang Raja");
	assert(clean_audacious_title("GMS Live - Sambut Sang Raja (Live)") ==
	       "GMS Live - Sambut Sang Raja");
	assert(clean_audacious_title("GMS Live - Sambut Sang Raja (Live at Jakarta)") ==
	       "GMS Live - Sambut Sang Raja (Live at Jakarta)");

	assert(clean_audacious_title("OCEANS (Pop-Punk Cover) [OVvN_YzWEgc]") ==
	       "OCEANS (Pop-Punk Cover) [OVvN_YzWEgc]");
	assert(clean_audacious_title("OCEANS (Official Music Video) [OVvN_YzWEgc]") ==
	       "OCEANS [OVvN_YzWEgc]");
	assert(clean_audacious_title("OCEANS (Official Video Music) [OVvN_YzWEgc] music-yt") ==
	       "OCEANS [OVvN_YzWEgc]");
	assert(clean_audacious_title("OCEANS (Official Video Music) [OVvN_YzWEgc].music-yt") ==
	       "OCEANS [OVvN_YzWEgc]");
	assert(clean_audacious_title("愛昧ショコラーテ -PandaBoYremix- [0qomiyjPNDc]") ==
	       "愛昧ショコラーテ -PandaBoYremix- [0qomiyjPNDc]");

	assert(make_scrolling_title("Short", 12, 100) == "Short");
	assert(make_scrolling_title("ABCDEFGHIJ", 5, 0) == "ABCDE");
	assert(make_scrolling_title("ABCDEFGHIJ", 5, 8) == "IJ   ");
	assert(make_scrolling_title("ABCDEFGHIJ", 5, 10) == "   --");
	assert(make_scrolling_title("愛昧ショコラーテ", 4, 0) == "愛昧ショ");
	assert(make_scrolling_title("ABCDEFGHIJ", 0, 0).empty());

	using namespace std::chrono_literals;
	assert(audacious_title_poll_wait(0ms) == 1000ms);
	assert(audacious_title_poll_wait(50ms) == 950ms);
	assert(audacious_title_poll_wait(999ms) == 1ms);
	assert(audacious_title_poll_wait(1000ms) == 0ms);
	assert(audacious_title_poll_wait(1750ms) == 0ms);

	std::cout << "audacious title tests passed\n";
	return 0;
}
