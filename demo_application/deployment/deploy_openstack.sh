#!/usr/bin/env bash

set -euxo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "Deploy to $REMOTE_USER on $REMOTE_HOST"

run_remote() {
    ssh "$REMOTE_USER"@"$REMOTE_HOST" "$@"
}


run_remote rm -rf /tmp/deploy
scp -r "$SCRIPT_DIR" "${REMOTE_USER}@${REMOTE_HOST}:/tmp/deploy"

run_remote "cd /tmp/deploy && packer build -only=openstack -var-file=service_registry_vars.json build.json"