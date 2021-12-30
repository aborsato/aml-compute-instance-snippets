#!/bin/bash

# Get path to script
SCRIPT=$(readlink -f "$0")
SCRIPT_PATH=$(dirname "$SCRIPT")
echo "Current working dir: $PWD"
echo "Path to scripts: $SCRIPT_PATH"

# Get python path
PYTHON_PATH=`which python`
echo "Python Path: $PYTHON_PATH"

# The file /etc/environment.sso stores the environment variables used by the API to authenticate to Azure services
set -a
source /etc/environment.sso
set +a

$PYTHON_PATH $SCRIPT_PATH/shutdown_if_inactive.py
