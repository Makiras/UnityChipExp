#!/usr/bin/env python3
import argparse
import csv
import os
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

try:
    import matplotlib.pyplot as plt
except ImportError as exc:
    raise SystemExit("matplotlib is required for plot_metrics.py") from exc

from _common import REPO_ROOT


GROUP_METRICS = {
    "A": ["codegen_total_s", "build_total_s", "artifact_size_bytes", "simulation_speed", "peak_memory_kb"],
    "B": ["simulation_speed", "peak_memory_kb"],
}


def load_metrics(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def numeric(value):
    if value in {"", "None", None}:
        return None
    return float(value)


def plot_group_metric(rows, group, metric, output_dir):
    relevant = [row for row in rows if row["group"] == group and numeric(row[metric]) is not None]
    if not relevant:
        return []

    if metric == "simulation_speed":
        by_unit = defaultdict(list)
        for row in relevant:
            by_unit[row["simulation_speed_unit"] or "unknown"].append(row)
    else:
        by_unit = {"default": relevant}

    outputs = []
    for unit, unit_rows in by_unit.items():
        labels = [f"{row['dut']}:{row['variant']}" for row in unit_rows]
        values = [numeric(row[metric]) for row in unit_rows]
        fig, ax = plt.subplots(figsize=(max(10, len(labels) * 0.7), 6))
        ax.bar(labels, values)
        ax.set_title(f"Group {group} - {metric}" + (f" ({unit})" if unit != "default" else ""))
        ax.set_ylabel(metric if unit == "default" else f"{metric} [{unit}]")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        suffix = f"_{unit}" if unit != "default" else ""
        path = output_dir / f"group_{group}_{metric}{suffix}.png"
        fig.savefig(path, dpi=160)
        plt.close(fig)
        outputs.append(path)
    return outputs


def main():
    parser = argparse.ArgumentParser(description="Plot extracted experiment metrics.")
    parser.add_argument("--input", default=str(REPO_ROOT / "results" / "extracted" / "metrics.csv"))
    parser.add_argument("--output-dir", default=str(REPO_ROOT / "results" / "plots"))
    parser.add_argument("--group", choices=["A", "B"])
    args = parser.parse_args()

    rows = load_metrics(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    groups = [args.group] if args.group else ["A", "B"]
    written = []
    for group in groups:
        for metric in GROUP_METRICS[group]:
            written.extend(plot_group_metric(rows, group, metric, output_dir))

    for path in written:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
