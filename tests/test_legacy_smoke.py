
def test_legacy_ping_import():
    try:
        from backend.app.legacy.utils import ping as ping_backend  # pragma: no cover
        assert ping_backend() == "legacy:ok"
        return
    except ImportError:
        pass
    from app.legacy.utils import ping as ping_app
    assert ping_app() == "legacy:ok"
