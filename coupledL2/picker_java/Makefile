TOP_ENTRY := $(shell pwd)/../rtl/TestTop.v
TOP_FILES :=$(shell pwd)/../filelist.txt
TOP_MODULE = TestTop
TARGET_NAME = CoupledL2

WAVE := true
TL ?= java
VERBOSE := false
EXAMPLE := false

PROJECT_INC := $(shell pwd)/out/picker_out_coupledL2

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

JAVA_SRC = $(shell find $(abspath ./src) -name "*.java")
DUT_CLASSPATH =  $(shell picker --show_xcom_lib_location_java):$(shell find $(PROJECT_INC) -name "*.jar" | tr '\n' ':').
JAVA_FLAGS = -encoding UTF-8 -classpath $(DUT_CLASSPATH) -d out/classes
# JVM options ref: "https://www.reddit.com/r/feedthebeast/comments/uz21wc/graalvm_speeds_up_modded_minecraft/"
JVM_OPTIONS = -classpath $(DUT_CLASSPATH):out/classes -Xmx1G -Xms32M -XX:+UnlockExperimentalVMOptions -XX:+UnlockDiagnosticVMOptions -XX:+AlwaysPreTouch -XX:+DisableExplicitGC -XX:+UseNUMA -XX:NmethodSweepActivity=1 -XX:ReservedCodeCacheSize=400M -XX:NonNMethodCodeHeapSize=12M -XX:ProfiledCodeHeapSize=194M -XX:NonProfiledCodeHeapSize=194M -XX:-DontCompileHugeMethods -XX:MaxNodeLimit=240000 -XX:NodeLimitFudgeFactor=8000 -XX:+UseVectorCmov -XX:+PerfDisableSharedMem -XX:+UseFastUnorderedTimeStamps -XX:+UseCriticalJavaThreadPriority -XX:AllocatePrefetchStyle=3  -XX:+UseG1GC -XX:MaxGCPauseMillis=37 -XX:+PerfDisableSharedMem -XX:G1HeapRegionSize=16M -XX:G1NewSizePercent=23 -XX:G1ReservePercent=20 -XX:SurvivorRatio=32 -XX:G1MixedGCCountTarget=3 -XX:G1HeapWastePercent=20 -XX:InitiatingHeapOccupancyPercent=10 -XX:G1RSetUpdatingPauseTimePercent=0 -XX:MaxTenuringThreshold=1 -XX:G1SATBBufferEnqueueingThresholdPercent=30 -XX:G1ConcMarkStepDurationMillis=5.0 -XX:GCTimeRatio=99


run-test: compile
	@java $(JVM_OPTIONS) TestCoupledL2
	@echo "---------Test CoupledL2 Start---------"

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
		--tdir ${TARGET} ${_WAVEFORM}${_EXAMPLE} ${_VERBOSE}

compile:
	@javac $(JAVA_FLAGS) $(JAVA_SRC)
	@echo "Build target exists in ./out/classes"

clean:
	rm -rf ${TARGET}

.PHONY: run-test dut compile clean
