# Benchmarks

This directory stores the benchmark source files that are used for the
artifact evaluation flows.

These files are the source of truth for runtime microbenchmarks.
Do not edit benchmark `example.*` files inside picker-generated output
directories directly, because they can be overwritten by a fresh codegen run.

Use `scripts/install_benchmarks.py` to copy the benchmark sources into the
generated directories after each export.

Current benchmark rules:

- assert `reset`
- initialize `clock`
- run DUT-specific benchmark steps:
  - `XS`: `5000`
  - `rocket`: `2000000`
  - `coupledL2`: `2200000`
- print machine-readable timing lines:
  - `bench_steps=...`
  - `bench_elapsed_ms=...`
  - `bench_speed_cycles_per_s=...`
- for Group B runtime experiments, clean build once and run each case `5` times
