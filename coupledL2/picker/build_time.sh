#!/bin/bash

# This script is used to calculate the build time of the project
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

LOG_DIR="${LOG_DIR:-logs}"
mkdir -p "${LOG_DIR}"

rm -rf dpi_python
echo "############# Codegen time #############" > "${LOG_DIR}/python-dpi_codegen_time.txt"
/usr/bin/time make python-dpi >> "${LOG_DIR}/python-dpi_codegen_time.txt" 2>&1
echo "############# Build time #############" > "${LOG_DIR}/python-dpi_build_time.txt"
cd dpi_python && /usr/bin/time make >> "../${LOG_DIR}/python-dpi_build_time.txt" 2>&1
cd ..

rm -rf mem_python
echo "############# Codegen time #############" > "${LOG_DIR}/python-mem_codegen_time.txt"
/usr/bin/time make python-mem >> "${LOG_DIR}/python-mem_codegen_time.txt" 2>&1
echo "############# Build time #############" > "${LOG_DIR}/python-mem_build_time.txt"
cd mem_python && /usr/bin/time make >> "../${LOG_DIR}/python-mem_build_time.txt" 2>&1
cd ..

rm -rf vpi_python
echo "############# Codegen time #############" > "${LOG_DIR}/python-vpi_codegen_time.txt"
/usr/bin/time make python-vpi >> "${LOG_DIR}/python-vpi_codegen_time.txt" 2>&1
echo "############# Build time #############" > "${LOG_DIR}/python-vpi_build_time.txt"
cd vpi_python && /usr/bin/time make >> "../${LOG_DIR}/python-vpi_build_time.txt" 2>&1
cd ..
