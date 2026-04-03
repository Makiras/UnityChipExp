LOG_DIR ?= logs
VERILATOR_THREADS ?= 4
BENCH_INSTALL := python3 ../../scripts/install_benchmarks.py --mode picker --dut coupledL2 --root $(CURDIR)

all: python-dpi python-vpi python-mem

clean:
	rm -rf *_python $(LOG_DIR)

python-dpi: 
	picker export ../rtl/TestTop.v --sname TestTop --autobuild false --lang python --tdir dpi_python \
		--sdir /home/xyl/picker/template --fs ../filelist.txt -V "--no-timing;--threads;$(VERILATOR_THREADS)" -C "-fPIC"
	$(BENCH_INSTALL) --variant python-dpi

python-mem:
	picker export ../rtl/TestTop.v --sname TestTop --autobuild false --lang python --tdir mem_python \
		--sdir /home/xyl/picker/template --fs ../filelist.txt -V "--no-timing;--threads;$(VERILATOR_THREADS)" -C "-fPIC" --rw mem_direct
	$(BENCH_INSTALL) --variant python-mem_direct

python-vpi: 
	picker export ../rtl/TestTop.v --sname TestTop --autobuild false --lang python --tdir vpi_python \
		--sdir /home/xyl/picker/template --fs ../filelist.txt -V "--no-timing;--threads;$(VERILATOR_THREADS)" -C "-fPIC" --vpi
	$(BENCH_INSTALL) --variant python-vpi
