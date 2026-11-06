"""Run the starter app, with knobs to make a "version" slow or flaky."""
import argparse
import logging
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from flask import cli  # noqa: E402
from app import app  # noqa: E402  (the starter's own app, not a copy)

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--port", type=int, default=8080)
p.add_argument("--version", default="v1", help="label shown in X-Version")
p.add_argument("--delay-ms", type=int, default=0, help="sleep before every request")
p.add_argument("--error-rate", type=float, default=0.0, help="0-1 share of 500s")
p.add_argument("--control", help="file holding 'version delay_ms'; read on every request")
p.add_argument("--seed", type=int, default=42, help="same seed, same errors")
args = p.parse_args()

dice = random.Random(args.seed)


def current():
    """(version, delay_ms) from the control file, else the command-line values."""
    try:
        with open(args.control) as f:
            version, delay = f.read().split()[:2]
            return version, int(delay)
    except (TypeError, OSError, ValueError):
        return args.version, args.delay_ms


@app.before_request
def misbehave():
    time.sleep(current()[1] / 1000)
    if dice.random() < args.error_rate:
        return "simulated failure", 500


@app.after_request
def label(reply):
    reply.headers["X-Version"] = current()[0]
    return reply


# Editing the control file switches version with no restart: a zero-downtime deploy.
app.add_url_rule("/version", "version", lambda: current()[0])

logging.getLogger("werkzeug").setLevel(logging.ERROR)  # keep the screen quiet
cli.show_server_banner = lambda *a, **k: None
print(f"serving {args.version} on port {args.port}", flush=True)
app.run(host="0.0.0.0", port=args.port)
