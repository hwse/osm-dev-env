#!/usr/bin/env bash

set -eux

DOCKER=podman

${DOCKER} build -t demo_stage_1 -f docker/stage_1/Dockerfile .
${DOCKER} build -t demo_stage_2 -f docker/stage_2/Dockerfile .
