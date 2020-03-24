#!/usr/bin/env bash

set -euo pipefail

VNFS=(load_balancer service_registry stage_1 stage_2)

./create_deploy_dirs.sh

if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo -n "Enter AWSAccessKeyId:"
    read -r -s AWS_ACCESS_KEY_ID
    echo
fi

if [ -z "$AWS_SECRET_KEY" ]; then
    echo -n "Enter AWSSecretKey:"
    read -r -s AWS_SECRET_KEY
    echo
fi

for vnf in "${VNFS[@]}"; do
    packer build -only=amazon-ebs \
        -var "aws_access_key=$AWS_ACCESS_KEY_ID" \
        -var "aws_secret_key=$AWS_SECRET_KEY" \
        -var-file="${vnf}_vars.json" \
        build.json
done