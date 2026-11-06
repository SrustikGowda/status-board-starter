"""Note a change (deploy, config edit, rollback) with the time it happened.

    python3 slo/changes.py "deploy v2"
"""
import argparse
import time

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("description", nargs="+")
p.add_argument("--log", default="changes.log")
args = p.parse_args()

text = " ".join(args.description).replace("\n", " ")
with open(args.log, "a") as log:
    log.write(f"{time.time():.3f},{text}\n")
print(f"noted: {text}")
