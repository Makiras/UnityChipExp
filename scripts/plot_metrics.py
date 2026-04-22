#!/usr/bin/env python3
import argparse
import csv
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")

try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
except ImportError as exc:
    raise SystemExit("matplotlib is required for plot_metrics.py") from exc

from _common import REPO_ROOT


DUT_ORDER = ["XS", "coupledL2", "rocket"]
GROUP_A_VARIANTS = ["python-mem_direct", "python-dpi", "python-vpi", "cocotb"]
GROUP_B_VARIANTS = ["raw-verilator", "cpp", "python", "golang", "java"]

GROUP_METRICS = {
    "A": [
        ("build_total_cpu_s", "Build CPU Time"),
        ("artifact_size_bytes", "Binary Size"),
        ("simulation_speed", "Simulation Speed"),
        ("peak_memory_kb", "Simulation Memory"),
    ],
    "B": [
        ("simulation_speed", "Simulation Speed"),
        ("peak_memory_kb", "Simulation Memory"),
    ],
}

VARIANT_COLORS = {
    "python-dpi": "#4C78A8",
    "python-mem_direct": "#72B7B2",
    "python-vpi": "#F58518",
    "cocotb": "#E45756",
    "raw-verilator": "#4C78A8",
    "cpp": "#72B7B2",
    "python": "#54A24B",
    "golang": "#EECA3B",
    "java": "#B279A2",
}


def default_input_path():
    extracted_root = REPO_ROOT / "results" / "extracted"
    preferred = sorted(extracted_root.glob("final_all_latest_*/metrics.csv"))
    if preferred:
        return preferred[-1]
    fallback = sorted(extracted_root.glob("final_all*/metrics.csv"))
    if fallback:
        return fallback[-1]
    return extracted_root / "final_all_latest" / "metrics.csv"


def parse_args():
    parser = argparse.ArgumentParser(description="Render matplotlib bar charts using the same grouping as the CLI plots.")
    parser.add_argument("--input", default=str(default_input_path()), help="metrics.csv path")
    parser.add_argument("--output-dir", default=str(REPO_ROOT / "results" / "plots"), help="output directory")
    parser.add_argument("--group", choices=["A", "B"], help="experiment group to render")
    return parser.parse_args()


def load_rows(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def numeric(value):
    if value in {"", None, "None"}:
        return None
    return float(value)


def format_value(metric, value):
    if value is None:
        return "-"
    if metric in {"simulation_speed", "build_total_cpu_s"}:
        return f"{value:,.2f}"
    if metric == "peak_memory_kb":
        return f"{value:,.1f}"
    if metric == "artifact_size_bytes":
        return f"{int(value):,}"
    return str(value)


def format_std(metric, row):
    if metric == "simulation_speed":
        std = numeric(row.get("simulation_speed_std"))
        if std is not None:
            return f" ±{std:,.2f}"
    if metric == "peak_memory_kb":
        std = numeric(row.get("peak_memory_std_kb"))
        if std is not None:
            return f" ±{std:,.1f}"
    return ""


def display_variant(variant):
    return "cocotb" if variant == "verilator" else variant


def build_lookup(rows, group):
    lookup = {}
    for row in rows:
        if row["group"] != group:
            continue
        variant = row["variant"]
        if group == "A" and variant == "verilator":
            variant = "cocotb"
        lookup[(row["dut"], variant)] = row
    return lookup


def build_slots(rows, group):
    lookup = build_lookup(rows, group)
    variants = GROUP_A_VARIANTS if group == "A" else GROUP_B_VARIANTS

    slots = []
    positions = []
    group_bounds = []
    x = 0.0
    group_gap = 0.9

    for dut in DUT_ORDER:
        start = x
        for variant in variants:
            slots.append((dut, variant, lookup.get((dut, variant))))
            positions.append(x)
            x += 1.0
        end = x - 1.0
        group_bounds.append((dut, start, end))
        x += group_gap

    return slots, positions, group_bounds


def normalized_values(slots, metric):
    raw_values = [numeric(row.get(metric)) if row else None for _, _, row in slots]
    dut_max = {}
    for dut in DUT_ORDER:
        values = [value for slot_dut, _, row in slots if slot_dut == dut for value in [numeric(row.get(metric)) if row else None] if value is not None]
        dut_max[dut] = max(values) if values else None

    scaled = []
    for (dut, _, _), value in zip(slots, raw_values):
        local_max = dut_max[dut]
        if value is None or local_max in {None, 0}:
            scaled.append(0.0)
        else:
            scaled.append(value / local_max)
    return raw_values, scaled


def plot_metric_on_axis(ax, slots, positions, group_bounds, metric, title):
    raw_values, scaled_values = normalized_values(slots, metric)
    present = [value for value in raw_values if value is not None]
    if not present:
        ax.set_visible(False)
        return False

    for index, (dut, start, end) in enumerate(group_bounds):
        if index % 2 == 0:
            ax.axvspan(start - 0.5, end + 0.5, color="#f5f5f5", zorder=0)
        center = (start + end) / 2.0
        ax.text(center, -0.18, dut, transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=10, fontweight="bold")

    for x, (dut, variant, row), raw_value, scaled in zip(positions, slots, raw_values, scaled_values):
        shown_variant = display_variant(variant)
        if row is None or raw_value is None:
            ax.bar(x, 0.0, width=0.78, color="#d9d9d9", edgecolor="#7f7f7f", hatch="//", linewidth=1.0, zorder=3)
            ax.text(x, 0.02, "-", ha="center", va="bottom", fontsize=6, color="#555555")
            continue

        color = VARIANT_COLORS.get(shown_variant, "#4C78A8")
        ax.bar(x, scaled, width=0.78, color=color, edgecolor="white", linewidth=0.8, zorder=3)
        label = f"{format_value(metric, raw_value)}{format_std(metric, row)}"
        ax.text(x, min(scaled + 0.025, 1.11), label, ha="center", va="bottom", fontsize=6)

    ax.set_xticks(positions)
    ax.set_xticklabels([display_variant(variant) for _, variant, _ in slots], rotation=32, ha="right", fontsize=8)
    ax.set_ylim(0, 1.16)
    ax.set_ylabel("Normalized within DUT")
    ax.grid(axis="y", linestyle="--", alpha=0.25, zorder=1)
    ax.set_axisbelow(True)

    global_max = max(present)
    note = f"Global max: {format_value(metric, global_max)}\nBars are normalized within each DUT group"
    ax.set_title(f"{title}\n{note}", fontsize=10, pad=10)
    return True


def render_group_figure(rows, group, output_dir):
    slots, positions, group_bounds = build_slots(rows, group)
    metrics = GROUP_METRICS[group]
    n_metrics = len(metrics)
    if group == "A":
        nrows, ncols = 2, 2
        figsize = (18, 12)
    else:
        nrows, ncols = 1, 2
        figsize = (18, 6)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    axes = list(axes.flat) if hasattr(axes, "flat") else [axes]

    plotted = 0
    for ax, (metric, title) in zip(axes, metrics):
        if plot_metric_on_axis(ax, slots, positions, group_bounds, metric, title):
            plotted += 1

    for ax in axes[n_metrics:]:
        ax.set_visible(False)

    if plotted == 0:
        plt.close(fig)
        return None

    legend_variants = GROUP_A_VARIANTS if group == "A" else GROUP_B_VARIANTS
    legend_handles = [Patch(facecolor=VARIANT_COLORS.get(variant, "#4C78A8"), edgecolor="none", label=variant) for variant in legend_variants]
    fig.legend(handles=legend_handles, loc="upper center", bbox_to_anchor=(0.5, 0.98), ncol=len(legend_handles), frameon=False)
    fig.suptitle(f"Group {group} Metrics Overview", fontsize=18, y=0.995)
    fig.subplots_adjust(left=0.06, right=0.99, bottom=0.13, top=0.82, wspace=0.12, hspace=0.46)

    output_path = output_dir / f"group_{group.lower()}_overview.png"
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path


def main():
    args = parse_args()
    rows = load_rows(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    groups = [args.group] if args.group else ["A", "B"]
    written = []
    for group in groups:
        path = render_group_figure(rows, group, output_dir)
        if path is not None:
            written.append(path)

    for path in written:
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
