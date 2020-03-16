#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$0")
CODE_DIR="${SCRIPT_DIR}/.."

VNFS=(load_balancer service_registry stage_1 stage_2)
CONTROL_FILES=(start.sh stop.sh)

mkdir -p "${VNFS[@]}"

for vnf in "${VNFS[@]}"; do
    echo "Building deploy directory for: $vnf"
    vnf_dir="${SCRIPT_DIR}/${vnf}"
    cp "${CODE_DIR}/common.py" \
        "${CODE_DIR}/common_requirements.txt" \
        "${CODE_DIR}/${vnf}.py" \
        "${CODE_DIR}/${vnf}_requirements.txt" \
        "$vnf_dir"
    for control_file in "${CONTROL_FILES[@]}"; do
        sed -e "s/%VNF%/${vnf}/g" "${SCRIPT_DIR}/${control_file}" > "${vnf_dir}/${control_file}"
        chmod +x "${vnf_dir}/${control_file}"
    done
    sed -e "s/%VNF%/${vnf}/g" "${SCRIPT_DIR}/run_app.sh" > "${vnf_dir}/${vnf}.sh"
    chmod +x "${vnf_dir}/${vnf}.sh"
done

echo "Done!"