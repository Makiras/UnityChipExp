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

rm -rf sim_build
rm -f results.xml

/usr/bin/time -v make sim_build/Vtop > "${LOG_DIR}/build.log" 2>&1
