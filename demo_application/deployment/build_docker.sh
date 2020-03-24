#!/usr/bin/env bash

set -euo pipefail

./create_deploy_dirs.sh

VNFS=(load_balancer service_registry stage_1 stage_2)
for vnf in "${VNFS[@]}"; do
    packer build -only=docker "-var-file=${vnf}_vars.json" -var 'app_user=root' build.json &
done

wait