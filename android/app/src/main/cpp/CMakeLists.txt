cmake_minimum_required(VERSION 3.22)

project(music_analyzer_android LANGUAGES C CXX)

set(MAO_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../../../../")
file(GLOB BTT_C_SOURCES CONFIGURE_DEPENDS
    "${MAO_ROOT}/third_party/beat_and_tempo_tracking/src/*.c"
)

add_library(music_analyzer_android SHARED
    "${MAO_ROOT}/src/analyzer.cpp"
    "${MAO_ROOT}/src/fret_control.cpp"
    "${MAO_ROOT}/src/visualizer_renderer.cpp"
    "android_bridge.cpp"
    ${BTT_C_SOURCES}
)

target_include_directories(music_analyzer_android PRIVATE
    "${MAO_ROOT}/src"
    "${MAO_ROOT}/third_party/beat_and_tempo_tracking"
    "${MAO_ROOT}/third_party/beat_and_tempo_tracking/src"
)

target_compile_features(music_analyzer_android PRIVATE cxx_std_17)
target_compile_options(music_analyzer_android PRIVATE -Wall -Wextra)
target_link_libraries(music_analyzer_android PRIVATE android jnigraphics log)
