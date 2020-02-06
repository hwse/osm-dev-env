#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")"

vnfds=$(find vnfd -mindepth 1 -type d)
for vnfd in $vnfds; do
    generate_descriptor_pkg.sh -N "$vnfd"
done

nsds=$(find nsd -mindepth 1 -type d)
for nsd in $nsds; do
    generate_descriptor_pkg.sh -N "$nsd"
done