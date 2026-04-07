#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

OUTPUT_DIR="results/extracted/group_a"

need_picker_build() {
  local dut="$1"
  [[ ! -f "${dut}/dpi_python/example.py" || ! -f "${dut}/mem_python/example.py" || ! -f "${dut}/vpi_python/example.py" ]]
}

need_cocotb_build() {
  local dut="$1"
  [[ ! -f "${dut}/cocotb/sim_build/Vtop" ]]
}

run_group_a_dut() {
  local dut="$1"
  local picker_root="$2"

  echo "[Group A] ${dut}: picker"
  if need_picker_build "${picker_root}"; then
    echo "  missing picker artifacts, running build_time.sh"
    bash "${dut}/picker/build_time.sh"
  fi
  bash "${dut}/picker/run_time.sh"

  echo "[Group A] ${dut}: cocotb"
  if need_cocotb_build "${dut}"; then
    echo "  missing cocotb sim_build/Vtop, running build_time.sh"
    bash "${dut}/cocotb/build_time.sh"
  fi
  bash "${dut}/cocotb/run_time.sh"
}

run_group_a_dut "rocket" "rocket/picker"
run_group_a_dut "coupledL2" "coupledL2/picker"

python3 scripts/extract_metrics.py \
  --group A \
  --output-dir "${OUTPUT_DIR}"

python3 scripts/plot_metrics_cli.py \
  --input "${OUTPUT_DIR}/metrics.csv" \
  --group A | tee "${OUTPUT_DIR}/group_a_cli_plot.txt"

echo "wrote ${OUTPUT_DIR}"
