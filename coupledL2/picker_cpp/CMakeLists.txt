cmake_minimum_required(VERSION 3.11)

set(ModuleName CoupledL2)
project(test_coupledL2 CXX)


set(CMAKE_CXX_STANDARD 20 )
set(CMAKE_CXX_STANDARD_REQUIRED ON )
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++20 -fcoroutines -ftls-model=global-dynamic" )
add_definitions(-DENABLE_XCOROUTINE=true)
set(ENABLE_XCOROUTINE true)


# libs find by picker
include_directories(
        /usr/local/share/picker/include
        ~/.local/picker/include
)
link_directories(
        /usr/local/share/picker/lib
        ~/.local/picker/lib
)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fcoroutines")
add_definitions(-DUSE_VERILATOR)


execute_process(
        COMMAND bash -c "verilator -V|grep ROOT|grep verilator|head -n 1|awk '{print $3}'"
        OUTPUT_VARIABLE CMD_VERILATOR_ROOT
        OUTPUT_STRIP_TRAILING_WHITESPACE
)
find_package(verilator REQUIRED PATHS ${CMD_VERILATOR_ROOT}  NO_DEFAULT_PATH)
include_directories(${VERILATOR_ROOT}/include
        ${VERILATOR_ROOT}/include/vltstd)

set(DUT_MODULE_DIR ${CMAKE_SOURCE_DIR}/out/picker_out_coupledL2/UT_CoupledL2)

include_directories(${DUT_MODULE_DIR})
link_directories(${DUT_MODULE_DIR})
add_executable(test_coupledL2 test_dut.cc ${DUT_MODULE_DIR}/UT_${ModuleName}.cpp)
target_link_libraries(test_coupledL2 UT${ModuleName} xspcomm ${CMAKE_DL_LIBS})
