"""Learn the normal band, flag what is outside it, group flags, find the cause.

    python3 aiops/detect.py --checks checks.csv --changes changes.log
"""
import argparse
import statistics

LEARN = 60  # how many answered checks teach us what normal is


def read_checks(path):
    """[(unix_time, milliseconds or None)] from 'time,ms' or 'time,none' lines."""
    rows = []
    with open(path) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 2:
                rows.append((float(parts[0]), None if parts[1] == "none" else float(parts[1])))
    return sorted(rows, key=lambda r: r[0])


def read_changes(path):
    """[(unix_time, description)] from 'time,description' lines."""
    rows = []
    try:
        with open(path) as f:
            for line in f:
                when, _, text = line.strip().partition(",")
                if text:
                    rows.append((float(when), text))
    except OSError:
        pass
    return sorted(rows)


def learn(checks, margin, count=LEARN):
    """Return (median, band, used, index where learning ended).

    The band is the middle value of the first `count` answered checks plus the margin.
    """
    seen = []
    for i, (_, ms) in enumerate(checks):
        if ms is not None:
            seen.append(ms)
            if len(seen) == count:
                break
    if not seen:
        raise ValueError("no answered checks to learn from")
    middle = statistics.median(seen)
    return middle, middle + margin, len(seen), i + 1


def flag(checks, band):
    """The checks above the band. No answer always counts as above."""
    return [(t, ms) for t, ms in checks if ms is None or ms > band]


def group(flags, gap):
    """Flags within `gap` seconds of the one before belong to one incident."""
    incidents = []
    for item in flags:
        if incidents and item[0] - incidents[-1][-1][0] <= gap:
            incidents[-1].append(item)
        else:
            incidents.append([item])
    return incidents


def likely_cause(changes, when):
    """(description, seconds before) of the latest change at or before `when`."""
    before = [c for c in changes if c[0] <= when]
    if not before:
        return None
    t, text = before[-1]
    return text, when - t


def seconds(s):
    if s < 0.1:
        return "under 0.1 s"
    return f"{round(s)} s" if s >= 1 else f"{s:.1f} s"


def report(checks, changes, margin, gap):
    middle, band, used, end = learn(checks, margin)
    flags = flag(checks[end:], band)  # judge only what came after the learning
    incidents = group(flags, gap)
    n = len(incidents)
    out = [
        f"Checks read:      {len(checks)}",
        f"Normal band:      about {middle:.0f} ms, alert above {band:.0f} ms",
        f"                  (learned from {used} checks)",
        f"Outside the band: {len(flags)} check{'' if len(flags) == 1 else 's'}",
    ]
    if not incidents:
        return out + ["Nothing to flag.", "You decide."]
    grouped = f"{n} incident{'' if n == 1 else 's'}"
    if len(flags) > n:
        grouped += f" (not {len(flags)} alerts)"
    out.append(f"Grouped into:     {grouped}")
    for i, inc in enumerate(incidents, 1):
        span = inc[-1][0] - inc[0][0]
        answered = [ms for _, ms in inc if ms is not None]
        text = f"{len(inc)} check{'' if len(inc) == 1 else 's'}"
        text += f" over {round(span)} s" if span >= 1 else ""
        text += f", worst {max(answered):.0f} ms" if answered else ", no answer"
        out.append(f"Incident {i}:".ljust(18) + text)
        cause = likely_cause(changes, inc[0][0])
        text = "none in the change log" if cause is None else (
            f"{cause[0]}, {seconds(cause[1])} before it started")
        out.append("Likely cause:".ljust(18) + text)
    return out + ["This is a likely cause, not proof.", "You decide."]


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checks", default="checks.csv")
    p.add_argument("--changes", default="changes.log")
    p.add_argument("--margin", type=float, default=5, help="ms added to the middle value")
    p.add_argument("--gap", type=float, default=5, help="seconds that join flags into one incident")
    a = p.parse_args()
    print("\n".join(report(read_checks(a.checks), read_changes(a.changes), a.margin, a.gap)))
