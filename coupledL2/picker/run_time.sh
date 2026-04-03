#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

LOG_DIR="${LOG_DIR:-logs}"
mkdir -p "${LOG_DIR}"

RUN_REPEATS="${RUN_REPEATS:-7}"
PIN_RUNTIME="${PIN_RUNTIME:-1}"
PIN_CPUS="${PIN_CPUS:-96-99}"

run_case() {
    local variant="$1"
    local workdir="$2"
    local base_name="$3"
    local cmd=(python3 example.py)

    python3 ../../scripts/install_benchmarks.py --mode picker --dut coupledL2 --root . --variant "${variant}"

    for i in $(seq 1 "${RUN_REPEATS}"); do
        local log_path="../${LOG_DIR}/${base_name}_run_${i}.log"
        if [[ "${PIN_RUNTIME}" == "1" ]]; then
            (
                cd "${workdir}"
                /usr/bin/time -v taskset -c "${PIN_CPUS}" "${cmd[@]}" > "${log_path}" 2>&1
            )
        else
            (
                cd "${workdir}"
                /usr/bin/time -v "${cmd[@]}" > "${log_path}" 2>&1
            )
        fi
    done

    cp "${LOG_DIR}/${base_name}_run_${RUN_REPEATS}.log" "${LOG_DIR}/${base_name}_run.log"
}

run_case "python-dpi" "dpi_python" "python-dpi"
run_case "python-mem_direct" "mem_python" "python-mem"
run_case "python-vpi" "vpi_python" "python-vpi"
