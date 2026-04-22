import csv
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
MATRIX_CSV = SCRIPTS_DIR / "experiment_matrix.csv"


def load_matrix():
    with MATRIX_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def select_cases(rows, group=None, case_ids=None):
    selected = []
    case_id_set = set(case_ids or [])
    for row in rows:
        if group and row["group"] != group:
            continue
        if case_id_set and row["case_id"] not in case_id_set:
            continue
        selected.append(row)
    return selected


def phase_command(row, phase):
    if phase == "generate":
        command = row["generate_entry"]
        return None if command == "N/A" else command
    if phase == "build":
        if row["flow"] == "cocotb":
            return f"make -C {row['canonical_dir']} sim_build/Vtop"
        return row["build_entry"]
    if phase == "run":
        if row["flow"] == "cocotb":
            return f"make -C {row['canonical_dir']} results.xml"
        return row["run_entry"]
    raise ValueError(f"unsupported phase: {phase}")


def case_output_dir(output_root, case_id):
    return Path(output_root) / case_id


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


_TIME_SUMMARY_RE = re.compile(
    r"(?P<user>\d+(?:\.\d+)?)user\s+"
    r"(?P<system>\d+(?:\.\d+)?)system\s+"
    r"(?P<elapsed>\d+:\d+(?::\d+(?:\.\d+)?)?(?:\.\d+)?)elapsed"
)
_VERBOSE_USER_RE = re.compile(r"User time \(seconds\):\s*(?P<value>\d+(?:\.\d+)?)")
_VERBOSE_SYSTEM_RE = re.compile(r"System time \(seconds\):\s*(?P<value>\d+(?:\.\d+)?)")
_VERBOSE_ELAPSED_RE = re.compile(
    r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s*(?P<value>\d+:\d+(?::\d+(?:\.\d+)?)?)"
)
_RSS_RE = re.compile(r"Maximum resident set size \(kbytes\):\s*(?P<rss>\d+)")


def parse_elapsed_to_seconds(value):
    parts = value.split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    raise ValueError(f"unsupported elapsed value: {value}")


def _make_time_entry(user_s, system_s, elapsed_value):
    elapsed_s = parse_elapsed_to_seconds(elapsed_value)
    return {
        "user_s": user_s,
        "system_s": system_s,
        "cpu_s": user_s + system_s,
        "elapsed_s": elapsed_s,
    }


def _extract_summary_time_entries(text):
    entries = []
    for match in _TIME_SUMMARY_RE.finditer(text):
        entries.append(
            _make_time_entry(
                float(match.group("user")),
                float(match.group("system")),
                match.group("elapsed"),
            )
        )
    return entries


def _extract_verbose_time_entries(text):
    entries = []
    user_s = None
    system_s = None
    for line in text.splitlines():
        match = _VERBOSE_USER_RE.search(line)
        if match:
            user_s = float(match.group("value"))
            continue

        match = _VERBOSE_SYSTEM_RE.search(line)
        if match:
            system_s = float(match.group("value"))
            continue

        match = _VERBOSE_ELAPSED_RE.search(line)
        if match and user_s is not None and system_s is not None:
            entries.append(_make_time_entry(user_s, system_s, match.group("value")))
            user_s = None
            system_s = None
    return entries


def extract_last_elapsed_seconds(text):
    entries = extract_all_time_entries(text)
    if not entries:
        return None
    return entries[-1]["elapsed_s"]


def extract_all_time_entries(text):
    summary_entries = _extract_summary_time_entries(text)
    if summary_entries:
        return summary_entries
    return _extract_verbose_time_entries(text)


def extract_all_elapsed_seconds(text):
    return [entry["elapsed_s"] for entry in extract_all_time_entries(text)]


def extract_max_rss_kb(text):
    matches = list(_RSS_RE.finditer(text))
    if not matches:
        return None
    return int(matches[-1].group("rss"))


def runtime_dir_for_artifact(row):
    canonical = REPO_ROOT / row["canonical_dir"]
    if row["flow"] == "cocotb":
        return canonical / "sim_build"
    if row["group"] == "A" and row["flow"] == "picker":
        mapping = {
            "python-dpi": "dpi_python",
            "python-vpi": "vpi_python",
            "python-mem_direct": "mem_python",
        }
        return canonical / mapping[row["variant"]]
    return canonical


def artifact_size_bytes(row):
    runtime_dir = runtime_dir_for_artifact(row)
    if not runtime_dir.exists():
        return None

    if row["flow"] == "cocotb":
        artifact = runtime_dir / "Vtop"
        return artifact.stat().st_size if artifact.exists() else None

    patterns = []
    if row["group"] == "A" and row["variant"] == "python-mem_direct":
        patterns = [".so", ".yaml"]
    elif row["group"] == "A":
        patterns = [".so"]
    elif row["variant"] == "python":
        patterns = [".so"]
    elif row["variant"] == "cpp":
        patterns = [".so"]
    elif row["variant"] == "java":
        patterns = [".so", ".jar"]
    elif row["variant"] == "golang":
        patterns = [".so"]
    elif row["variant"] == "raw-verilator":
        patterns = [".so"]

    total = 0
    for path in runtime_dir.rglob("*"):
        if not path.is_file():
            continue
        if "build" in path.parts or "sim_build" in path.parts or "__pycache__" in path.parts:
            continue
        name = path.name
        if row["variant"] in {"cpp", "raw-verilator"} and "example" in name:
            total += path.stat().st_size
            continue
        if any(name.endswith(suffix) for suffix in patterns):
            total += path.stat().st_size
    return total or None
