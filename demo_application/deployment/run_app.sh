#!/bin/bash

VNF="%VNF%"

while true; do
    if SERVICE_REGISTRY_HOST="10.0.0.5" python3 "/opt/$VNF/$VNF.py"; then
        break
    fi
    echo "Application stopped, restarting now...."
done
