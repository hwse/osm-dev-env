#!/usr/bin/env bash

set -eu

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

run_remote() {
    ssh "$REMOTE_USER"@"$REMOTE_HOST" "$@"
}

echo "Deploying Files"

run_remote 'mkdir -p ~/deploy'

scp -r "$SCRIPT_DIR" "$REMOTE_USER"@"$REMOTE_HOST":~/deploy
echo "Building Docker Images"

run_remote 'cd ~/deploy/demo_application && ./build_docker_image.sh'