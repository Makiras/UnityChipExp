#!/usr/bin/env python3
import argparse
import csv
import json
import re
import statistics
from pathlib import Path
from xml.etree import ElementTree

from _common import (
    REPO_ROOT,
    artifact_size_bytes,
    case_output_dir,
    extract_all_time_entries,
    extract_max_rss_kb,
    load_matrix,
    select_cases,
)


BENCH_SPEED_RE = re.compile(r"bench_speed_cycles_per_s=(?P<value>[0-9.]+)")
LEGACY_SPEED_RE = re.compile(r"speed:\s*(?P<value>[0-9.]+)\s*c/s")
BENCH_ELAPSED_RE = re.compile(r"bench_elapsed_ms=(?P<value>[0-9.]+)")


def cocotb_results_xml_path(row, raw_root):
    case_dir = case_output_dir(raw_root, row["case_id"])
    results_xml = case_dir / "results.xml"
    if results_xml.exists():
        return results_xml
    fallback = REPO_ROOT / row["canonical_dir"] / "results.xml"
    return fallback if fallback.exists() else None


def parse_runtime_speed(row, raw_root):
    if row["flow"] == "cocotb":
        run_log = resolve_phase_log(row, raw_root, "run")
        run_text = read_log(run_log)
        build_text = read_log(resolve_phase_log(row, raw_root, "build"))
        speed_text = run_text or build_text
        source_prefix = "run.log" if run_text else "build.log"
        match = BENCH_SPEED_RE.search(speed_text)
        if match:
            return float(match.group("value")), "cycles_per_s", f"{source_prefix}:bench_speed_cycles_per_s"
        match = LEGACY_SPEED_RE.search(speed_text)
        if match:
            return float(match.group("value")), "cycles_per_s", f"{source_prefix}:legacy_speed"
        match = BENCH_ELAPSED_RE.search(speed_text)
        if match:
            elapsed_ms = float(match.group("value"))
            steps_match = re.search(r"bench_steps=(?P<value>\d+)", speed_text)
            if elapsed_ms > 0 and steps_match:
                steps = float(steps_match.group("value"))
                return steps * 1000.0 / elapsed_ms, "cycles_per_s", f"{source_prefix}:bench_elapsed_ms"
        results_xml = cocotb_results_xml_path(row, raw_root)
        if results_xml is None:
            return None, None, None
        root = ElementTree.fromstring(results_xml.read_text(encoding="utf-8"))
        testcase = root.find(".//testcase")
        if testcase is None:
            return None, None, None
        ratio = testcase.attrib.get("ratio_time")
        return (float(ratio), "ns_per_s", "results.xml:ratio_time") if ratio else (None, None, None)

    run_logs = resolve_run_logs(row, raw_root)
    if not run_logs:
        return None, None, None

    text = run_logs[0].read_text(encoding="utf-8", errors="replace")
    match = BENCH_SPEED_RE.search(text)
    if match:
        return float(match.group("value")), "cycles_per_s", "run.log:bench_speed_cycles_per_s"
    match = LEGACY_SPEED_RE.search(text)
    if match:
        return float(match.group("value")), "cycles_per_s", "run.log:legacy_speed"
    match = BENCH_ELAPSED_RE.search(text)
    if match:
        elapsed_ms = float(match.group("value"))
        if elapsed_ms > 0:
            return 5000.0 * 1000.0 / elapsed_ms, "cycles_per_s", "run.log:bench_elapsed_ms"
    return None, None, None


def read_log(path):
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def fallback_repo_log(row, phase):
    def first_existing(*paths):
        for path in paths:
            if path.exists():
                return path
        return None

    if row["group"] == "A" and row["flow"] == "picker":
        root = REPO_ROOT / row["canonical_dir"]
        variant = row["variant"]
        if root == REPO_ROOT / "XS":
            suffix = {
                "python-dpi": ("python-dpi_codegen_time.txt", "python-dpi_build_time.txt", "python-dpi_run.log"),
                "python-vpi": ("python-vpi_codegen_time.txt", "python-vpi_build_time.txt", "python-vpi_run.log"),
                "python-mem_direct": ("python-mem_codegen_time.txt", "python-mem_build_time.txt", "python-mem_run.log"),
            }[variant]
        elif root == REPO_ROOT / "rocket" / "picker":
            suffix = {
                "python-dpi": ("python-dpi_codegen_roc.txt", "python-dpi_build_roc.txt", "python-dpi_run.log"),
                "python-vpi": ("python-vpi_codegen_roc.txt", "python-vpi_build_roc.txt", "python-vpi_run.log"),
                "python-mem_direct": ("python-mem_codegen_roc.txt", "python-mem_build_roc.txt", "python-mem_run.log"),
            }[variant]
        else:
            suffix = {
                "python-dpi": ("python-dpi_codegen_time.txt", "python-dpi_build_time.txt", "python-dpi_run.log"),
                "python-vpi": ("python-vpi_codegen_time.txt", "python-vpi_build_time.txt", "python-vpi_run.log"),
                "python-mem_direct": ("python-mem_codegen_time.txt", "python-mem_build_time.txt", "python-mem_run.log"),
            }[variant]
        if phase == "generate":
            name = suffix[0]
        elif phase == "build":
            name = suffix[1]
        elif phase == "run":
            name = suffix[2]
        else:
            return None
        return first_existing(root / "logs" / name, root / name)

    if row["group"] == "A" and row["flow"] == "cocotb":
        root = REPO_ROOT / row["canonical_dir"]
        if phase == "build":
            for name in ("build.log", "build_log"):
                path = first_existing(root / "logs" / name, root / name)
                if path:
                    return path
        if phase == "run":
            for name in ("run.log",):
                path = first_existing(root / "logs" / name, root / name)
                if path:
                    return path
        return None

    if row["group"] == "B":
        multilang_root = (REPO_ROOT / row["canonical_dir"]).parents[1]
        variant = "cpp" if row["variant"] == "raw-verilator" else row["variant"]
        if phase == "generate":
            name = f"{variant}-dpi_codegen_roc.txt"
            return first_existing(multilang_root / "logs" / name, multilang_root / name)
        if phase == "build":
            name = f"{variant}-dpi_build_ml.txt"
            return first_existing(multilang_root / "logs" / name, multilang_root / name)
        if phase == "run":
            name = f"{row['variant']}_run.log"
            return first_existing(multilang_root / "logs" / name, multilang_root / name)
    return None


def _sorted_log_paths(paths):
    def key(path):
        match = re.search(r"_(\d+)\.log$", path.name)
        return int(match.group(1)) if match else -1

    return sorted(paths, key=key)


def resolve_run_logs(row, raw_root):
    case_dir = case_output_dir(raw_root, row["case_id"])
    numbered = _sorted_log_paths(case_dir.glob("run_*.log"))
    if numbered:
        return numbered

    fallback = resolve_phase_log(row, raw_root, "run")
    if fallback.exists():
        prefix = fallback.stem
        numbered_fallback = _sorted_log_paths(fallback.parent.glob(f"{prefix}_*.log"))
        if numbered_fallback:
            return numbered_fallback
        return [fallback]
    return []


def trim_extremes(values):
    if len(values) < 7:
        return values
    ordered = sorted(values)
    return ordered[1:-1]


def parse_single_run_metrics(text):
    speed = None
    speed_unit = None
    speed_source = None
    match = BENCH_SPEED_RE.search(text)
    if match:
        speed = float(match.group("value"))
        speed_unit = "cycles_per_s"
        speed_source = "bench_speed_cycles_per_s"
    else:
        match = LEGACY_SPEED_RE.search(text)
        if match:
            speed = float(match.group("value"))
            speed_unit = "cycles_per_s"
            speed_source = "legacy_speed"
        else:
            match = BENCH_ELAPSED_RE.search(text)
            if match:
                elapsed_ms = float(match.group("value"))
                steps_match = re.search(r"bench_steps=(?P<value>\d+)", text)
                if elapsed_ms > 0 and steps_match:
                    speed = float(steps_match.group("value")) * 1000.0 / elapsed_ms
                    speed_unit = "cycles_per_s"
                    speed_source = "bench_elapsed_ms"
    rss_kb = extract_max_rss_kb(text)
    return speed, speed_unit, speed_source, rss_kb


def parse_runtime_metrics(row, raw_root):
    if row["flow"] == "cocotb":
        run_logs = resolve_run_logs(row, raw_root)
        speed_values = []
        speed_unit = None
        speed_source = None
        rss_values = []
        for log in run_logs:
            text = read_log(log)
            speed, unit, source, rss_kb = parse_single_run_metrics(text)
            if speed is not None:
                speed_values.append(speed)
                speed_unit = unit
                speed_source = source
            if rss_kb is not None:
                rss_values.append(rss_kb)

        trimmed_speed_values = trim_extremes(speed_values)
        trimmed_rss_values = trim_extremes(rss_values)

        if trimmed_speed_values or trimmed_rss_values:
            return {
                "simulation_speed": statistics.mean(trimmed_speed_values) if trimmed_speed_values else None,
                "simulation_speed_std": statistics.pstdev(trimmed_speed_values) if len(trimmed_speed_values) >= 2 else None,
                "simulation_speed_unit": speed_unit,
                "simulation_speed_source": speed_source,
                "simulation_speed_sample_count": len(trimmed_speed_values),
                "peak_memory_kb": statistics.mean(trimmed_rss_values) if trimmed_rss_values else None,
                "peak_memory_std_kb": statistics.pstdev(trimmed_rss_values) if len(trimmed_rss_values) >= 2 else None,
                "peak_memory_sample_count": len(trimmed_rss_values),
                "run_log_count": len(run_logs),
                "run_logs": [str(path) for path in run_logs if path.exists()],
            }

        speed, unit, source = parse_runtime_speed(row, raw_root)
        run_log = resolve_phase_log(row, raw_root, "run")
        rss_values = [extract_max_rss_kb(read_log(run_log))] if run_log.exists() else []
        rss_values = [value for value in rss_values if value is not None]
        return {
            "simulation_speed": speed,
            "simulation_speed_std": None,
            "simulation_speed_unit": unit,
            "simulation_speed_source": source,
            "simulation_speed_sample_count": 1 if speed is not None else 0,
            "peak_memory_kb": rss_values[0] if rss_values else None,
            "peak_memory_std_kb": None,
            "peak_memory_sample_count": len(rss_values),
            "run_log_count": len(run_logs),
            "run_logs": [str(path) for path in run_logs if path.exists()],
        }

    run_logs = resolve_run_logs(row, raw_root)
    speed_values = []
    speed_unit = None
    speed_source = None
    rss_values = []
    for log in run_logs:
        text = read_log(log)
        speed, unit, source, rss_kb = parse_single_run_metrics(text)
        if speed is not None:
            speed_values.append(speed)
            speed_unit = unit
            speed_source = source
        if rss_kb is not None:
            rss_values.append(rss_kb)

    trimmed_speed_values = trim_extremes(speed_values)
    trimmed_rss_values = trim_extremes(rss_values)

    return {
        "simulation_speed": statistics.mean(trimmed_speed_values) if trimmed_speed_values else None,
        "simulation_speed_std": statistics.pstdev(trimmed_speed_values) if len(trimmed_speed_values) >= 2 else None,
        "simulation_speed_unit": speed_unit,
        "simulation_speed_source": speed_source,
        "simulation_speed_sample_count": len(trimmed_speed_values),
        "peak_memory_kb": statistics.mean(trimmed_rss_values) if trimmed_rss_values else None,
        "peak_memory_std_kb": statistics.pstdev(trimmed_rss_values) if len(trimmed_rss_values) >= 2 else None,
        "peak_memory_sample_count": len(trimmed_rss_values),
        "run_log_count": len(run_logs),
        "run_logs": [str(path) for path in run_logs if path.exists()],
    }


def resolve_phase_log(row, raw_root, phase):
    case_dir = case_output_dir(raw_root, row["case_id"])
    raw_path = case_dir / f"{phase}.log"
    if raw_path.exists():
        return raw_path
    fallback = fallback_repo_log(row, phase)
    if fallback and fallback.exists():
        return fallback
    return raw_path


def parse_build_metrics(row, build_entries):
    if row["flow"] == "cocotb":
        if build_entries:
            return sum(entry["cpu_s"] for entry in build_entries), "sum_cocotb_cpu_phases"
        return None, None

    if not build_entries:
        return None, None
    return build_entries[-1]["cpu_s"], "outer_cpu_total"


def collect_quality_notes(row, build_log, build_text, raw_root):
    notes = []
    if row["flow"] != "cocotb":
        return notes

    if "No tests were discovered" in build_text:
        notes.append("build_log_reports_no_tests")

    results_xml = cocotb_results_xml_path(row, raw_root)
    if build_log.exists() and results_xml and build_log.resolve() != results_xml.resolve():
        delta_s = abs(build_log.stat().st_mtime - results_xml.stat().st_mtime)
        if delta_s > 24 * 3600:
            notes.append("build_log_and_results_xml_mtime_mismatch_gt_24h")
    return notes


def build_row(row, raw_root):
    generate_log = resolve_phase_log(row, raw_root, "generate")
    build_log = resolve_phase_log(row, raw_root, "build")
    run_log = resolve_phase_log(row, raw_root, "run")
    generate_text = read_log(generate_log)
    build_text = read_log(build_log)
    generate_entries = extract_all_time_entries(generate_text)
    build_entries = extract_all_time_entries(build_text)
    build_total_s, build_total_source = parse_build_metrics(row, build_entries)

    runtime_metrics = parse_runtime_metrics(row, raw_root)
    quality_notes = collect_quality_notes(row, build_log, build_text, raw_root)

    return {
        "case_id": row["case_id"],
        "group": row["group"],
        "dut": row["dut"],
        "flow": row["flow"],
        "variant": row["variant"],
        "codegen_total_s": generate_entries[-1]["cpu_s"] if generate_entries else None,
        "codegen_total_cpu_s": generate_entries[-1]["cpu_s"] if generate_entries else None,
        "codegen_total_source": "outer_cpu_total" if generate_entries else None,
        "codegen_elapsed_count": len(generate_entries),
        "codegen_outer_elapsed_s": generate_entries[-1]["elapsed_s"] if generate_entries else None,
        "build_total_s": build_total_s,
        "build_total_cpu_s": build_total_s,
        "build_total_source": build_total_source,
        "build_elapsed_count": len(build_entries),
        "build_inner_phase_1_s": build_entries[0]["cpu_s"] if len(build_entries) >= 2 else None,
        "build_inner_phase_2_s": build_entries[1]["cpu_s"] if len(build_entries) >= 3 else None,
        "build_inner_phase_1_cpu_s": build_entries[0]["cpu_s"] if len(build_entries) >= 2 else None,
        "build_inner_phase_2_cpu_s": build_entries[1]["cpu_s"] if len(build_entries) >= 3 else None,
        "build_inner_phase_1_elapsed_s": build_entries[0]["elapsed_s"] if len(build_entries) >= 2 else None,
        "build_inner_phase_2_elapsed_s": build_entries[1]["elapsed_s"] if len(build_entries) >= 3 else None,
        "build_outer_total_s": build_entries[-1]["cpu_s"] if build_entries else None,
        "build_outer_total_cpu_s": build_entries[-1]["cpu_s"] if build_entries else None,
        "build_outer_elapsed_s": build_entries[-1]["elapsed_s"] if build_entries else None,
        "simulation_speed": runtime_metrics["simulation_speed"],
        "simulation_speed_std": runtime_metrics["simulation_speed_std"],
        "simulation_speed_unit": runtime_metrics["simulation_speed_unit"],
        "simulation_speed_source": runtime_metrics["simulation_speed_source"],
        "simulation_speed_sample_count": runtime_metrics["simulation_speed_sample_count"],
        "peak_memory_kb": runtime_metrics["peak_memory_kb"],
        "peak_memory_std_kb": runtime_metrics["peak_memory_std_kb"],
        "peak_memory_sample_count": runtime_metrics["peak_memory_sample_count"],
        "run_log_count": runtime_metrics["run_log_count"],
        "artifact_size_bytes": artifact_size_bytes(row),
        "data_quality_notes": ";".join(quality_notes),
        "generate_log": str(generate_log) if generate_log.exists() else "",
        "build_log": str(build_log) if build_log.exists() else "",
        "run_log": str(run_log) if run_log.exists() else "",
        "run_logs": ";".join(runtime_metrics["run_logs"]),
    }


def main():
    parser = argparse.ArgumentParser(description="Extract metrics from raw logs and runtime artifacts.")
    parser.add_argument("--group", choices=["A", "B"])
    parser.add_argument("--case", action="append", dest="cases")
    parser.add_argument("--raw-root", default=str(REPO_ROOT / "results" / "raw"))
    parser.add_argument("--output-dir", default=str(REPO_ROOT / "results" / "extracted"))
    args = parser.parse_args()

    rows = load_matrix()
    selected = select_cases(rows, group=args.group, case_ids=args.cases)
    if not selected:
        raise SystemExit("no cases selected")

    extracted = [build_row(row, Path(args.raw_root)) for row in selected]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "metrics.csv"
    json_path = output_dir / "metrics.json"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(extracted[0].keys()))
        writer.writeheader()
        writer.writerows(extracted)
    json_path.write_text(json.dumps(extracted, indent=2), encoding="utf-8")
    print(f"wrote {csv_path}")
    print(f"wrote {json_path}")


if __name__ == "__main__":
    main()
