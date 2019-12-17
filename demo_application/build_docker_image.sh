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
${DOCKER} build -t demo_stage_1 -f docker/stage_1/Dockerfile .
${DOCKER} build -t demo_stage_2 -f docker/stage_2/Dockerfile .
