import csv

from saleslist.csv_io import CsvWriter, output_path, read_usernames
from saleslist.models import CSV_COLUMNS, Follower


def test_writer_uses_fixed_columns_and_writes_unknown_dm(tmp_path):
    path = tmp_path / "list.csv"
    with CsvWriter(path) as writer:
        writer.write(Follower(platform="instagram", username="Example", dm_status="unknown"))

    with path.open(encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    assert tuple(rows[0]) == CSV_COLUMNS
    assert rows[0]["username"] == "Example"
    assert rows[0]["dm_status"] == "unknown"
    assert rows[0]["collected_at"]


def test_resume_reads_case_insensitive_usernames(tmp_path):
    path = tmp_path / "previous.csv"
    with CsvWriter(path) as writer:
        writer.write(Follower(platform="x", username="AlreadyThere"))
    assert read_usernames(path) == {"alreadythere"}


def test_output_path_is_timestamped_and_sanitizes_target(tmp_path):
    path = output_path(tmp_path, "x", "@hello/world")
    assert path.parent == tmp_path
    assert path.name.startswith("x__hello_world_")
    assert path.suffix == ".csv"
