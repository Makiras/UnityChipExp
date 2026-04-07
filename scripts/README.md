# Scripts

This directory contains:

- one-click experiment wrappers:
  - `A_without_XS.sh`
  - `B_without_XS.sh`
  - `A_with_XS.sh`
  - `B_with_XS.sh`
- extraction and plotting helpers:
  - `extract_metrics.py`
  - `plot_metrics.py`
  - `plot_metrics_cli.py`
- benchmark installation helper:
  - `install_benchmarks.py`

## Recommended Use

Use the one-click shell scripts first. They:

- reuse existing build artifacts by default
- only build when required files are missing
- run the corresponding `run_time.sh`
- re-extract metrics automatically
- write extracted tables under `results/extracted/...`
- print CLI bar charts at the end

Examples:

```bash
./scripts/A_without_XS.sh
./scripts/B_without_XS.sh
./scripts/A_with_XS.sh
./scripts/B_with_XS.sh
```

If runtime pinning cannot be honored on your machine, rerun with `PIN_RUNTIME=0`, for example:

```bash
PIN_RUNTIME=0 ./scripts/A_without_XS.sh
```

## Extract Metrics

Manual extraction:

```bash
python3 scripts/extract_metrics.py --group A
python3 scripts/extract_metrics.py --group B
```

The extractor records:

- GNU `time` CPU totals as `user + system`
- trimmed runtime aggregates from `7` runs, dropping one max and one min
- simulation speed
- runtime memory
- artifact size

## CLI Plots

Terminal plots:

```bash
python3 scripts/plot_metrics_cli.py --group A
python3 scripts/plot_metrics_cli.py --group B
```

The CLI plots are grouped by DUT:

- `XS`
- `coupledL2`
- `rocket`

## Notes

- `scripts/experiment_matrix.csv` is the case source of truth.
- Group A and Group B are independent and use different runtime policies.
- `install_benchmarks.py` patches generated benchmark files and wrapper Makefiles as part of the workflow.
