#!/usr/bin/env bash

# for Z see https://www.mankier.com/1/podman-run
docker run -ti -v "$PWD:/work:Z" demo_osm_builder /bin/bash