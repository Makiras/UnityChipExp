#!/bin/bash

# This script is used to calculate the build time of the project
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

LOG_DIR="${LOG_DIR:-logs}"
mkdir -p "${LOG_DIR}"

rm -rf dpi_python

/usr/bin/time make python-dpi > "${LOG_DIR}/python-dpi_codegen_roc.txt" 2>&1

cd dpi_python && /usr/bin/time make > "../${LOG_DIR}/python-dpi_build_ml.txt" 2>&1
cd ..

rm -rf dpi_cpp

/usr/bin/time make cpp-dpi > "${LOG_DIR}/cpp-dpi_codegen_roc.txt" 2>&1

cd dpi_cpp && /usr/bin/time make > "../${LOG_DIR}/cpp-dpi_build_ml.txt" 2>&1
cd ..

rm -rf dpi_java

/usr/bin/time make java-dpi > "${LOG_DIR}/java-dpi_codegen_roc.txt" 2>&1

cd dpi_java && /usr/bin/time make > "../${LOG_DIR}/java-dpi_build_ml.txt" 2>&1
cd ..

rm -rf dpi_golang

/usr/bin/time make golang-dpi > "${LOG_DIR}/golang-dpi_codegen_roc.txt" 2>&1

cd dpi_golang && /usr/bin/time make > "../${LOG_DIR}/golang-dpi_build_ml.txt" 2>&1
cd ..
