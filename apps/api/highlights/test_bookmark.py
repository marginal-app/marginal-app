import json
import uuid

import pytest

from highlights.models import Catalog, CatalogMembership, Highlight


def _post_bookmark(
    client,
    page_key: str,
    catalog: dict | None = None,
    *,
    auth_headers: dict[str, str],
):
    payload: dict = {"pageKey": page_key}
    if catalog is not None:
        payload["catalog"] = catalog
    return client.post(
        "/api/bookmarks",
        data=json.dumps(payload),
        content_type="application/json",
        headers=auth_headers,
    )


def _post_highlight(client, page_key: str, *, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/highlights",
        data=json.dumps(
            {
                "id": str(uuid.uuid4()),
                "pageKey": page_key,
                "quote": "q",
                "color": "#fff",
            }
        ),
        content_type="application/json",
        headers=auth_headers,
    )
    assert response.status_code == 201


@pytest.mark.django_db
def test_bookmark_post_points_at_one_catalog_row(client, auth_headers) -> None:
    response = _post_bookmark(
        client,
        "https://example.com/item?id=321#comments",
        auth_headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["pageKey"] == "https://example.com/item?id=321"
    assert body["bookmarked"] is True

    assert Catalog.objects.count() == 1
    assert CatalogMembership.objects.count() == 1
    membership = CatalogMembership.objects.get()
    assert membership.catalog.query == "?id=321"
    assert membership.bookmarked is True


@pytest.mark.django_db
def test_second_bookmark_on_same_page_is_the_same_row(client, auth_headers) -> None:
    first = _post_bookmark(client, "https://example.com/item?id=321", auth_headers=auth_headers)
    second = _post_bookmark(client, "https://example.com/item?id=321#x", auth_headers=auth_headers)
    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    assert CatalogMembership.objects.count() == 1
    assert Catalog.objects.count() == 1


@pytest.mark.django_db
def test_bookmark_and_highlight_share_the_catalog_row(client, auth_headers) -> None:
    _post_highlight(client, "https://example.com/item?id=321", auth_headers=auth_headers)
    _post_bookmark(client, "https://example.com/item?id=321", auth_headers=auth_headers)

    assert Catalog.objects.count() == 1
    assert CatalogMembership.objects.count() == 1
    assert Highlight.objects.count() == 1
    membership = CatalogMembership.objects.get()
    assert membership.catalog_id == Catalog.objects.get().id
    assert membership.bookmarked is True


@pytest.mark.django_db
def test_bookmark_post_writes_membership_title_and_description(client, auth_headers) -> None:
    response = _post_bookmark(
        client,
        "https://example.com/item?id=321",
        catalog={"title": "The item", "description": "Saved without a quote."},
        auth_headers=auth_headers,
    )
    assert response.status_code == 201
    row = CatalogMembership.objects.get()
    assert row.title == "The item"
    assert row.description == "Saved without a quote."
