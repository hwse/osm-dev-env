#!/usr/bin/env bash

set -euxo pipefail

docker build -t demo_osm_builder --build-arg USER_UID=$UID .