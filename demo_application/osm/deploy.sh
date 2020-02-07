#!/usr/bin/env bash

set -eu

DEPLOY_DIR='/tmp/osm_deploy'

run_remote() {
    ssh "$REMOTE_USER"@"$REMOTE_HOST" "$@"
}


run_remote "mkdir -p ${DEPLOY_DIR}"

vnfds=$(find vnfd -name "*.tar.gz")
scp $vnfds "${REMOTE_USER}@${REMOTE_HOST}:${DEPLOY_DIR}"

nsds=$(find nsd -name "*.tar.gz")
scp $nsds "${REMOTE_USER}@${REMOTE_HOST}:${DEPLOY_DIR}"

for nsd in $nsds; do
    nsd=$(basename "$nsd")
    nsd_name="${nsd%%.*}"
    echo "=== Delete NSD-packge $nsd_name ==="
    run_remote "osm nsd-delete $nsd_name" || echo "Ignore Failure"
done

for vnfd in $vnfds; do
    vnfd=$(basename "$vnfd")
    vnfd_name="${vnfd%%.*}"
    echo "=== Delete VNFD-packge $vnfd_name ==="
    run_remote "osm vnfd-delete $vnfd_name" || echo "Ignore Failure"

    echo "=== Creating VNFD-package: $vnfd_name ==="
    run_remote "osm vnfd-create ${DEPLOY_DIR}/${vnfd}"
done

for nsd in $nsds; do
    nsd=$(basename "$nsd")
    nsd_name="${nsd%%.*}"

    echo "=== Create NSD-package $nsd_name ==="
    run_remote "osm nsd-create ${DEPLOY_DIR}/${nsd}" || echo "Ignore Failure"
done