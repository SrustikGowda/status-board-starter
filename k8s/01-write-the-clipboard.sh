#!/usr/bin/env bash
# Chapter 5, the clipboard: apply a file that says "three copies", wait for three pods.
source "$(dirname "$0")/common.sh"; use_yard

say "Writing the clipboard: deployment.yaml says replicas: 3"
grep -n 'replicas:' "$K8S_DIR/deployment.yaml"
run kubectl apply -f "$K8S_DIR/deployment.yaml"

say "Waiting until 3/3 pods are ready"
run kubectl rollout status deployment/status-board --timeout=180s
run kubectl get deployment status-board

say "The crates (pods) and the hub (node) each one stands on"
run $PODS
