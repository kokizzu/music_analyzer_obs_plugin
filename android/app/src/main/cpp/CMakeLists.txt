cmake_minimum_required(VERSION 3.22)

project(music_analyzer_android LANGUAGES CXX)

set(MAO_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../../../../")

add_library(music_analyzer_android SHARED
    "${MAO_ROOT}/src/analyzer.cpp"
    "${MAO_ROOT}/src/visualizer_renderer.cpp"
    "android_bridge.cpp"
)

target_include_directories(music_analyzer_android PRIVATE
    "${MAO_ROOT}/src"
)

target_compile_features(music_analyzer_android PRIVATE cxx_std_17)
target_compile_options(music_analyzer_android PRIVATE -Wall -Wextra)
target_link_libraries(music_analyzer_android PRIVATE android jnigraphics log)
