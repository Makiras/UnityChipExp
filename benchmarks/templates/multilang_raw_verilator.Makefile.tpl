CURRENT_DIR := $(shell pwd)
NPROC := $(shell (nproc 2>/dev/null || sysctl -n hw.ncpu) 2>/dev/null)
.PHONY: all test compile clean purge

all: test clean
	@echo "All complete"

test: compile
	@cp build/UT{{TOP_NAME}}_example .
	@rm -rf build
	@echo "--------------Compile Success Test Step DUT--------------------"
	@./UT{{TOP_NAME}}_example && rm -rf *.fst *.vcd *.fsdb *.log *.key 2>/dev/null || true
	@echo "--------------------------------------------------------------"

compile:
	@echo "start build raw benchmark at $(shell date)"
	@cmake . -Bbuild
	@cmake --build build --config Release --parallel $(NPROC)
	@echo "end build raw benchmark at $(shell date)"

clean:
	@rm -rf *.fst *.vcd *.fsdb *.log *.key *.dat build

purge: clean
	@mv ./* ../ || true
	@echo "purge complete"
	@rm -rf $(CURRENT_DIR)
