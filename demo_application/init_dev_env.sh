#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [[ ! -d "${SCRIPT_DIR}/devops" ]]; then
    echo "devops directory is empty, cloning..."
    git clone https://osm.etsi.org/gerrit/osm/devops.git
fi