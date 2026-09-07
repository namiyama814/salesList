from saleslist.normalizers import dm_status


def test_dm_status_only_uses_explicit_platform_flag():
    assert dm_status({"can_dm": True}) == "available"
    assert dm_status({"can_message": False}) == "unavailable"
    assert dm_status({"username": "no-flag"}) == "unknown"
