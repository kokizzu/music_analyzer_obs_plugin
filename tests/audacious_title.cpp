#include "audacious_title.hpp"

#include <cassert>
#include <iostream>
#include <string>

int main()
{
	using mao::extract_audacious_song_title;
	using mao::find_audacious_window_title;
	using mao::format_audacious_artist_title;
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
	assert(extract_audacious_song_title("Artist - Album - Tést") == "T?st");

	assert(format_audacious_artist_title("GMS Live", "Sambut Sang Raja (Official Video...) ") ==
	       "GMS Live - Sambut Sang Raja");
	assert(format_audacious_artist_title("GMS Live", "Sambut Sang Raja (Live at Jakarta)") ==
	       "GMS Live - Sambut Sang Raja");
	assert(format_audacious_artist_title("", "Sambut Sang Raja (Official Video)") == "Sambut Sang Raja");
	assert(format_audacious_artist_title("GMS Live", "Sambut Sang Raja") ==
	       "GMS Live - Sambut Sang Raja");

	assert(make_scrolling_title("Short", 12, 100) == "Short");
	assert(make_scrolling_title("ABCDEFGHIJ", 5, 0) == "ABCDE");
	assert(make_scrolling_title("ABCDEFGHIJ", 5, 8) == "IJ   ");
	assert(make_scrolling_title("ABCDEFGHIJ", 5, 10) == "   --");
	assert(make_scrolling_title("ABCDEFGHIJ", 0, 0).empty());

	std::cout << "audacious title tests passed\n";
	return 0;
}
