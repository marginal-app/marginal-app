import json
import uuid

import pytest

from highlights.models import Catalog, CatalogMembership, Highlight
from identity.tokens import seed_dev_user


def _post_highlight(client, *, auth_headers: dict[str, str], **payload) -> dict:
    body = {
        "id": str(uuid.uuid4()),
        "pageKey": "https://example.com/item?id=321",
        "quote": "q",
        "color": "#fff",
        **payload,
    }
    response = client.post(
        "/api/highlights",
        data=json.dumps(body),
        content_type="application/json",
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.django_db
def test_highlights_are_scoped_to_the_bearer_user(client, auth_headers, other_auth_headers) -> None:
    _post_highlight(client, auth_headers=auth_headers, quote="mine")
    _post_highlight(client, auth_headers=other_auth_headers, quote="theirs")

    mine = client.get("/api/highlights", headers=auth_headers)
    theirs = client.get("/api/highlights", headers=other_auth_headers)
    assert [row["quote"] for row in mine.json()] == ["mine"]
    assert [row["quote"] for row in theirs.json()] == ["theirs"]


@pytest.mark.django_db
def test_cannot_patch_another_users_highlight(client, auth_headers, other_auth_headers) -> None:
    created = _post_highlight(client, auth_headers=auth_headers)
    response = client.patch(
        f"/api/highlights/{created['id']}",
        data=json.dumps({"comment": "stolen"}),
        content_type="application/json",
        headers=other_auth_headers,
    )
    assert response.status_code == 404
    stored = Highlight.objects.get(id=created["id"])
    assert stored.comment == ""


@pytest.mark.django_db
def test_cannot_push_a_highlight_id_owned_by_another_user(
    client, auth_headers, other_auth_headers
) -> None:
    highlight_id = str(uuid.uuid4())
    _post_highlight(client, auth_headers=auth_headers, id=highlight_id)
    response = client.post(
        "/api/sync/push",
        data=json.dumps(
            {
                "memberships": [],
                "highlights": [
                    {
                        "id": highlight_id,
                        "pageKey": "https://example.com/item?id=321",
                        "quote": "stolen",
                        "color": "#fff",
                    }
                ],
            }
        ),
        content_type="application/json",
        headers=other_auth_headers,
    )
    assert response.status_code == 409
    assert Highlight.objects.get(id=highlight_id).quote == "q"


@pytest.mark.django_db
def test_pull_returns_only_the_bearer_users_rows(client, auth_headers, other_auth_headers) -> None:
    _post_highlight(client, auth_headers=auth_headers, quote="mine")
    _post_highlight(client, auth_headers=other_auth_headers, quote="theirs")

    pulled = client.get("/api/sync/pull", headers=auth_headers)
    assert pulled.status_code == 200
    body = pulled.json()
    assert [row["quote"] for row in body["highlights"]] == ["mine"]
    assert len(body["memberships"]) == 1


@pytest.mark.django_db
def test_pull_since_excludes_older_rows(client, auth_headers) -> None:
    first = _post_highlight(client, auth_headers=auth_headers, quote="old")
    later = client.get("/api/sync/pull", headers=auth_headers).json()
    cursor = later["cursor"]
    _post_highlight(client, auth_headers=auth_headers, quote="new")

    incremental = client.get("/api/sync/pull", {"since": cursor}, headers=auth_headers)
    quotes = [row["quote"] for row in incremental.json()["highlights"]]
    assert "old" not in quotes
    assert "new" in quotes
    assert first["id"] not in {row["id"] for row in incremental.json()["highlights"]}


@pytest.mark.django_db
def test_push_keeps_client_highlight_id_and_stamps_server_time(client, auth_headers) -> None:
    highlight_id = str(uuid.uuid4())
    created_at = 1_700_000_000_000
    response = client.post(
        "/api/sync/push",
        data=json.dumps(
            {
                "memberships": [
                    {
                        "pageKey": "https://example.com/item?id=321",
                        "bookmarked": False,
                        "title": "The item",
                        "description": "A page.",
                    }
                ],
                "highlights": [
                    {
                        "id": highlight_id,
                        "pageKey": "https://example.com/item?id=321",
                        "quote": "q",
                        "prefix": "p",
                        "suffix": "s",
                        "color": "#fff",
                        "comment": "note",
                        "createdAt": created_at,
                    }
                ],
            }
        ),
        content_type="application/json",
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["highlights"][0]["id"] == highlight_id
    assert body["highlights"][0]["createdAt"] == created_at
    assert body["highlights"][0]["updatedAt"] >= created_at
    stored = Highlight.objects.get(id=highlight_id)
    assert stored.user == seed_dev_user()
    membership = CatalogMembership.objects.get()
    assert membership.title == "The item"
    assert membership.bookmarked is False
    assert membership.note == ""
    assert body["memberships"][0]["note"] == ""


@pytest.mark.django_db
def test_push_empty_title_does_not_wipe_membership_meta(client, auth_headers) -> None:
    page_key = "https://example.com/item?id=321"
    client.post(
        "/api/sync/push",
        data=json.dumps(
            {
                "memberships": [
                    {
                        "pageKey": page_key,
                        "title": "Kept",
                        "description": "Also kept",
                    }
                ],
                "highlights": [],
            }
        ),
        content_type="application/json",
        headers=auth_headers,
    )
    client.post(
        "/api/sync/push",
        data=json.dumps(
            {
                "memberships": [{"pageKey": page_key, "title": "", "description": ""}],
                "highlights": [],
            }
        ),
        content_type="application/json",
        headers=auth_headers,
    )
    row = CatalogMembership.objects.get()
    assert row.title == "Kept"
    assert row.description == "Also kept"
    assert row.note == ""


@pytest.mark.django_db
def test_push_note_is_additive_and_omission_does_not_wipe(client, auth_headers) -> None:
    page_key = "https://example.com/item?id=321"
    client.post(
        "/api/sync/push",
        data=json.dumps(
            {
                "memberships": [
                    {
                        "pageKey": page_key,
                        "title": "Kept",
                        "description": "Also kept",
                        "note": "page note",
                    }
                ],
                "highlights": [],
            }
        ),
        content_type="application/json",
        headers=auth_headers,
    )
    client.post(
        "/api/sync/push",
        data=json.dumps(
            {
                "memberships": [{"pageKey": page_key, "title": "", "description": ""}],
                "highlights": [],
            }
        ),
        content_type="application/json",
        headers=auth_headers,
    )
    row = CatalogMembership.objects.get()
    assert row.note == "page note"


@pytest.mark.django_db
def test_same_page_has_one_catalog_across_users(client, auth_headers, other_auth_headers) -> None:
    _post_highlight(client, auth_headers=auth_headers)
    _post_highlight(client, auth_headers=other_auth_headers)
    assert Catalog.objects.count() == 1
    assert CatalogMembership.objects.count() == 2
