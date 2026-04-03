
LOG_DIR ?= logs
VERILATOR_THREADS ?= 1
BENCH_INSTALL := python3 ../../scripts/install_benchmarks.py --mode multilang --dut coupledL2 --root $(CURDIR)

all: python-dpi cpp-dpi java-dpi golang-dpi


clean:
	rm -rf dpi_python dpi_cpp dpi_java dpi_golang dpi_scala $(LOG_DIR)

python-dpi: 
	picker export ../rtl/TestTop.v  --sname TestTop --verbose --autobuild false --lang python --tdir dpi_python \
		--sdir /home/xyl/picker/template --fs ../filelist.txt -V "--no-timing;--threads;$(VERILATOR_THREADS);-CFLAGS;-lz;-LDFLAGS;-lz" -C "-fPIC -lz"
	$(BENCH_INSTALL) --variant python

cpp-dpi: 
	picker export ../rtl/TestTop.v  --sname TestTop --verbose --autobuild false --lang cpp --tdir dpi_cpp \
		--sdir /home/xyl/picker/template --fs ../filelist.txt -V "--no-timing;--threads;$(VERILATOR_THREADS);-CFLAGS;-lz;-LDFLAGS;-lz" -C "-fPIC -lz"
	$(BENCH_INSTALL) --variant cpp --variant raw-verilator

java-dpi: 
	picker export ../rtl/TestTop.v  --sname TestTop --verbose --autobuild false --lang java --tdir dpi_java \
		--sdir /home/xyl/picker/template --fs ../filelist.txt -V "--no-timing;--threads;$(VERILATOR_THREADS);-CFLAGS;-lz;-LDFLAGS;-lz" -C "-fPIC -lz"
	$(BENCH_INSTALL) --variant java

golang-dpi: 
	picker export ../rtl/TestTop.v  --sname TestTop --verbose --autobuild false --lang golang --tdir dpi_golang \
		--sdir /home/xyl/picker/template --fs ../filelist.txt -V "--no-timing;--threads;$(VERILATOR_THREADS);-CFLAGS;-lz;-LDFLAGS;-lz" -C "-fPIC -lz"
	$(BENCH_INSTALL) --variant golang

# scala-dpi: 
# 	picker export ../rtl/TestTop.v  --sname TestTop --verbose --autobuild false --lang scala --tdir dpi_scala \
# 		--sdir /home/xyl/picker/template --fs ../filelist.txt -V "--no-timing;-CFLAGS;-lz;-LDFLAGS;-lz" -C "-fPIC -lz"

test:
	PYTHONPATH=. python3 test.py $(args)
