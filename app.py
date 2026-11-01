"""Status Board: a tiny web page that checks three websites and shows each one's state."""
import time
import urllib.request

from flask import Flask

SITES = ["https://example.com", "https://example.org", "https://example.net"]
SLOW_SECONDS = 2.0

app = Flask(__name__)


def check(url):
    """Return ON TIME, DELAYED (answered, but slowly) or PROBLEM (no good answer)."""
    started = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=5) as reply:
            ok = 200 <= reply.status < 400
    except Exception:
        return "PROBLEM"
    if not ok:
        return "PROBLEM"
    return "DELAYED" if time.monotonic() - started > SLOW_SECONDS else "ON TIME"


@app.get("/")
def board():
    rows = "".join(f"<tr><td>{url}</td><td>{check(url)}</td></tr>" for url in SITES)
    return f"<h1>Status Board</h1><table>{rows}</table>"


@app.get("/health")
def health():
    return "OK"


if __name__ == "__main__":
    # 0.0.0.0 so the board answers from outside the server or container, on port 8080.
    app.run(host="0.0.0.0", port=8080)
