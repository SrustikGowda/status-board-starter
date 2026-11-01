# Status Board starter

The practice app from "Every App Is a Parcel Network". You don't need to write it from scratch:
clone this, then build the seven scans around it.

## Run it on your laptop

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py            # open http://localhost:8080
pytest                   # the test your CI pipeline will run in Scan 3
```

## Files

- `app.py`: the board (three sites: ON TIME, DELAYED or PROBLEM) and a `/health` page that says `OK`.
- `test_app.py`: one small test.
- `Dockerfile`: the container recipe from Scan 2 (`docker build -t status-board .`, then `docker run -p 8080:8080 status-board`).
- `check.sh`: the Stage 4 script (`bash check.sh` prints the time and UP or DOWN).

The sites are the reserved documentation domains; swap in sites you're allowed to check.
