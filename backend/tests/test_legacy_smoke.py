def test_legacy_ping_import_backend():
    from app.legacy.utils import ping
    assert ping() == "legacy:ok"
