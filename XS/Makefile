
LOG_DIR ?= logs
VERILATOR_THREADS ?= 8
BENCH_INSTALL := python3 ../scripts/install_benchmarks.py --mode picker --dut XS --root $(CURDIR)

all: python-dpi python-vpi python-mem


clean:
	rm -rf *_python $(LOG_DIR)

python-dpi: 
	picker export rtl/SimTop.sv --autobuild false --lang python --tdir dpi_python \
		--sdir /home/xyl/picker/template --fs rtl/picker.f -V "--no-timing;--threads;$(VERILATOR_THREADS)" -C "-fPIC  -lz"
	$(BENCH_INSTALL) --variant python-dpi

python-mem:
	picker export rtl/SimTop.sv --autobuild false --lang python --tdir mem_python \
		--sdir /home/xyl/picker/template --fs rtl/picker.f -V "--no-timing;--threads;$(VERILATOR_THREADS)" -C "-fPIC  -lz" --rw mem_direct
	$(BENCH_INSTALL) --variant python-mem_direct

python-vpi: 
	picker export rtl/SimTop.sv --autobuild false --lang python --tdir vpi_python \
		--sdir /home/xyl/picker/template --fs rtl/picker.f -V "--no-timing;--threads;$(VERILATOR_THREADS)" -C "-fPIC  -lz" --vpi
	$(BENCH_INSTALL) --variant python-vpi

test:
	PYTHONPATH=. python3 test.py $(args)
