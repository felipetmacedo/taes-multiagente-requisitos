import csv, os
from pathlib import Path


def read_issues(path, limit=None):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    return rows[:limit] if limit else rows


def done_keys(path, keys):
    if not os.path.exists(path):
        return set()
    return {tuple(r[k] for k in keys) for r in csv.DictReader(open(path, encoding="utf-8"))}


class Appender:
    """CSV append com flush por linha (retomável)."""

    def __init__(self, path, fields):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        new = not os.path.exists(path)
        self.f = open(path, "a", newline="", encoding="utf-8")
        self.w = csv.DictWriter(self.f, fieldnames=fields)
        if new:
            self.w.writeheader()

    def write(self, row):
        self.w.writerow(row)
        self.f.flush()
