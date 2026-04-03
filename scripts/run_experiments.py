#!/usr/bin/env python3
import argparse
import os
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from _common import REPO_ROOT, case_output_dir, load_matrix, phase_command, select_cases, write_json


def inject_make_vars(command, make_vars):
    if not make_vars:
        return command
    parts = shlex.split(command)
    if not parts or parts[0] != "make":
        return command
    return shlex.join([parts[0], *make_vars, *parts[1:]])


def parse_key_value(items):
    parsed = {}
    for item in items or []:
        if "=" not in item:
            raise SystemExit(f"expected KEY=VALUE, got: {item}")
        key, value = item.split("=", 1)
        parsed[key] = value
    return parsed


def run_phase(row, phase, output_root, force=False, dry_run=False, make_vars=None, extra_env=None):
    command = phase_command(row, phase)
    if command is None:
        return {"phase": phase, "status": "skipped", "reason": "N/A"}
    command = inject_make_vars(command, make_vars)

    out_dir = case_output_dir(output_root, row["case_id"])
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / f"{phase}.log"

    if log_path.exists() and not force:
        return {"phase": phase, "status": "skipped", "reason": "log exists", "log": str(log_path)}

    wrapped = ["/usr/bin/time", "-v", "bash", "-lc", command]
    if dry_run:
        return {
            "phase": phase,
            "status": "dry-run",
            "command": shlex.join(wrapped),
            "log": str(log_path),
        }

    started = datetime.now(timezone.utc).isoformat()
    env = os.environ.copy()
    env.update(extra_env or {})
    with log_path.open("w", encoding="utf-8") as log_file:
        log_file.write(f"$ {command}\n\n")
        completed = subprocess.run(
            wrapped,
            cwd=REPO_ROOT,
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    ended = datetime.now(timezone.utc).isoformat()
    return {
        "phase": phase,
        "status": "ok" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "started_at_utc": started,
        "ended_at_utc": ended,
        "command": command,
        "log": str(log_path),
    }


def main():
    parser = argparse.ArgumentParser(description="Run experiment phases and save raw logs.")
    parser.add_argument("--group", choices=["A", "B"])
    parser.add_argument("--case", action="append", dest="cases", help="repeatable case id filter")
    parser.add_argument(
        "--phases",
        nargs="+",
        choices=["generate", "build", "run"],
        default=["generate", "build", "run"],
    )
    parser.add_argument("--output-root", default=str(REPO_ROOT / "results" / "raw"))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--make-var", action="append", dest="make_vars", help="repeatable KEY=VALUE injected into make commands")
    parser.add_argument("--env", action="append", dest="env_vars", help="repeatable KEY=VALUE added to subprocess environment")
    args = parser.parse_args()

    rows = load_matrix()
    selected = select_cases(rows, group=args.group, case_ids=args.cases)
    if not selected:
        raise SystemExit("no cases selected")
    make_vars = args.make_vars or []
    extra_env = parse_key_value(args.env_vars)

    for row in selected:
        results = []
        for phase in args.phases:
            result = run_phase(
                row,
                phase,
                args.output_root,
                force=args.force,
                dry_run=args.dry_run,
                make_vars=make_vars,
                extra_env=extra_env,
            )
            results.append(result)
            if result["status"] == "failed":
                break
        metadata = {
            "case_id": row["case_id"],
            "group": row["group"],
            "dut": row["dut"],
            "flow": row["flow"],
            "variant": row["variant"],
            "canonical_dir": row["canonical_dir"],
            "phases": results,
        }
        write_json(case_output_dir(args.output_root, row["case_id"]) / "metadata.json", metadata)
        summary = ", ".join(f"{result['phase']}={result['status']}" for result in results)
        print(f"{row['case_id']}: {summary}")


if __name__ == "__main__":
    main()
