#!/usr/bin/env bash
# One run (~85 s): learn normal, deploy a slow v2, roll back, then run the detector.
#   PORT=8093 bash aiops/demo.sh        (PYTHON=... to choose the Python)
export PYTHONDONTWRITEBYTECODE=1
PORT="${PORT:-8080}"
PY="${PYTHON:-python3}"
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$HERE")"
RUN="$HERE/last-run"
rm -rf "$RUN" && mkdir -p "$RUN" && cd "$RUN" || exit 1
SERVER=""
WATCHER=""

# The starter's own app.py, plus one tweak: while version.txt says 2, every answer takes 600 ms.
# Changing that file switches version with no restart, so a deploy has no downtime.
serve() {
  "$PY" - "$ROOT" "$PORT" "$RUN/version.txt" >> server.log 2>&1 <<'PYEOF' &
import logging, sys, time
root, port, control = sys.argv[1], int(sys.argv[2]), sys.argv[3]
sys.path.insert(0, root)
from app import app

@app.before_request
def slow_if_v2():
    try:
        if open(control).read().strip() == "2":
            time.sleep(0.6)
    except OSError:
        pass

logging.getLogger("werkzeug").setLevel(logging.ERROR)
app.run(host="0.0.0.0", port=port)
PYEOF
  SERVER=$!
}
stop_server() { [ -n "$SERVER" ] && kill "$SERVER" 2>/dev/null && wait "$SERVER" 2>/dev/null; SERVER=""; }
cleanup() { stop_server; [ -n "$WATCHER" ] && kill "$WATCHER" 2>/dev/null; }
trap cleanup EXIT

healthy() { until curl -sf "http://localhost:$PORT/health" >/dev/null; do sleep 0.2; done; }
note() { printf '%s,%s\n' "$("$PY" -c 'import time; print(f"{time.time():.3f}")')" "$1" >> changes.log; }
step() { echo "[$(printf '%2d' "$SECONDS") s] $1"; }
wait_until() { while [ "$SECONDS" -lt "$1" ]; do sleep 0.2; done; }
lines() { wc -l < checks.csv | tr -d ' '; }

echo 1 > version.txt
serve; healthy
SECONDS=0
step "start version 1, start watching"
"$PY" "$HERE/watch.py" --url "http://localhost:$PORT/health" --seconds 82 --out checks.csv &
WATCHER=$!

wait_until 40
step "deploy version 2 (600 ms per answer, no restart)"
note "deploy version 2"
echo 2 > version.txt

wait_until 70
step "rollback to version 1 (restart)"
note "rollback to version 1"
echo 1 > version.txt
# Restart on purpose, timed so the watcher sees exactly one check with no answer:
# wait for a fresh check, stop the app, pause, start it again. A restart this fast
# would slip between two checks, so we pause 0.45 s: the app is gone for about 0.7 s,
# long enough to catch the next check, short enough to miss the one after.
n=$(lines); until [ "$(lines)" -gt "$n" ]; do sleep 0.02; done
stop_server
sleep 0.45
serve; healthy

wait "$WATCHER"; WATCHER=""
step "done watching"
echo
"$PY" "$HERE/detect.py" --checks checks.csv --changes changes.log

echo
echo "Data kept in aiops/last-run/. Try a much wider margin:"
echo "  python3 aiops/detect.py --checks aiops/last-run/checks.csv \\"
echo "    --changes aiops/last-run/changes.log --margin 1000"
