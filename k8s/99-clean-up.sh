#!/usr/bin/env bash
# Delete the whole yard. The local Docker images stay unless you remove them.
source "$(dirname "$0")/common.sh"
say "Deleting the kind cluster '$CLUSTER'"
run kind delete cluster --name "$CLUSTER"
echo "Optional: docker rmi status-board:v1 status-board:v2"
