import json
import uuid

import pytest

from highlights.models import Catalog, CatalogMembership, Highlight


def _post_highlight(
    client,
    page_key: str,
    quote: str = "q",
    catalog: dict | None = None,
    *,
    auth_headers: dict[str, str],
    highlight_id: uuid.UUID | None = None,
) -> dict:
    payload: dict = {
        "id": str(highlight_id or uuid.uuid4()),
        "pageKey": page_key,
        "quote": quote,
        "color": "#fff",
    }
    if catalog is not None:
        payload["catalog"] = catalog
    response = client.post(
        "/api/highlights",
        data=json.dumps(payload),
        content_type="application/json",
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.django_db
def test_highlight_post_upserts_catalog_row(client, auth_headers) -> None:
    _post_highlight(
        client,
        "https://example.com/item?id=321#comments",
        auth_headers=auth_headers,
    )

    row = Catalog.objects.get()
    assert row.origin == "https://example.com"
    assert row.path == "/item"
    assert row.query == "?id=321"
    assert CatalogMembership.objects.get().bookmarked is False


@pytest.mark.django_db
def test_second_highlight_on_same_page_does_not_duplicate_catalog(client, auth_headers) -> None:
    _post_highlight(
        client, "https://example.com/item?id=321", quote="one", auth_headers=auth_headers
    )
    _post_highlight(
        client, "https://example.com/item?id=321#x", quote="two", auth_headers=auth_headers
    )

    assert Catalog.objects.count() == 1
    assert CatalogMembership.objects.count() == 1
    assert Highlight.objects.count() == 2


@pytest.mark.django_db
def test_different_query_creates_another_catalog_row(client, auth_headers) -> None:
    _post_highlight(client, "https://example.com/item?id=321", auth_headers=auth_headers)
    _post_highlight(client, "https://example.com/item?id=322", auth_headers=auth_headers)

    keys = set(Catalog.objects.values_list("origin", "path", "query"))
    assert keys == {
        ("https://example.com", "/item", "?id=321"),
        ("https://example.com", "/item", "?id=322"),
    }


@pytest.mark.django_db
def test_highlight_post_writes_membership_title_and_description(client, auth_headers) -> None:
    _post_highlight(
        client,
        "https://example.com/item?id=321",
        catalog={"title": "The item", "description": "A page about the item."},
        auth_headers=auth_headers,
    )

    row = CatalogMembership.objects.get()
    assert row.title == "The item"
    assert row.description == "A page about the item."


@pytest.mark.django_db
def test_later_highlight_does_not_wipe_membership_meta_with_empty(client, auth_headers) -> None:
    _post_highlight(
        client,
        "https://example.com/item?id=321",
        quote="one",
        catalog={"title": "The item", "description": "Kept."},
        auth_headers=auth_headers,
    )
    _post_highlight(
        client, "https://example.com/item?id=321", quote="two", auth_headers=auth_headers
    )

    row = CatalogMembership.objects.get()
    assert row.title == "The item"
    assert row.description == "Kept."


@pytest.mark.django_db
def test_later_highlight_refreshes_membership_meta_when_sent(client, auth_headers) -> None:
    _post_highlight(
        client,
        "https://example.com/item?id=321",
        quote="one",
        catalog={"title": "Old", "description": "Old desc."},
        auth_headers=auth_headers,
    )
    _post_highlight(
        client,
        "https://example.com/item?id=321",
        quote="two",
        catalog={"title": "New", "description": "New desc."},
        auth_headers=auth_headers,
    )

    row = CatalogMembership.objects.get()
    assert row.title == "New"
    assert row.description == "New desc."


@pytest.mark.django_db
def test_highlight_post_requires_client_id(client, auth_headers) -> None:
    response = client.post(
        "/api/highlights",
        data=json.dumps({"pageKey": "https://example.com/", "quote": "q", "color": "#fff"}),
        content_type="application/json",
        headers=auth_headers,
    )
    assert response.status_code == 400
