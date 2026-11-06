#!/usr/bin/env bash
# Chapter 11, on your laptop: delete one pod, do NOT fix it, watch a new one appear.
source "$(dirname "$0")/common.sh"; use_yard

say "Before: three pods"
run $PODS

VICTIM="$(kubectl get pods -l app=status-board -o jsonpath='{.items[0].metadata.name}')"
say "Deleting one pod: $VICTIM (and touching nothing else)"
run kubectl delete pod "$VICTIM" --wait=false

say "Watching: a snapshot every 2 seconds for 16 seconds"
for i in 1 2 3 4 5 6 7 8; do
  printf '\n-- t+%ss\n' "$(( (i-1) * 2 ))"
  kubectl get pods -l app=status-board -o wide
  sleep 2
done

say "After: three pods again, one of them new"
run kubectl get deployment status-board
echo "The clipboard still said three, so the tower opened another."
