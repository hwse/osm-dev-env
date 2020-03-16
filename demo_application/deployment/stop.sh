#!/usr/bin/env bash


VNF="%VNF%"
APP_STARTER="/opt/${VNF}/${VNF}.sh"
PID=$(pgrep -f "$APP_STARTER")

set -euxo pipefail

if [ -z "$PID" ]; then
    echo "Not running"
else
    echo "Already running"
    kill -9 "$PID"
    echo "Stopped $PID"
fi