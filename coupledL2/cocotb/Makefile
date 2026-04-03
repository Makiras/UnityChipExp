# Makefile

SIM = verilator
TOPLEVEL_LANG = verilog
TEST_SOURCE =  $(shell pwd)/../

waves = True
CPPFLAGS += -lz -L/usr/local/lib/ -lxspcomm 
# EXTRA_ARGS += --coverage --trace-fst --timescale 1ns/1ps
EXTRA_ARGS += -f ${TEST_SOURCE}/filelist.txt --no-timing
EXTRA_ARGS += --timescale 1ns/1ps --threads 4 --MAKEFLAGS -DVL_INLINE_OPT=inline -O3 --instr-count-dpi 0
# EXTRA_ARGS += --no-timing -Wno-fatal -CFLAGS '-lz -L/usr/local/lib/ -lxspcomm -fcoroutines' -LDFLAGS '-lz -L/usr/local/lib/ -lxspcomm'
PLUSARGS += --trace

# VERILOG_SOURCES = ${TEST_SOURCE}/rtl/TestTop.v
TOPLEVEL = TestTop
MODULE = TLTest

include $(shell cocotb-config --makefiles)/Makefile.sim
