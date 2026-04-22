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

## Docker

Published image:

```bash
sudo docker pull ghcr.io/makiras/unitychipexp:latest
sudo docker run --rm -it ghcr.io/makiras/unitychipexp:latest
```

Or build the image locally from the repository root:

```bash
cd /home/xyl/exp
sudo docker build --network=host -f docker/Dockerfile -t exp-repro:dev .
sudo docker run --rm -it exp-repro:dev
```

Inside the container, the working directory is already:

```bash
cd /home/xyl/exp
```

Runtime pinning should stay enabled by default.

- Group A pins runtime to a CPU set with `taskset`
- Group B pins runtime to a single CPU with `taskset`
- automatic topology detection is intentionally avoided because it behaves differently across bare metal, VMs, and containers
- the fixed defaults therefore expect at least `8` physical cores for reproducible runs
- only if your machine or container cannot honor `taskset`, fall back to `PIN_RUNTIME=0`

## Quick Start

After the environment is ready, start from the repository root:

```bash
cd /home/xyl/exp
```

Run the one-click scripts first if you only want to reproduce the experiments:

```bash
# Quick Check
./scripts/A_without_XS.sh
./scripts/B_without_XS.sh
# Full Check ( more than 1 days )
./scripts/A_with_XS.sh
./scripts/B_with_XS.sh
```

These scripts:

- prefer reusing existing build artifacts
- only rebuild when required files are missing
- re-extract metrics automatically
- print the CLI comparison charts at the end

Use the manual commands below only if you want to run one DUT or one group step by step.

## Group A

Group A compares:

- `python-dpi`
- `python-mem_direct`
- `python-vpi`
- `cocotb`

Thread policy:

- `rocket`: `4` Verilator threads
- `coupledL2`: `4` Verilator threads
- `XS`: `8` Verilator threads

Runtime policy:

- `warmup_steps = 1000`
- `rocket = 300000` steps
- `coupledL2 = 300000` steps
- `XS = 5000` steps
- `run_repeats = 7`
- trim one max and one min sample
- report the middle `5`

Runtime pinning:

- `rocket/coupledL2`: `2-5`
- `XS`: `2-9`

These defaults are fixed instead of auto-detected.

- different environments expose CPU topology differently, especially inside containers
- for consistency, the scripts use fixed CPU sets and expect at least `8` physical cores
- if your machine cannot honor these pinned sets, rerun with `PIN_RUNTIME=0` or override `PIN_CPUS`


### Manual Run for `rocket`

```bash
cd /home/xyl/exp

make -C rocket/picker clean
bash rocket/picker/build_time.sh
bash rocket/picker/run_time.sh

rm -rf rocket/cocotb/sim_build
rm -f rocket/cocotb/results.xml
bash rocket/cocotb/build_time.sh
bash rocket/cocotb/run_time.sh

python3 scripts/extract_metrics.py \
  --group A \
  --output-dir results/extracted/group_a_rocket
```

### Manual Run for `coupledL2`

```bash
cd /home/xyl/exp

make -C coupledL2/picker clean
bash coupledL2/picker/build_time.sh
bash coupledL2/picker/run_time.sh

rm -rf coupledL2/cocotb/sim_build
rm -f coupledL2/cocotb/results.xml
bash coupledL2/cocotb/build_time.sh
bash coupledL2/cocotb/run_time.sh

python3 scripts/extract_metrics.py \
  --group A \
  --output-dir results/extracted/group_a_coupledl2
```

### Manual Run for `XS`

```bash
cd /home/xyl/exp

make -C XS clean
bash XS/build_time.sh
bash XS/run_time.sh

rm -rf XS/cocotb/sim_build
rm -f XS/cocotb/results.xml
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

- default CPU: `2`
- no `numactl`; Group B now relies on `taskset` only

### Manual Run for `rocket`

```bash
cd /home/xyl/exp

make -C rocket/multilang clean
bash rocket/multilang/build_time.sh
bash rocket/multilang/run_time.sh

python3 scripts/extract_metrics.py \
  --group B \
  --output-dir results/extracted/group_b_rocket
```

### Manual Run for `coupledL2`

```bash
cd /home/xyl/exp

make -C coupledL2/multilang clean
bash coupledL2/multilang/build_time.sh
bash coupledL2/multilang/run_time.sh

python3 scripts/extract_metrics.py \
  --group B \
  --output-dir results/extracted/group_b_coupledl2
```

### Manual Run for `XS`

```bash
cd /home/xyl/exp

make -C XS/multilang clean
bash XS/multilang/build_time.sh
bash XS/multilang/run_time.sh

python3 scripts/extract_metrics.py \
  --group B \
  --output-dir results/extracted/group_b_xs
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

- `codegen_total_cpu_s`
- `build_total_cpu_s`
- `simulation_speed`
- `simulation_speed_std`
- `peak_memory_kb`
- `peak_memory_std_kb`
- `artifact_size_bytes`

Definitions:

- `codegen_total_cpu_s` and `build_total_cpu_s` use GNU `time` CPU time: `user + system`
- `simulation_speed` comes from benchmark output inside the program
- `peak_memory_kb` comes from `/usr/bin/time -v`
- repeated runtime logs are trimmed before aggregation

## Notes

- Group A and Group B are independent. Do not mix their runtime settings.
- `scripts/install_benchmarks.py` is part of the workflow. It injects benchmark programs and patches generated wrapper Makefiles.
- This repository does not keep historical logs by default. Re-running the commands above recreates the required logs and extracted tables.
