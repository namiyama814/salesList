from saleslist.collector import collect_target
from saleslist.config import Settings
from saleslist.csv_io import CsvWriter
from saleslist.errors import NetworkError
from saleslist.models import Follower


class FakeClient:
    def __init__(self, followers, fail_once=False):
        self.followers_ = followers
        self.fail_once = fail_once
        self.calls = 0

    def followers(self, target):
        self.calls += 1
        for index, follower in enumerate(self.followers_):
            if self.fail_once and self.calls == 1 and index == 1:
                raise NetworkError("temporary failure")
            yield follower


def test_collection_skips_resumed_duplicates_and_honors_limit(tmp_path):
    client = FakeClient([
        Follower("x", "done"), Follower("x", "one"), Follower("x", "two"),
    ])
    with CsvWriter(tmp_path / "output.csv") as writer:
        count = collect_target(
            client, "target", writer, Settings(request_interval_seconds=0),
            limit=1, already_seen={"done"},
        )
    assert count == 1
    assert (tmp_path / "output.csv").read_text(encoding="utf-8").count("\n") == 2


def test_collection_retries_network_error_without_duplicate_rows(tmp_path):
    client = FakeClient([Follower("x", "one"), Follower("x", "two")], fail_once=True)
    with CsvWriter(tmp_path / "output.csv") as writer:
        count = collect_target(
            client, "target", writer,
            Settings(request_interval_seconds=0, max_retries=1, retry_delay_seconds=0), limit=None,
        )
    assert count == 2
    assert client.calls == 2
    assert "one" in (tmp_path / "output.csv").read_text(encoding="utf-8")
    assert "two" in (tmp_path / "output.csv").read_text(encoding="utf-8")
