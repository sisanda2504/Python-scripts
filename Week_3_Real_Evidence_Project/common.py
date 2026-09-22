from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


TIME_FORMAT = "%Y/%m/%d %H:%M:%S"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Evidence file not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_time(value: str) -> datetime:
    return datetime.strptime(value.strip(), TIME_FORMAT)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, data) -> None:
    ensure_dir(path.parent)
    import json
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
