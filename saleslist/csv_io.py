from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from .models import CSV_COLUMNS, Follower


def output_path(output_dir: Path, platform: str, target: str) -> Path:
    safe_target = "".join(char if char.isalnum() or char in "-_" else "_" for char in target)
    timestamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    return output_dir / f"{platform}_{safe_target}_{timestamp}.csv"


class CsvWriter:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._file = path.open("w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        self._writer.writeheader()
        self._file.flush()

    def write(self, follower: Follower) -> None:
        self._writer.writerow(follower.csv_row())
        self._file.flush()

    def close(self) -> None:
        self._file.close()

    def __enter__(self) -> "CsvWriter":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def read_usernames(path: Path) -> set[str]:
    if not path.is_file():
        raise FileNotFoundError(f"Resume CSV not found: {path}")
    with path.open(newline="", encoding="utf-8") as file:
        return {row["username"].casefold() for row in csv.DictReader(file) if row.get("username")}


def latest_output(output_dir: Path, platform: str, target: str) -> Path | None:
    pattern = f"{platform}_{target}_*.csv"
    files = sorted(output_dir.glob(pattern)) if output_dir.exists() else []
    return files[-1] if files else None
