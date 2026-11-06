#!/usr/bin/env bash
# Chapter 6, literal: the tower does exactly what the file says, including the lines you did not mean.
source "$(dirname "$0")/common.sh"; use_yard

say "Mistake 1: the file names a crate that was never packed (status-board:v99)"
sed 's|image: status-board:v1|image: status-board:v99|' "$K8S_DIR/deployment.yaml" | { printf '$ kubectl apply -f - (image: status-board:v99)\n'; kubectl apply -f -; }
sleep 20
run $PODS
echo "The new pod cannot start, and the tower keeps trying; the old pods keep serving (maxUnavailable: 0)."
kubectl get pods -l app=status-board -o jsonpath='{range .items[*]}{.metadata.name}{"  "}{.status.containerStatuses[0].state.waiting.reason}{"\n"}{end}' | awk 'NF == 2 {print "stuck: " $0}'

say "Mistake 2: the file says replicas: 0. Zero is a number; the tower obeys."
sed 's/replicas: 3/replicas: 0/' "$K8S_DIR/deployment.yaml" | { printf '$ kubectl apply -f - (replicas: 0)\n'; kubectl apply -f -; }
sleep 10
run $PODS || true
run kubectl get deployment status-board

say "Fixing the file, not the pods: apply the real deployment.yaml (status-board:v1, replicas: 3)"
run kubectl apply -f "$K8S_DIR/deployment.yaml"
run kubectl rollout status deployment/status-board --timeout=180s
run $PODS
