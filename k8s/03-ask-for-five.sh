#!/usr/bin/env bash
# Chapter 8, ask for five: change the number in the file, apply, watch two more pods open.
source "$(dirname "$0")/common.sh"; use_yard

say "Editing the clipboard: replicas 3 -> 5 (applied from a changed copy; the file on disk stays at 3)"
sed 's/replicas: 3/replicas: 5/' "$K8S_DIR/deployment.yaml" | { printf '$ kubectl apply -f - (replicas: 5)\n'; kubectl apply -f -; }
run kubectl rollout status deployment/status-board --timeout=120s
run $PODS

say "Putting the clipboard back: apply the real file, which says three"
run kubectl apply -f "$K8S_DIR/deployment.yaml"
sleep 5
run $PODS
