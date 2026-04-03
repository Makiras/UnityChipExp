#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

LOG_DIR="${LOG_DIR:-logs}"
mkdir -p "${LOG_DIR}"

rm -rf sim_build
rm -f results.xml

/usr/bin/time -v make sim_build/Vtop > "${LOG_DIR}/build.log" 2>&1
