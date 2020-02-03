#!/usr/bin/env bash

set -eu

find_docker_installation() {
    DOCKER="not_found"
    command -v docker && DOCKER=docker
    command -v podman && DOCKER=podman
    if [[ $DOCKER = "not_found" ]]; then
        echo "No docker or podman installation found!"
        return 1
    else
        echo "using $DOCKER as docker executable"
    fi
}

find_docker_installation

echo "Building docker containers"

namespace="demo"
apps=(stage_1 stage_2 load_balancer service_registry)

for app in "${apps[@]}"; do
    echo "Building app $app"
    ${DOCKER} build -t "${namespace}_${app}" -f "docker/${app}/Dockerfile" .
done