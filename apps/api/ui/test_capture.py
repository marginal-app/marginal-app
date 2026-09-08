from pathlib import Path

from ui.capture import dest_path, silhouette_url


def test_silhouette_url_strips_trailing_slash():
    assert (
        silhouette_url("http://127.0.0.1:8000/", "empty-state")
        == "http://127.0.0.1:8000/dev/components/empty-state/"
    )


def test_dest_path_uses_the_slug():
    assert dest_path(Path("/tmp/sil"), "button-default") == Path("/tmp/sil/button-default.png")
