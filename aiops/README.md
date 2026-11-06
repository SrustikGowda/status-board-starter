# AIOps for beginners

Three small files that turn a stream of checks into one calm answer: what looked
abnormal, and what changed just before it. Python standard library only.

## The files

- `watch.py`: checks a URL twice a second and appends `unix_time,milliseconds` to a file.
  No answer (error, or nothing within 2 s) is written as `unix_time,none`. That file is your metric.
  Options: `--url` (default `http://localhost:8080/health`), `--seconds`, `--out`.
- `detect.py`: learns the normal band from the first 60 answered checks (the middle value
  plus `--margin` ms, default 5), flags every later check above the band (no answer always counts),
  groups flags within `--gap` seconds (default 5) into incidents, and names the most recent
  change in the change log before each one. The change log has lines like
  `1700000000.123,deploy version 2`.
- `demo.sh`: one repeatable run, about 85 s. Learn normal for 40 s, deploy version 2 (600 ms
  per answer), roll back at 70 s, keep watching, then run `detect.py`.
- `test_detect.py`: pytest tests for the detector. `SAMPLE_OUTPUT.txt`: a real run.

## Run it

From the starter root (the folder with `app.py`):

```
bash aiops/demo.sh                 # uses port 8080; PORT=8093 bash aiops/demo.sh for another
```

The data stays in `aiops/last-run/` (`checks.csv`, `changes.log`). Change the margin from 5 to
1,000 and read the same data again:

```
python3 aiops/detect.py --checks aiops/last-run/checks.csv --changes aiops/last-run/changes.log --margin 1000
```

The band is now so wide that the slow deploy slips through. Only the blip during the
rollback is flagged, and the detector blames the rollback. A tool only knows what you tell it.

## Honest notes

- The demo switches version 2 on without a restart (it edits `last-run/version.txt`, which the
  app reads on every request), so the deploy has no downtime. The rollback does restart the app,
  and demo.sh times the pause so the watcher catches exactly one check with no answer.
- Numbers vary a little between runs (the normal band, the worst time, how many checks fall
  in the incident). The story should not.
- Checks used to learn the band are not themselves judged.
- A likely cause is not proof. You decide.
