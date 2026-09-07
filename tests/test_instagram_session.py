from saleslist.instagram.client import InstagramClient


def test_session_id_is_preferred_over_password_login(monkeypatch, tmp_path):
    calls = []

    class FakeClient:
        def load_settings(self, path):
            calls.append(("load", path))

        def login_by_sessionid(self, session_id):
            calls.append(("session", session_id))
            return True

        def login(self, username, password):
            calls.append(("password", username, password))

        def dump_settings(self, path):
            calls.append(("dump", path))

    monkeypatch.setenv("INSTAGRAM_SESSION_ID", "browser-session")
    monkeypatch.setattr("instagrapi.Client", FakeClient)
    client = InstagramClient(tmp_path / "sessions")._login()
    assert isinstance(client, FakeClient)
    assert ("session", "browser-session") in calls
    assert not any(call[0] == "password" for call in calls)
