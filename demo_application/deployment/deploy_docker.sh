#!/usr/bin/env bash

set -eu

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VNFS=(load_balancer service_registry stage_1 stage_2)
TMP_DIR=$(mktemp -d)
DEPLOY_DIR="~/deploy"

run_remote() {
    ssh "$REMOTE_USER"@"$REMOTE_HOST" "$@"
}

echo "=== Deploying Docker Images to ${REMOTE_USER}@${REMOTE_HOST}"

echo "Creating Image Files in $TMP_DIR"

for vnf in "${VNFS[@]}"; do
    docker save "$vnf" -o "/${TMP_DIR}/${vnf}.tar"
done

echo "Copying file to $REMOTE_HOST"

run_remote "mkdir -p ${DEPLOY_DIR}"
scp "$TMP_DIR"/* "$REMOTE_USER"@"$REMOTE_HOST":"$DEPLOY_DIR"

echo "Deleting tmp dir"
rm -rf "${TMP_DIR}"

echo "Importing Docker Images"

for vnf in "${VNFS[@]}"; do
    remote_image="${DEPLOY_DIR}/${vnf}.tar"
    run_remote "docker load -i ${remote_image}"
    run_remote "rm ${remote_image}"
done

echo "Images on target:"
run_remote "docker image ls"

