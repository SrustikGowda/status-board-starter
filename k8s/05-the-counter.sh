#!/usr/bin/env bash
# Chapter 10, the counter: a Service gives one stable address; reach it on localhost:8092.
source "$(dirname "$0")/common.sh"; use_yard

say "Creating the counter (Service)"
run kubectl apply -f "$K8S_DIR/service.yaml"
run kubectl get service status-board
run kubectl get endpointslices -l kubernetes.io/service-name=status-board

say "Opening a tunnel: localhost:8092 -> Service status-board:80"
kubectl port-forward service/status-board 8092:80 >/tmp/status-board-port-forward.log 2>&1 &
PF=$!
trap 'kill $PF 2>/dev/null || true' EXIT
for i in $(seq 1 20); do curl -fs localhost:8092/health >/dev/null 2>&1 && break; sleep 1; done

say "Knocking on the counter four times"
for i in 1 2 3 4; do
  printf '$ curl localhost:8092/health  ->  '; curl -s -w '  (HTTP %{http_code})\n' localhost:8092/health
done
echo "Same address every time, whichever pod answers."
