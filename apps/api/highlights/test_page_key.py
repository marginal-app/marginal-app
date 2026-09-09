import json

import pytest

from highlights.models import Highlight
from highlights.page_key import (
    canonicalize_page_key,
    page_identity_from_page_key,
    page_key_from_href,
)


def test_page_key_keeps_query_and_drops_hash() -> None:
    assert (
        page_key_from_href("https://example.com/item?id=321#comments")
        == "https://example.com/item?id=321"
    )


def test_page_key_treats_different_query_values_as_different_pages() -> None:
    assert page_key_from_href("https://example.com/item?id=321") == (
        "https://example.com/item?id=321"
    )
    assert page_key_from_href("https://example.com/item?id=322") == (
        "https://example.com/item?id=322"
    )


def test_page_key_uses_slash_for_origin_only_href() -> None:
    assert page_key_from_href("https://example.com") == "https://example.com/"


def test_page_key_from_href_rejects_non_url() -> None:
    assert page_key_from_href("not-a-url") is None


def test_page_identity_splits_origin_path_query() -> None:
    identity = page_identity_from_page_key("https://example.com/item?id=321#x")
    assert identity.origin == "https://example.com"
    assert identity.path == "/item"
    assert identity.query == "?id=321"
    assert identity.page_key == "https://example.com/item?id=321"


def test_legacy_non_url_page_key_stays_as_path() -> None:
    assert canonicalize_page_key("a") == "a"
    identity = page_identity_from_page_key("a")
    assert identity.origin == ""
    assert identity.path == "a"
    assert identity.query == ""
    assert identity.page_key == "a"


@pytest.mark.django_db
def test_highlights_post_canonicalizes_page_key(client, auth_headers) -> None:
    response = client.post(
        "/api/highlights",
        data=json.dumps(
            {
                "pageKey": "https://example.com/item?id=321#comments",
                "quote": "q",
                "color": "#fff",
            }
        ),
        content_type="application/json",
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["pageKey"] == "https://example.com/item?id=321"
    stored = Highlight.objects.get(id=body["id"])
    assert stored.page_key == "https://example.com/item?id=321"


@pytest.mark.django_db
def test_highlights_get_filters_by_canonical_page_key(client, auth_headers) -> None:
    Highlight.objects.create(
        page_key="https://example.com/item?id=321",
        quote="one",
        color="#fff",
    )
    Highlight.objects.create(
        page_key="https://example.com/item?id=322",
        quote="two",
        color="#fff",
    )

    matched = client.get(
        "/api/highlights",
        {"pageKey": "https://example.com/item?id=321#comments"},
        headers=auth_headers,
    )
    other = client.get(
        "/api/highlights",
        {"pageKey": "https://example.com/item?id=322"},
        headers=auth_headers,
    )
    assert matched.status_code == 200
    assert [row["quote"] for row in matched.json()] == ["one"]
    assert [row["quote"] for row in other.json()] == ["two"]
