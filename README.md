# Reproduction Guide

This repository contains two independent experiment groups.

- Group A: `cocotb` vs `python-dpi` vs `python-vpi` vs `python-mem_direct`
- Group B: `raw-verilator` vs `python` vs `cpp` vs `java` vs `golang`

Only these DUTs are in scope:

- `rocket / SimTop`
- `coupledL2 / TestTop`
- `XS / SimTop`

`XS` uses the same workflow, but it is much heavier. The commands below focus on `rocket` and `coupledL2`.

## Requirements

The commands below assume:

- `picker` is installed and available in `PATH`
- `verilator` is installed
- `python3`, `cmake`, `swig` are installed
- `java` is installed for Group B Java
- `go` is installed for Group B Golang
- `cocotb` is installed for Group A cocotb
- `ccache` is installed for the cocotb Verilator build
- the local picker template directory exists at `/home/xyl/picker/template`

## Quick Start

Start from the repository root:

```bash
cd /home/xyl/exp
```

## Group A

Group A compares:

- `python-dpi`
- `python-vpi`
- `python-mem_direct`
- `cocotb`

Thread policy:

- `rocket`: `4` Verilator threads
- `coupledL2`: `4` Verilator threads
- `XS`: `8` Verilator threads

Runtime policy:

- `warmup_steps = 1000`
- `bench_steps = 300000`
- `run_repeats = 7`
- trim one max and one min sample
- report the middle `5`

Runtime pinning:

- `rocket/coupledL2`: `96-99`
- `XS`: `96-103`

### Run Group A for `rocket`

```bash
cd /home/xyl/exp

make -C rocket/picker clean
bash rocket/picker/build_time.sh
bash rocket/picker/run_time.sh

rm -rf rocket/cocotb/sim_build rocket/cocotb/results.xml rocket/cocotb/logs
bash rocket/cocotb/build_time.sh
bash rocket/cocotb/run_time.sh

python3 scripts/extract_metrics.py \
  --group A \
  --output-dir results/extracted/group_a_rocket
```

### Run Group A for `coupledL2`

```bash
cd /home/xyl/exp

make -C coupledL2/picker clean
bash coupledL2/picker/build_time.sh
bash coupledL2/picker/run_time.sh

rm -rf coupledL2/cocotb/sim_build coupledL2/cocotb/results.xml coupledL2/cocotb/logs
bash coupledL2/cocotb/build_time.sh
bash coupledL2/cocotb/run_time.sh

python3 scripts/extract_metrics.py \
  --group A \
  --output-dir results/extracted/group_a_coupledl2
```

### Run Group A for `XS`

```bash
cd /home/xyl/exp

make -C XS clean
bash XS/build_time.sh
bash XS/run_time.sh

rm -rf XS/cocotb/sim_build XS/cocotb/results.xml XS/cocotb/logs
bash XS/cocotb/build_time.sh
bash XS/cocotb/run_time.sh

python3 scripts/extract_metrics.py \
  --group A \
  --output-dir results/extracted/group_a_xs
```

## Group B

Group B compares:

- `raw-verilator`
- `python`
- `cpp`
- `java`
- `golang`

Runtime policy:

- single-thread Verilator
- single pinned CPU by default
- `warmup_steps = 1000`
- `rocket = 2000000` steps
- `coupledL2 = 2200000` steps
- `XS = 5000` steps
- `run_repeats = 7`
- trim one max and one min sample
- report the middle `5`

Build policy:

- generated wrapper Makefiles are patched from `all: test clean` to `all: compile clean`
- build time does not include example execution

Runtime pinning:

- default CPU: `96`
- default NUMA node: `1`

### Run Group B for `rocket`

```bash
cd /home/xyl/exp

make -C rocket/multilang clean
bash rocket/multilang/build_time.sh
bash rocket/multilang/run_time.sh

python3 scripts/extract_metrics.py \
  --group B \
  --output-dir results/extracted/group_b_rocket
```

### Run Group B for `coupledL2`

```bash
cd /home/xyl/exp

make -C coupledL2/multilang clean
bash coupledL2/multilang/build_time.sh
bash coupledL2/multilang/run_time.sh

python3 scripts/extract_metrics.py \
  --group B \
  --output-dir results/extracted/group_b_coupledl2
```

### Run Group B for `XS`

```bash
cd /home/xyl/exp

make -C XS/multilang clean
bash XS/multilang/build_time.sh
bash XS/multilang/run_time.sh

python3 scripts/extract_metrics.py \
  --group B \
  --output-dir results/extracted/group_b_xs
```

## All-in-One Commands

### Group A, `rocket + coupledL2`

```bash
cd /home/xyl/exp

make -C rocket/picker clean
bash rocket/picker/build_time.sh
bash rocket/picker/run_time.sh
rm -rf rocket/cocotb/sim_build rocket/cocotb/results.xml rocket/cocotb/logs
bash rocket/cocotb/build_time.sh
bash rocket/cocotb/run_time.sh

make -C coupledL2/picker clean
bash coupledL2/picker/build_time.sh
bash coupledL2/picker/run_time.sh
rm -rf coupledL2/cocotb/sim_build coupledL2/cocotb/results.xml coupledL2/cocotb/logs
bash coupledL2/cocotb/build_time.sh
bash coupledL2/cocotb/run_time.sh

python3 scripts/extract_metrics.py \
  --group A \
  --output-dir results/extracted/group_a
```

### Group B, `rocket + coupledL2`

```bash
cd /home/xyl/exp

make -C rocket/multilang clean
bash rocket/multilang/build_time.sh
bash rocket/multilang/run_time.sh

make -C coupledL2/multilang clean
bash coupledL2/multilang/build_time.sh
bash coupledL2/multilang/run_time.sh

python3 scripts/extract_metrics.py \
  --group B \
  --output-dir results/extracted/group_b
```

## Output Files

After a run:

- raw logs are recreated under each experiment directory as `logs/`
- extracted tables are written to the `--output-dir` you choose

The extractor writes:

- `metrics.csv`
- `metrics.json`

## Metrics

Main fields:

- `codegen_total_s`
- `build_total_s`
- `simulation_speed`
- `simulation_speed_std`
- `peak_memory_kb`
- `peak_memory_std_kb`
- `artifact_size_bytes`

Definitions:

- `codegen_total_s` and `build_total_s` use GNU `time` CPU time: `user + system`
- `simulation_speed` comes from benchmark output inside the program
- `peak_memory_kb` comes from `/usr/bin/time -v`
- repeated runtime logs are trimmed before aggregation

## Notes

- Group A and Group B are independent. Do not mix their runtime settings.
- `scripts/install_benchmarks.py` is part of the workflow. It injects benchmark programs and patches generated wrapper Makefiles.
- This repository does not keep historical logs by default. Re-running the commands above recreates the required logs and extracted tables.
