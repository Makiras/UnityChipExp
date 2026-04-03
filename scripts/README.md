# Scripts

This directory contains three separate script families:

- `run_experiments.py`: run selected cases and save raw logs
- `extract_metrics.py`: extract metrics from raw logs and runtime artifacts
- `plot_metrics.py`: generate plots from extracted metrics

## Typical Workflow

### 1. Run experiments

```bash
python3 scripts/run_experiments.py --group A
python3 scripts/run_experiments.py --group B
```

Raw logs are written to:

- `results/raw/<case_id>/generate.log`
- `results/raw/<case_id>/build.log`
- `results/raw/<case_id>/run.log`

To pass picker-generated Makefile parameters through the runner:

```bash
python3 scripts/run_experiments.py --group B \
  --make-var SIMULATOR=verilator \
  --make-var NPROC=8
```

To add environment variables:

```bash
python3 scripts/run_experiments.py --group B \
  --env VCS_HOME=/path/to/vcs \
  --env VERDI_HOME=/path/to/verdi
```

### 2. Extract metrics

```bash
python3 scripts/extract_metrics.py
```

If `results/raw/<case_id>/...` logs are missing, the extractor will fall back to the existing repository logs when a known path can be derived from the experiment matrix.

Extracted tables are written to:

- `results/extracted/metrics.csv`
- `results/extracted/metrics.json`

The extractor records:

- main totals as GNU `time` CPU time, that is `user + system`
- outer `elapsed` values as reference fields
- auxiliary inner build timings when the build log contains multiple GNU `time` entries
- for repeated runtime logs such as `*_run_1.log` to `*_run_5.log`, runtime speed and runtime memory are aggregated as mean and population standard deviation

### 3. Plot results

```bash
python3 scripts/plot_metrics.py
```

Plots are written to:

- `results/plots/`

## Notes

- The scripts use `scripts/experiment_matrix.csv` as the source of case definitions.
- `run_experiments.py` only launches the existing lower-level commands and archives their logs.
- Runtime speed and runtime memory are intentionally treated as different data sources.
- `cocotb` is handled separately in the extraction logic.
- The current Group B workflow is `clean build once, then run each case 5 times`.
