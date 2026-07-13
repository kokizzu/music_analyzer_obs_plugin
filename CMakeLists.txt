cmake_minimum_required(VERSION 3.16)

project(music_analyzer_obs_plugin VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBOBS REQUIRED libobs)
pkg_get_variable(LIBOBS_INCLUDEDIR libobs includedir)

set(LIBOBS_CXX_FLAGS ${LIBOBS_CFLAGS_OTHER})
list(REMOVE_ITEM LIBOBS_CXX_FLAGS "-std=gnu17" "-Werror")
set(LOCAL_SIMDE_INCLUDE "${CMAKE_CURRENT_SOURCE_DIR}/build/deps/usr/include")

add_library(music-analyzer-obs MODULE
    src/analyzer.cpp
    src/plugin.cpp
)

target_include_directories(music-analyzer-obs PRIVATE
    ${LIBOBS_INCLUDE_DIRS}
    ${LOCAL_SIMDE_INCLUDE}
    ${LIBOBS_INCLUDEDIR}/obs
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)
target_compile_options(music-analyzer-obs PRIVATE
    ${LIBOBS_CXX_FLAGS}
    -Wall
    -Wextra
)
target_link_directories(music-analyzer-obs PRIVATE ${LIBOBS_LIBRARY_DIRS})
target_link_libraries(music-analyzer-obs PRIVATE ${LIBOBS_LIBRARIES} pthread)
set_target_properties(music-analyzer-obs PROPERTIES PREFIX "")

add_executable(analyzer_smoke tests/analyzer_smoke.cpp src/analyzer.cpp)
target_include_directories(analyzer_smoke PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(analyzer_smoke PRIVATE -Wall -Wextra)

enable_testing()
add_test(NAME analyzer_smoke COMMAND analyzer_smoke)
