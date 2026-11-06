"""Read checks.csv and say how much error budget is left."""
import argparse
import os


def load_checks(path):
    """Rows of (unix_time, milliseconds, ok_bool), oldest first."""
    rows = []
    with open(path) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 3:
                rows.append((float(parts[0]), float(parts[1]), parts[2] == "ok"))
    return sorted(rows)


def load_changes(path):
    rows = []
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                when, _, text = line.strip().partition(",")
                if text:
                    rows.append((float(when), text))
    return sorted(rows)


def is_good(row, threshold_ms):
    return row[2] and row[1] <= threshold_ms


def count_bad(rows, threshold_ms):
    return sum(1 for r in rows if not is_good(r, threshold_ms))


def sli_percent(good, total):
    return 100.0 * good / total if total else 100.0


def budget_allowed(total, target):
    """Bad checks the target allows out of this many checks."""
    return total * (1 - target / 100)


def budget_remaining(allowed, used):
    """Percent of budget left. Negative means overspent."""
    if allowed == 0:
        return 100.0 if used == 0 else float("-inf")
    return 100.0 * (allowed - used) / allowed


def burn_rate(rows, threshold_ms, target, window):
    """(bad fraction in the last `window` seconds) / (1 - target)."""
    if not rows:
        return 0.0
    since = rows[-1][0] - window
    recent = [r for r in rows if r[0] > since]
    return (count_bad(recent, threshold_ms) / len(recent)) / (1 - target / 100)


def verdict(remaining):
    if remaining > 25:
        return "BUDGET OK"
    if remaining > 0:
        return "BUDGET LOW"
    return "BUDGET EMPTY: pause risky changes"


def alert(rate):
    """Single-window version of the SRE Workbook table (14.4x, 6x page; 1x ticket)."""
    if rate >= 14.4:
        return "PAGE: burning 14x too fast"
    if rate >= 6:
        return "PAGE: burning 6x too fast"
    if rate >= 1:
        return "TICKET: budget will run out"
    return "No alert"


def count_errors_and_slow(rows, threshold_ms):
    """Errors = no good answer. Slow = answered ok, but too late."""
    errors = sum(1 for r in rows if not r[2])
    slow = sum(1 for r in rows if r[2] and r[1] > threshold_ms)
    return errors, slow


def overspent(allowed, used):
    """How many times the allowance was used, or None if not overspent."""
    return used / allowed if allowed and used > allowed else None


def likely_cause(rows, changes, threshold_ms):
    """Latest change before the first bad check: a clue, not proof."""
    bad = [r for r in rows if not is_good(r, threshold_ms)]
    before = [c for c in changes if bad and c[0] <= bad[0][0]]
    if not before:
        return None
    when, text = before[-1]
    return text, bad[0][0] - when


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checks", default="checks.csv")
    p.add_argument("--changes", default="changes.log")
    p.add_argument("--threshold-ms", type=float, default=300)
    p.add_argument("--target", type=float, default=99.0, help="percent")
    p.add_argument("--window", type=float, default=60, help="seconds")
    a = p.parse_args()

    rows = load_checks(a.checks)
    total = len(rows)
    used = count_bad(rows, a.threshold_ms)
    allowed = budget_allowed(total, a.target)
    left = budget_remaining(allowed, used)
    rate = burn_rate(rows, a.threshold_ms, a.target, a.window)

    print(f"Good = ok and <= {a.threshold_ms:g} ms")
    print(f"Total checks:     {total}")
    print(f"Good checks:      {total - used}")
    print(f"SLI:              {sli_percent(total - used, total):.1f}%")
    print(f"Target:           {a.target:g}%")
    print(f"Budget allowed:   {allowed:.1f} bad checks")
    print(f"Bad checks used:  {used}")
    print(f"Budget remaining: {max(left, 0):.0f}%")
    over = overspent(allowed, used)
    if over:
        print(f"Overspent:        {over:.1f}x the allowance")
    errors, slow = count_errors_and_slow(rows, a.threshold_ms)
    print(f"Errors: {errors}   Slow (>{a.threshold_ms:g} ms): {slow}")
    print(f"{'Burn rate (' + format(a.window, 'g') + 's):':18}{rate:.1f}x")
    print(verdict(left))
    print(alert(rate))
    print("(one window; real alerts use two)")
    cause = likely_cause(rows, load_changes(a.changes), a.threshold_ms)
    if cause:
        print(f"Likely cause: {cause[0][:30]}, {cause[1]:.1f} s before trouble")
        print("(a clue, not proof: go and check)")


if __name__ == "__main__":
    main()
