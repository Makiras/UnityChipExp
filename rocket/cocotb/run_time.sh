#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

LOG_DIR="${LOG_DIR:-logs}"
mkdir -p "${LOG_DIR}"
export CCACHE_DIR="${CCACHE_DIR:-${SCRIPT_DIR}/.ccache}"
export CCACHE_TEMPDIR="${CCACHE_TEMPDIR:-${SCRIPT_DIR}/.ccache-tmp}"
mkdir -p "${CCACHE_DIR}"
mkdir -p "${CCACHE_TEMPDIR}"
BUILD_JOBS="${BUILD_JOBS:-$(nproc)}"

RUN_REPEATS="${RUN_REPEATS:-7}"
PIN_RUNTIME="${PIN_RUNTIME:-1}"
PIN_CPUS="${PIN_CPUS:-2-5}"

for i in $(seq 1 "${RUN_REPEATS}"); do
    rm -f results.xml
    if [[ "${PIN_RUNTIME}" == "1" ]]; then
        /usr/bin/time -v taskset -c "${PIN_CPUS}" make BUILD_ARGS="-j${BUILD_JOBS}" results.xml > "${LOG_DIR}/run_${i}.log" 2>&1
    else
        /usr/bin/time -v make BUILD_ARGS="-j${BUILD_JOBS}" results.xml > "${LOG_DIR}/run_${i}.log" 2>&1
    fi
done

cp "${LOG_DIR}/run_${RUN_REPEATS}.log" "${LOG_DIR}/run.log"
