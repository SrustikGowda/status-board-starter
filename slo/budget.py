"""How much bad time does an SLO allow?

    python3 slo/budget.py 99.9 28
    python3 slo/budget.py 99.9 28 --requests 2000000
"""
import argparse


def allowed_minutes(target_percent, days):
    return days * 24 * 60 * (1 - target_percent / 100)


def allowed_requests(target_percent, requests):
    return requests * (1 - target_percent / 100)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("target", type=float, help="SLO in percent, e.g. 99.9")
    p.add_argument("days", type=float, help="window length in days")
    p.add_argument("--requests", type=int, help="requests in the window")
    a = p.parse_args()
    print(f"{a.target:g}% over {a.days:g} days = "
          f"{allowed_minutes(a.target, a.days):.1f} minutes of bad time")
    if a.requests:
        print(f"{a.target:g}% of {a.requests} requests = "
              f"{allowed_requests(a.target, a.requests):.0f} bad requests allowed")
