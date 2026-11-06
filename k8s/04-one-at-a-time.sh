#!/usr/bin/env bash
# Chapter 9, one at a time: roll out status-board:v2 without ever going dark, then undo it.
source "$(dirname "$0")/common.sh"; use_yard

say "Packing version two (same app, heading reads 'Status Board v2')"
run docker build -q -f "$K8S_DIR/Dockerfile.v2" --build-arg LABEL=v2 -t status-board:v2 "$APP_DIR"
load_image status-board:v2

say "Telling the Deployment to use v2, then watching pods swap one at a time"
run kubectl set image deployment/status-board status-board=status-board:v2
for i in 1 2 3 4 5 6 7 8; do
  printf -- '-- t+%ss\n' "$(( (i-1) * 3 ))"; kubectl get pods -l app=status-board; sleep 3
done
run kubectl rollout status deployment/status-board --timeout=180s

say "Rollout history and the image now running"
run kubectl rollout history deployment/status-board
kubectl get deployment status-board -o jsonpath='image: {.spec.template.spec.containers[0].image}{"\n"}'
echo "Heading inside a running pod:"; kubectl exec deploy/status-board -- grep -n '<h1>' app.py

say "Changed our mind: rollout undo (swaps back, again one at a time)"
run kubectl rollout undo deployment/status-board
run kubectl rollout status deployment/status-board --timeout=180s
kubectl get deployment status-board -o jsonpath='image: {.spec.template.spec.containers[0].image}{"\n"}'
echo "Heading inside a running pod:"; kubectl exec deploy/status-board -- grep -n '<h1>' app.py
