"""Check a URL twice a second and write one line per check: unix_time,milliseconds.

A check with no answer (error or 2 s timeout) is written as unix_time,none.
That file is your metric.
"""
import argparse
import time
import urllib.request


def check(url, timeout=2.0):
    """Return how many milliseconds the answer took, or None if there was none."""
    started = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as reply:
            if not 200 <= reply.status < 400:
                return None
            reply.read()
    except Exception:
        return None
    return round((time.monotonic() - started) * 1000)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", default="http://localhost:8080/health")
    p.add_argument("--seconds", type=float, default=60, help="how long to keep watching")
    p.add_argument("--out", default="checks.csv")
    args = p.parse_args()

    end = time.time() + args.seconds
    with open(args.out, "a") as out:
        while time.time() < end:
            began = time.time()
            ms = check(args.url)
            out.write(f"{began:.3f},{'none' if ms is None else ms}\n")
            out.flush()
            time.sleep(max(0, 0.5 - (time.time() - began)))  # two checks a second


if __name__ == "__main__":
    main()
