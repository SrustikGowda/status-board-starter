#!/usr/bin/env bash
# Chapter 4, the yard: build a tiny cluster (one tower, two hubs) and pack the app as status-board:v1.
source "$(dirname "$0")/common.sh"

say "Creating the kind cluster '$CLUSTER' (1 control-plane + 2 workers). Takes a minute or two."
run kind create cluster --name "$CLUSTER" --config "$K8S_DIR/kind-config.yaml"

say "Packing the app into an image from the starter Dockerfile: status-board:v1"
run docker build -q -t status-board:v1 "$APP_DIR"

say "Loading the image into every node (kind cannot see your local Docker images otherwise)"
load_image status-board:v1

say "Waiting for all three nodes to be Ready"
run kubectl wait --for=condition=Ready node --all --timeout=120s
run kubectl get nodes
