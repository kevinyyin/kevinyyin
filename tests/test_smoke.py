def test_fixture(contrib):
    assert contrib["current_streak"] == {"length": 40, "start": "2026-10-15", "end": "2026-11-23"}
    assert contrib["days"][-1]["date"] == "2026-11-24"
