#!/usr/bin/env python3
"""
Copy the most recent available lesson JSON into missing dates between start and end.
This avoids 404 on the frontend when historical dates are requested but not generated.

Usage:
  - Locally: python scripts/backfill_copy.py 2026-01-12 2026-01-15
  - In workflow: set INPUT_START_DATE and INPUT_END_DATE env vars and run script
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path("data")

def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date()

def find_most_recent_file():
    if not DATA_DIR.exists():
        return None
    files = sorted([p for p in DATA_DIR.iterdir() if p.suffix == ".json"], reverse=True)
    return files[0] if files else None

def backfill(start_date, end_date):
    start = parse_date(start_date)
    end = parse_date(end_date)
    if start > end:
        start, end = end, start

    most_recent = find_most_recent_file()
    if not most_recent:
        print("No existing JSON files found to copy from. Aborting.")
        sys.exit(1)

    content = most_recent.read_text(encoding="utf-8")
    print(f"Using source file {most_recent.name} to backfill.")

    created = []
    for n in range((end - start).days + 1):
        d = start + timedelta(days=n)
        target = DATA_DIR / f"{d.isoformat()}.json"
        if target.exists():
            print(f"{target.name} already exists; skip.")
            continue
        target.write_text(content, encoding="utf-8")
        created.append(target.name)
        print(f"Created {target.name}")

    if created:
        print("Backfill created files:", created)
    else:
        print("No files created (all existed).")

if __name__ == "__main__":
    # params from argv or env
    if len(sys.argv) >= 3:
        s = sys.argv[1]
        e = sys.argv[2]
    else:
        import os
        s = os.getenv("INPUT_START_DATE", None)
        e = os.getenv("INPUT_END_DATE", None)
    if not s or not e:
        print("Usage: scripts/backfill_copy.py START_DATE END_DATE")
        print("Or set INPUT_START_DATE and INPUT_END_DATE environment variables.")
        sys.exit(2)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    backfill(s, e)


