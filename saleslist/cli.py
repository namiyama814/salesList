from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .clients import client_for
from .collector import collect_target
from .config import Settings
from .csv_io import CsvWriter, latest_output, output_path, read_usernames
from .errors import SalesListError


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Export Instagram or X followers to a CSV file.")
    result.add_argument("platform", choices=("instagram", "x"))
    result.add_argument("target", help="Source account username (without @)")
    result.add_argument("--limit", type=int, default=None, help="Maximum new rows to write (default: all).")
    result.add_argument("--output-dir", type=Path, default=Path("output"))
    result.add_argument(
        "--resume", nargs="?", const="auto", metavar="CSV",
        help="Skip usernames in CSV; without a path, use the latest matching output.",
    )
    return result


def main(argv: list[str] | None = None) -> None:
    args = parser().parse_args(argv)
    if args.limit is not None and args.limit < 1:
        parser().error("--limit must be at least 1")
    settings = Settings.load()
    resumed_from: Path | None = None
    if args.resume:
        resumed_from = latest_output(args.output_dir, args.platform, args.target) if args.resume == "auto" else Path(args.resume)
    try:
        seen = read_usernames(resumed_from) if resumed_from else set()
        path = output_path(args.output_dir, args.platform, args.target)
        client = client_for(args.platform, Path("sessions"), settings.request_interval_seconds)
        with CsvWriter(path) as writer:
            count = collect_target(client, args.target, writer, settings, limit=args.limit, already_seen=seen)
    except (SalesListError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(f"Wrote {count} followers to {path}")
    if resumed_from:
        print(f"Skipped usernames already present in {resumed_from}")
