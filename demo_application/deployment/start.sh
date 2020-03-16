#!/usr/bin/env bash


VNF="%VNF%"
APP_STARTER="/opt/${VNF}/${VNF}.sh"
PID=$(pgrep -f "$APP_STARTER")

set -euxo pipefail

if [ -z "$PID" ]; then
    echo "Not running"
    echo "Starting $VNF ..."
    nohup "$APP_STARTER" &
else
    echo "Already running"
fi