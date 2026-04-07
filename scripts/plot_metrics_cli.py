#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path

from _common import REPO_ROOT


def default_input_path():
    extracted_root = REPO_ROOT / "results" / "extracted"
    preferred = sorted(extracted_root.glob("final_all_latest_*/metrics.csv"))
    if preferred:
        return preferred[-1]
    fallback = sorted(extracted_root.glob("final_all*/metrics.csv"))
    if fallback:
        return fallback[-1]
    return extracted_root / "final_all_latest" / "metrics.csv"

DUT_ORDER = ["XS", "coupledL2", "rocket"]
GROUP_A_VARIANTS = ["python-dpi", "python-mem_direct", "python-vpi", "cocotb"]
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


def parse_args():
    parser = argparse.ArgumentParser(description="Render fixed grouped terminal bar charts for experiment metrics.")
    parser.add_argument("--input", default=str(default_input_path()), help="metrics.csv path")
    parser.add_argument("--group", choices=["A", "B"], required=True, help="experiment group to render")
    parser.add_argument("--height", type=int, default=10, help="chart height in rows")
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


def render_chart(rows_by_slot, metric, title, height):
    values = [numeric(row.get(metric)) if row else None for _, _, row in rows_by_slot]
    present = [v for v in values if v is not None]
    print(f"{title} [{metric}]")
    if not present:
        print("no matching rows\n")
        return

    max_value = max(present)
    scaled = []
    for dut in DUT_ORDER:
        dut_indices = [i for i, (slot_dut, _, _) in enumerate(rows_by_slot) if slot_dut == dut]
        dut_values = [values[i] for i in dut_indices if values[i] is not None]
        dut_max = max(dut_values) if dut_values else None
        for i in dut_indices:
            value = values[i]
            if value is None or not dut_max or dut_max == 0:
                scaled.append(0)
            else:
                scaled.append(max(1, round((value / dut_max) * height)))

    print(f"global max: {format_value(metric, max_value)}")
    print("bars are normalized within each DUT group")
    print()

    for level in range(height, 0, -1):
        line = []
        for bar_h in scaled:
            line.append("###" if bar_h >= level else "   ")
        print(" ".join(line))

    print("---" * len(rows_by_slot) + "-" * max(0, len(rows_by_slot) - 1))
    print(" ".join(f"{i+1:>3}" for i in range(len(rows_by_slot))))
    print()

    idx = 1
    for dut in DUT_ORDER:
        print(f"{dut}:")
        dut_rows = [(variant, row) for slot_dut, variant, row in rows_by_slot if slot_dut == dut]
        for variant, row in dut_rows:
            shown_variant = display_variant(variant)
            if row is None:
                print(f" {idx:>2}. {shown_variant:<16} = -")
            else:
                value = numeric(row.get(metric))
                print(f" {idx:>2}. {shown_variant:<16} = {format_value(metric, value)}{format_std(metric, row)}")
            idx += 1
        print()


def main():
    args = parse_args()
    rows = load_rows(args.input)
    lookup = build_lookup(rows, args.group)
    variants = GROUP_A_VARIANTS if args.group == "A" else GROUP_B_VARIANTS

    slots = []
    for dut in DUT_ORDER:
        for variant in variants:
            slots.append((dut, variant, lookup.get((dut, variant))))

    for metric, title in GROUP_METRICS[args.group]:
        render_chart(slots, metric, title, args.height)


if __name__ == "__main__":
    main()
