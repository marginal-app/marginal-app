import hashlib
import secrets

from identity.models import ApiToken, User

DEV_TOKEN = "dev-token"


def hash_token(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()


def user_from_bearer(plaintext: str) -> User | None:
    if not plaintext:
        return None
    try:
        token = ApiToken.objects.select_related("user").get(key_hash=hash_token(plaintext))
    except ApiToken.DoesNotExist:
        return None
    if not token.user.is_active:
        return None
    return token.user


def issue_or_rotate(user: User, *, plaintext: str | None = None) -> str:
    raw = plaintext or secrets.token_urlsafe(32)
    ApiToken.objects.update_or_create(
        user=user,
        defaults={"key_hash": hash_token(raw), "hint": raw[-4:]},
    )
    return raw


def seed_dev_user(
    *,
    username: str = "dev",
    password: str = "dev",
    token: str = DEV_TOKEN,
) -> User:
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password(password)
        user.save(update_fields=["password"])
    issue_or_rotate(user, plaintext=token)
    return user
