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
- `aiops/`: the AIOps episode. Run `bash aiops/demo.sh` to learn a normal band, deploy a slow v2, roll back and let the detector group the alerts into one incident (see `aiops/README.md`).
- `slo/`: the SLO and error-budget episode. Run `bash slo/demo.sh` to deploy a slow v2, watch the budget drain and read the report (see `slo/README.md`).
- `k8s/`: the Kubernetes episode. A tiny three-node yard on your laptop with kind: three pods, delete one, watch it come back (see `k8s/README.md`).

The sites are the reserved documentation domains; swap in sites you're allowed to check.
