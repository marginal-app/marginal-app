import pytest

from identity.tokens import DEV_TOKEN, seed_dev_user


@pytest.fixture
def auth_headers(db):
    seed_dev_user()
    return {"Authorization": f"Bearer {DEV_TOKEN}"}


@pytest.fixture
def other_auth_headers(db):
    seed_dev_user(username="other", token="other-token")
    return {"Authorization": "Bearer other-token"}
