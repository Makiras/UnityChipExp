#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

LOG_DIR="${LOG_DIR:-logs}"
RUN_REPEATS="${RUN_REPEATS:-7}"
PIN_RUNTIME="${PIN_RUNTIME:-1}"
PIN_CPUS="${PIN_CPUS:-96}"
PIN_NUMA_NODE="${PIN_NUMA_NODE:-1}"
mkdir -p "${LOG_DIR}"

BENCH_ARGS=()
[[ -d dpi_python ]] && BENCH_ARGS+=(--variant python)
[[ -d dpi_cpp ]] && BENCH_ARGS+=(--variant cpp --variant raw-verilator)
[[ -d dpi_java ]] && BENCH_ARGS+=(--variant java)
[[ -d dpi_golang ]] && BENCH_ARGS+=(--variant golang)
if [[ ${#BENCH_ARGS[@]} -gt 0 ]]; then
  python3 ../../scripts/install_benchmarks.py --mode multilang --dut coupledL2 --root . "${BENCH_ARGS[@]}"
fi

write_skip_log() {
  local path="$1"
  local reason="$2"
  printf 'SKIPPED: %s\n' "${reason}" > "${path}"
}

clear_run_logs() {
  local prefix="$1"
  rm -f "${LOG_DIR}/${prefix}_run.log" "${LOG_DIR}/${prefix}_run_"*.log
}

copy_last_run_log() {
  local prefix="$1"
  local last_log="${LOG_DIR}/${prefix}_run_${RUN_REPEATS}.log"
  if [[ -f "${last_log}" ]]; then
    cp "${last_log}" "${LOG_DIR}/${prefix}_run.log"
  fi
}

run_pinned() {
  if [[ "${PIN_RUNTIME}" == "1" ]]; then
    taskset -c "${PIN_CPUS}" numactl --cpunodebind="${PIN_NUMA_NODE}" --membind="${PIN_NUMA_NODE}" "$@"
  else
    "$@"
  fi
}

run_repeats() {
  local prefix="$1"
  local workdir="$2"
  shift 2
  clear_run_logs "${prefix}"
  local i
  for i in $(seq 1 "${RUN_REPEATS}"); do
    ( cd "${workdir}" && run_pinned "$@" ) > "${LOG_DIR}/${prefix}_run_${i}.log" 2>&1 || true
  done
  copy_last_run_log "${prefix}"
}

ensure_release() {
  local rel_dir="$1"
  local expected_path="$2"
  local log_path="$3"
  if [[ -e "${expected_path}" ]]; then
    return 0
  fi
  if [[ -f "${rel_dir}/Makefile" ]]; then
    ( cd "${rel_dir}" && make ) > "${log_path}" 2>&1 || true
  fi
}

ensure_release "dpi_python" "dpi_python/UT_TestTop/Makefile" "${LOG_DIR}/python_bootstrap.log"
if [[ -f dpi_python/UT_TestTop/Makefile ]]; then
  ( cd dpi_python/UT_TestTop && make TARGET=UT_TestTop compile ) > "${LOG_DIR}/python_prepare.log" 2>&1 || true
  run_repeats python "dpi_python" env PYTHONPATH=.:/usr/local/share/picker/python/xspcomm/.. /usr/bin/time -v python3 -u example.py
else
  write_skip_log "${LOG_DIR}/python_bootstrap.log" "dpi_python/UT_TestTop/Makefile missing"
  write_skip_log "${LOG_DIR}/python_prepare.log" "dpi_python/UT_TestTop/Makefile missing"
  write_skip_log "${LOG_DIR}/python_run.log" "dpi_python/UT_TestTop/Makefile missing"
fi

ensure_release "dpi_cpp" "dpi_cpp/UT_TestTop/Makefile" "${LOG_DIR}/cpp_bootstrap.log"
if [[ -f dpi_cpp/UT_TestTop/Makefile ]]; then
  ( cd dpi_cpp/UT_TestTop && make copy_xspcomm && cmake . -Bbuild -DCMAKE_BUILD_TYPE=Release && cmake --build build --parallel "$(nproc)" ) > "${LOG_DIR}/cpp_prepare.log" 2>&1 || true
  run_repeats cpp "dpi_cpp/UT_TestTop" /usr/bin/time -v ./build/UTTestTop_example
else
  write_skip_log "${LOG_DIR}/cpp_bootstrap.log" "dpi_cpp/UT_TestTop/Makefile missing"
  write_skip_log "${LOG_DIR}/cpp_prepare.log" "dpi_cpp/UT_TestTop/Makefile missing"
  write_skip_log "${LOG_DIR}/cpp_run.log" "dpi_cpp/UT_TestTop/Makefile missing"
fi

if [[ -f dpi_cpp/UT_TestTopraw/Makefile ]]; then
  ( cd dpi_cpp/UT_TestTopraw && cmake . -Bbuild -DCMAKE_BUILD_TYPE=Release && cmake --build build --parallel "$(nproc)" ) > "${LOG_DIR}/raw-verilator_prepare.log" 2>&1 || true
  run_repeats raw-verilator "dpi_cpp/UT_TestTopraw" /usr/bin/time -v ./build/UTTestTop_example
else
  write_skip_log "${LOG_DIR}/raw-verilator_prepare.log" "dpi_cpp/UT_TestTopraw/Makefile missing"
  write_skip_log "${LOG_DIR}/raw-verilator_run.log" "dpi_cpp/UT_TestTopraw/Makefile missing"
fi

ensure_release "dpi_java" "dpi_java/UT_TestTop/Makefile" "${LOG_DIR}/java_bootstrap.log"
if [[ -f dpi_java/UT_TestTop/Makefile ]]; then
  ( cd dpi_java/UT_TestTop && rm -rf build UT_TestTop-java.jar && make TARGET=UT_TestTop compile ) > "${LOG_DIR}/java_prepare.log" 2>&1 || true
  run_repeats java "dpi_java/UT_TestTop" /usr/bin/time -v java -cp xspcomm-java.jar:UT_TestTop-java.jar -ea com.ut.TestTop.example
else
  write_skip_log "${LOG_DIR}/java_bootstrap.log" "dpi_java/UT_TestTop/Makefile missing"
  write_skip_log "${LOG_DIR}/java_prepare.log" "dpi_java/UT_TestTop/Makefile missing"
  write_skip_log "${LOG_DIR}/java_run.log" "dpi_java/UT_TestTop/Makefile missing"
fi

ensure_release "dpi_golang" "dpi_golang/UT_TestTop/golang/src/UT_TestTop/UT_TestTop.go" "${LOG_DIR}/golang_bootstrap.log"
if [[ -f dpi_golang/UT_TestTop/golang/src/UT_TestTop/UT_TestTop.go ]]; then
  ( cd dpi_golang && GO111MODULE=off GOPATH="`pwd`/UT_TestTop/golang:/usr/local/share/picker/golang" GOCACHE="`pwd`/.gocache" go build -o example example.go ) > "${LOG_DIR}/golang_prepare.log" 2>&1 || true
  run_repeats golang "dpi_golang" /usr/bin/time -v ./example
else
  write_skip_log "${LOG_DIR}/golang_bootstrap.log" "dpi_golang/UT_TestTop/golang/src/UT_TestTop/UT_TestTop.go missing"
  write_skip_log "${LOG_DIR}/golang_prepare.log" "dpi_golang/UT_TestTop/golang/src/UT_TestTop/UT_TestTop.go missing"
  write_skip_log "${LOG_DIR}/golang_run.log" "dpi_golang/UT_TestTop/golang/src/UT_TestTop/UT_TestTop.go missing"
fi
