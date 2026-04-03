# Makefile

SIM = verilator
TOPLEVEL_LANG = verilog
TEST_SOURCE =  $(shell pwd)/rtl
CPPFLAGS += -lz -L/usr/local/lib/ -lxspcomm 
EXTRA_ARGS +=  --timescale 1ns/1ps --threads 8 --MAKEFLAGS -DVL_INLINE_OPT=inline -O3 --instr-count-dpi 0
EXTRA_ARGS += -Irtl/ -f picker.f  --no-timing -Wno-fatal -CFLAGS '-lz -L/usr/local/lib/ -lxspcomm -fcoroutines' -LDFLAGS '-lz -L/usr/local/lib/ -lxspcomm'
PLUSARGS += 

TOPLEVEL = SimTop
MODULE = XSTest

include $(shell cocotb-config --makefiles)/Makefile.sim