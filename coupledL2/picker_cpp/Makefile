TOP_ENTRY := $(shell pwd)/../rtl/TestTop.v
TOP_FILES :=$(shell pwd)/../filelist.txt
TOP_MODULE = TestTop
TARGET_NAME = CoupledL2

WAVE := true
TL ?= cpp
VERBOSE := false
EXAMPLE := false

PROJECT_INC := $(shell pwd)/out/picker_out_coupledL2/UT_CoupledL2

ifneq ($(TARGET),)
	TARGET := $(TARGET)
else
	TARGET := out/picker_out_coupledL2
endif

# if EXAMPLE is set, then _EXAMPLE is set to -e
ifneq ($(EXAMPLE), false)
	_EXAMPLE := -e
endif
_EXAMPLE ?=
# if VERBOSE is set, then _VERBOSE is set to -v
ifneq ($(VERBOSE), false)
	_VERBOSE := --verbose
endif
_VERBOSE ?=
# if WAVE is set, then _WAVEFORM is set to -w
ifneq ($(WAVE), false)
	ifneq ($(WAVE), true)
		_WAVEFORM := -w $(WAVE)
	else
		_WAVEFORM := -w coupledL2.fst
	endif
endif
_WAVEFORM ?=

run-test: compile
	@./out/build/test_coupledL2
	@echo "---------Test CoupledL2 End ---------"

dut:
	@echo "Building tage module with parameters: "
	@echo "TL=${TL}"
	@echo "TOP_ENTRY=${TOP_ENTRY}"
	@echo "TOP_FILES=${TOP_FILES}"
	@echo "TARGET=${TARGET}"
	@echo "WAVEFORM=${_WAVEFORM}"
	@echo "VERBOSE=${_VERBOSE}"
	@echo "EXAMPLE=${_EXAMPLE}"

	@mkdir -p out
	rm -rf ${TARGET}
	picker export ${TOP_ENTRY} --sname ${TOP_MODULE} --tname ${TARGET_NAME} --fs ${TOP_FILES} --lang ${TL} -c\
		--tdir ${TARGET} ${_WAVEFORM}${_EXAMPLE} ${_VERBOSE} --cp_lib true


compile:
	@cmake . -Bout/build
	@cmake --build out/build --config Release --parallel `nproc`
	@echo "Build target exists in ./out/build"

clean:
	rm -rf ${TARGET}

.PHONY: run-test dut compile clean
