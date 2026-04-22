#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

OUTPUT_DIR="results/extracted/group_b_with_xs"
PLOT_DIR="results/plots/group_b_with_xs"
OVERVIEW_PNG="${PLOT_DIR}/group_b_overview.png"

need_multilang_build() {
  local dut="$1"
  [[ ! -d "${dut}/multilang/dpi_python" || ! -d "${dut}/multilang/dpi_cpp" || ! -d "${dut}/multilang/dpi_java" || ! -d "${dut}/multilang/dpi_golang" ]]
}

run_group_b_dut() {
  local dut="$1"

  echo "[Group B] ${dut}: multilang"
  if need_multilang_build "${dut}"; then
    echo "  missing multilang artifacts, running build_time.sh"
    bash "${dut}/multilang/build_time.sh"
  fi
  bash "${dut}/multilang/run_time.sh"
}

run_group_b_dut "rocket"
run_group_b_dut "coupledL2"
run_group_b_dut "XS"

python3 scripts/extract_metrics.py \
  --group B \
  --output-dir "${OUTPUT_DIR}"

python3 scripts/plot_metrics_cli.py \
  --input "${OUTPUT_DIR}/metrics.csv" \
  --group B | tee "${OUTPUT_DIR}/group_b_cli_plot.txt"

python3 scripts/plot_metrics.py \
  --input "${OUTPUT_DIR}/metrics.csv" \
  --group B \
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
