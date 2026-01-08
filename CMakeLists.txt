cmake_minimum_required(VERSION 3.20)
project(reversi_core LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

add_library(reversi_core SHARED
    cpp/src/Board.cpp
    cpp/src/AI.cpp
    cpp/src/Game.cpp
    cpp/src/api.cpp
)

target_include_directories(reversi_core PUBLIC cpp/include)

if (MSVC)
    target_compile_options(reversi_core PRIVATE /W4 /permissive-)
else()
    target_compile_options(reversi_core PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Ensure DLL outputs to the build directory with a consistent name
set_target_properties(reversi_core PROPERTIES
    OUTPUT_NAME reversi_core
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
    ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)