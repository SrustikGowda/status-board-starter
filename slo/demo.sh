#!/usr/bin/env bash
# One repeatable run (~90 s): v1 is fine, v2 is slow (never down), roll back, read the budget.
#   PORT=8091 bash slo/demo.sh
PORT="${PORT:-8080}"
PY="${PYTHON:-python3}"
HERE="$(cd "$(dirname "$0")" && pwd)"
RUN="$(mktemp -d)"
cd "$RUN" || exit 1
SERVER=""
WATCHER=""

stop_server() { [ -n "$SERVER" ] && kill "$SERVER" 2>/dev/null && wait "$SERVER" 2>/dev/null; SERVER=""; }
cleanup() { stop_server; [ -n "$WATCHER" ] && kill "$WATCHER" 2>/dev/null; rm -rf "$RUN"; }
trap cleanup EXIT

start() {  # one server for the whole run; it reads control.txt on every request
  echo "v1 0" > control.txt
  "$PY" "$HERE/serve.py" --port "$PORT" --control control.txt >> server.log 2>&1 &
  SERVER=$!
  until curl -sf "http://localhost:$PORT/health" >/dev/null; do sleep 0.2; done
}
step() { echo "[$(printf '%2d' "$SECONDS") s] $1"; }
wait_until() { while [ "$SECONDS" -lt "$1" ]; do sleep 0.2; done; }

SECONDS=0
step "start v1 (fast)"
start
"$PY" "$HERE/watch.py" --url "http://localhost:$PORT/health" --seconds 90 --out checks.csv &
WATCHER=$!

wait_until 40
step "deploy v2 (600 ms delay, no restart)"
"$PY" "$HERE/changes.py" "deploy v2" --log changes.log
echo "v2 600" > control.txt

wait_until 70
step "rollback to v1 (no restart)"
"$PY" "$HERE/changes.py" "rollback to v1" --log changes.log
echo "v1 0" > control.txt

wait "$WATCHER"; WATCHER=""
step "done watching"
echo
"$PY" "$HERE/slo.py"

# Keep this run's data so you can re-read it with other settings.
mkdir -p "$HERE/last-run" && cp checks.csv changes.log "$HERE/last-run/"
echo
echo "Data kept in slo/last-run/. Try a looser threshold:"
echo "  python3 slo/slo.py --checks slo/last-run/checks.csv \\"
echo "    --changes slo/last-run/changes.log --threshold-ms 1000"
