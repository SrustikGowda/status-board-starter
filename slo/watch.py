"""Check a URL twice a second and write one CSV line per check."""
import argparse
import time
import urllib.request


def check(url, timeout=2.0):
    """Return (milliseconds, 'ok' or 'error'). Slow (>2 s) or failed = error."""
    started = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as reply:
            state = "ok" if 200 <= reply.status < 400 else "error"
    except Exception:
        state = "error"
    return round((time.monotonic() - started) * 1000), state


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", default="http://localhost:8080/health")
    p.add_argument("--seconds", type=float, default=60)
    p.add_argument("--out", default="checks.csv")
    args = p.parse_args()

    end = time.time() + args.seconds
    with open(args.out, "a") as out:
        while time.time() < end:
            began = time.time()
            ms, state = check(args.url)
            out.write(f"{began:.3f},{ms},{state}\n")
            out.flush()
            time.sleep(max(0, 0.5 - (time.time() - began)))


if __name__ == "__main__":
    main()
