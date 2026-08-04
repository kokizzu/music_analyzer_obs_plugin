#include "audacious_title.hpp"

#include <cassert>
#include <iostream>

int main()
{
	using mao::extract_audacious_song_title;
	using mao::make_scrolling_title;

	assert(extract_audacious_song_title("Artist - Album - Song title") == "Song title");
	assert(extract_audacious_song_title("Artist - Album - Song - Live - Audacious") == "Song - Live");
	assert(extract_audacious_song_title("Artist - filename.flac") == "filename.flac");
	assert(extract_audacious_song_title("Audacious - filename.mp3") == "filename.mp3");
	assert(extract_audacious_song_title("filename.ogg [Audacious]") == "filename.ogg");
	assert(extract_audacious_song_title("Artist - Album - Tést") == "T?st");

	assert(make_scrolling_title("Short", 12, 100) == "Short");
	assert(make_scrolling_title("ABCDEFGHIJ", 5, 0) == "ABCDE");
	assert(make_scrolling_title("ABCDEFGHIJ", 5, 8) == "IJ   ");
	assert(make_scrolling_title("ABCDEFGHIJ", 5, 10) == "   --");
	assert(make_scrolling_title("ABCDEFGHIJ", 0, 0).empty());

	std::cout << "audacious title tests passed\n";
	return 0;
}
