cmake_minimum_required(VERSION 3.15)

project({{TOP_NAME}}Raw VERSION 1.0)

include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++20" COMPILER_SUPPORTS_CXX20)
if(COMPILER_SUPPORTS_CXX20)
    set(CMAKE_CXX_STANDARD 20)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++20 -fcoroutines")
else()
    set(CMAKE_CXX_STANDARD 17)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17")
endif()

execute_process(
    COMMAND bash -c "verilator -V|grep ROOT|grep verilator|tail -n 1|awk '{print $3}'"
    OUTPUT_VARIABLE CMD_VERILATOR_ROOT
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
find_package(verilator REQUIRED PATHS ${CMD_VERILATOR_ROOT} NO_DEFAULT_PATH)

add_library(DPI{{TOP_NAME}} STATIC IMPORTED)
set_property(
    TARGET DPI{{TOP_NAME}}
    PROPERTY IMPORTED_LOCATION
    ${CMAKE_CURRENT_SOURCE_DIR}/../build/libDPI{{TOP_NAME}}.a
)

add_executable(UT{{TOP_NAME}}_example example.cpp)
target_include_directories(
    UT{{TOP_NAME}}_example
    PRIVATE
    ${VERILATOR_ROOT}/include
    ${VERILATOR_ROOT}/include/vltstd
    ${CMAKE_CURRENT_SOURCE_DIR}/../build/DPI{{TOP_NAME}}
)
target_link_libraries(UT{{TOP_NAME}}_example PRIVATE DPI{{TOP_NAME}} dl z pthread atomic)
