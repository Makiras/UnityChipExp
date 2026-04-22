#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

OUTPUT_DIR="results/extracted/group_a_with_xs"
PLOT_DIR="results/plots/group_a_with_xs"
OVERVIEW_PNG="${PLOT_DIR}/group_a_overview.png"

need_picker_build() {
  local dut="$1"
  [[ ! -f "${dut}/dpi_python/example.py" || ! -f "${dut}/mem_python/example.py" || ! -f "${dut}/vpi_python/example.py" ]]
}

need_cocotb_build() {
  local dut="$1"
  [[ ! -f "${dut}/cocotb/sim_build/Vtop" ]]
}

run_group_a_picker_dut() {
  local dut="$1"
  local picker_root="$2"

  echo "[Group A] ${dut}: picker"
  if need_picker_build "${picker_root}"; then
    echo "  missing picker artifacts, running build_time.sh"
    bash "${dut}/build_time.sh"
  fi
  bash "${dut}/run_time.sh"
}

run_group_a_cocotb_dut() {
  local dut="$1"

  echo "[Group A] ${dut}: cocotb"
  if need_cocotb_build "${dut}"; then
    echo "  missing cocotb sim_build/Vtop, running build_time.sh"
    bash "${dut}/cocotb/build_time.sh"
  fi
  bash "${dut}/cocotb/run_time.sh"
}

run_group_a_picker_dut "rocket/picker" "rocket"
run_group_a_cocotb_dut "rocket"

run_group_a_picker_dut "coupledL2/picker" "coupledL2"
run_group_a_cocotb_dut "coupledL2"

run_group_a_picker_dut "XS" "XS"
run_group_a_cocotb_dut "XS"

python3 scripts/extract_metrics.py \
  --group A \
  --output-dir "${OUTPUT_DIR}"

python3 scripts/plot_metrics_cli.py \
  --input "${OUTPUT_DIR}/metrics.csv" \
  --group A | tee "${OUTPUT_DIR}/group_a_cli_plot.txt"

python3 scripts/plot_metrics.py \
  --input "${OUTPUT_DIR}/metrics.csv" \
  --group A \
  --output-dir "${PLOT_DIR}"

CONTAINER_REF="$(hostname)"
echo "wrote ${OUTPUT_DIR}"
echo "wrote ${OVERVIEW_PNG}"
echo "copy overview png from host:"
echo "  docker cp ${CONTAINER_REF}:/home/xyl/exp/${OVERVIEW_PNG} ./"
echo "copy extracted outputs from host:"
echo "  docker cp ${CONTAINER_REF}:/home/xyl/exp/${OUTPUT_DIR} ./$(basename "${OUTPUT_DIR}")"
echo "copy plot outputs from host:"
echo "  docker cp ${CONTAINER_REF}:/home/xyl/exp/${PLOT_DIR} ./$(basename "${PLOT_DIR}")"
