# SLO starter: error budgets and incidents

Needs the status board's Flask (`pip install -r ../requirements.txt`) and Python 3.9+.
Run every command from the `status-board-starter` folder.

| File | What it does |
|------|--------------|
| `serve.py` | Runs the board's `app.py` as a "version": `--port`, `--version`, `--delay-ms` (slow), `--error-rate` (0-1 of requests fail). Adds `/version` and an `X-Version` header. `--control FILE` makes it read `version delay_ms` (e.g. `v2 600`) from FILE on every request, so you can "deploy" with no restart. |
| `watch.py` | Checks `/health` every 0.5 s and appends `unix_time,milliseconds,ok\|error` to `checks.csv`. |
| `changes.py` | Notes a change with a time in `changes.log`. |
| `slo.py` | Reads the two files: SLI, error budget (the health bar), errors vs slow answers, burn rate, alert, and a clue about the cause. |
| `budget.py` | Arithmetic: how much bad time a target allows. |
| `demo.sh` | The whole story in about 90 seconds: one server, v2 "deployed" by editing a control file, so nothing is ever down, only slow. |
| `test_slo.py` | pytest tests for the maths in `slo.py` and `budget.py`. |
| `POSTMORTEM_TEMPLATE.md` | A blameless incident review to fill in. |
| `prometheus/` | Optional: the same idea with real tools. |

## Order to run things

1. The sums first: `python3 slo/budget.py 99.9 28` (add `--requests 2000000` for requests).
2. Run the story: `bash slo/demo.sh` (set `PORT=8091` to change the port; `PYTHON=` to pick an interpreter).
   `SAMPLE_OUTPUT.txt` is one real run. The run's data is kept in `slo/last-run/`, so you can
   re-read it with other settings, e.g. `python3 slo/slo.py --checks slo/last-run/checks.csv --changes slo/last-run/changes.log --threshold-ms 1000`.
3. Or do it by hand, in separate terminals:
   ```
   echo "v1 0" > control.txt
   python3 slo/serve.py --control control.txt
   python3 slo/watch.py --seconds 60
   python3 slo/changes.py "deploy v2"      # then: echo "v2 600" > control.txt
   python3 slo/slo.py
   ```
   A check is good when it is ok and took at most 300 ms (`--threshold-ms`). Defaults: `--target 99`, `--window 60`.
   Verdicts: BUDGET OK (over 25% left), BUDGET LOW, BUDGET EMPTY (pause risky changes). When overspent it shows 0% left and how many times the allowance was used.
   Alerts (single-window simplification of the SRE Workbook table): 14.4x or 6x = PAGE, 1x = TICKET.
4. Fill in `POSTMORTEM_TEMPLATE.md` for the incident.
5. Tests: `pip install pytest && pytest slo`

`slo.py` measures the window from the last check, so the same files always give the same report.
"Likely cause" is a clue (the last change before the first bad check), not proof.

## Optional: Prometheus and Blackbox Exporter

Needs Docker. Start the app (`python3 slo/serve.py`), then:

```
cd slo/prometheus
docker compose up -d
```

Open http://localhost:9090. Under Status > Targets the probe should be UP; query
`sli:probe_success:ratio_5m`. Alerts are on the Alerts page. If your app is not on port 8080, edit the
target in `prometheus.yml`. Stop with `docker compose down`.

`rules.yml` records the success ratio over 5m, 30m, 1h and 6h for a 99% target, and has two alerts
in the style of the Google SRE Workbook: 14.4x over 1h and 5m, 6x over 6h and 30m (both page, as in Table 5-8 of https://sre.google/workbook/alerting-on-slos/).
The probe only sees success or failure, not the 300 ms threshold that `slo.py` uses.
Check the files with `promtool check config` and `promtool check rules` from the Prometheus image.
