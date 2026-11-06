#!/usr/bin/env bash
# Chapter 7, the dark hub: stop a worker node's container and watch its pods get replaced elsewhere.
source "$(dirname "$0")/common.sh"; use_yard

say "Before: where each pod stands"
run $PODS

# Pick the worker node that currently carries the most pods.
DARK="$(kubectl get pods -l app=status-board -o jsonpath='{range .items[*]}{.spec.nodeName}{"\n"}{end}' | grep worker | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')"
say "Cutting the power to $DARK (docker stop $DARK)"
START=$(date +%s)
trap 'docker start "$DARK" >/dev/null 2>&1 || true' EXIT   # never leave the node stopped, even if this script fails
run docker stop "$DARK" >/dev/null

say "Watching every 5 s until three pods are Running and none is on $DARK (limit 5 min)"
while :; do
  T=$(( $(date +%s) - START ))
  printf '\n-- t+%ss\n' "$T"
  kubectl get nodes --no-headers
  kubectl get pods -l app=status-board -o wide
  # Count live pods only: pods on the dark node stay "Terminating" until that node comes back.
  LIVE=$(kubectl get pods -l app=status-board --no-headers -o custom-columns=NODE:.spec.nodeName,READY:.status.containerStatuses[0].ready,DEL:.metadata.deletionTimestamp | awk '$3 == "<none>"')
  READY_ELSEWHERE=$(printf '%s\n' "$LIVE" | awk -v dark="$DARK" '$1 != dark && $2 == "true"' | wc -l | tr -d ' ')
  ON_DARK=$(printf '%s\n' "$LIVE" | awk -v dark="$DARK" '$1 == dark' | wc -l | tr -d ' ')
  if [ "$READY_ELSEWHERE" -ge 3 ] && [ "$ON_DARK" -eq 0 ]; then echo; echo "Replaced in about ${T}s. Three ready pods, none live on $DARK."; break; fi
  [ "$T" -gt 300 ] && { echo "Gave up after 5 minutes"; break; }
  sleep 5
done

say "Restoring the power: docker start $DARK"
run docker start "$DARK" >/dev/null
for i in $(seq 1 30); do kubectl get node "$DARK" --no-headers | grep -qw Ready && break; sleep 3; done
run kubectl get nodes
run $PODS
