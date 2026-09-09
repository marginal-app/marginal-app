import json

import pytest

from highlights.models import Catalog, Highlight

AUTH = {"Authorization": "Bearer dev-token"}


def _post_highlight(client, page_key: str, quote: str = "q") -> dict:
    response = client.post(
        "/api/highlights",
        data=json.dumps(
            {
                "pageKey": page_key,
                "quote": quote,
                "color": "#fff",
            }
        ),
        content_type="application/json",
        headers=AUTH,
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.django_db
def test_highlight_post_upserts_catalog_row(client) -> None:
    _post_highlight(client, "https://example.com/item?id=321#comments")

    row = Catalog.objects.get()
    assert row.origin == "https://example.com"
    assert row.path == "/item"
    assert row.query == "?id=321"


@pytest.mark.django_db
def test_second_highlight_on_same_page_does_not_duplicate_catalog(client) -> None:
    _post_highlight(client, "https://example.com/item?id=321", quote="one")
    _post_highlight(client, "https://example.com/item?id=321#x", quote="two")

    assert Catalog.objects.count() == 1
    assert Highlight.objects.count() == 2


@pytest.mark.django_db
def test_different_query_creates_another_catalog_row(client) -> None:
    _post_highlight(client, "https://example.com/item?id=321")
    _post_highlight(client, "https://example.com/item?id=322")

    keys = set(Catalog.objects.values_list("origin", "path", "query"))
    assert keys == {
        ("https://example.com", "/item", "?id=321"),
        ("https://example.com", "/item", "?id=322"),
    }
