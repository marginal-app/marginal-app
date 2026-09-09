import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from .clock import epoch_ms
from .page_key import page_identity_from_page_key


class Catalog(models.Model):
    origin = models.TextField()
    path = models.TextField()
    query = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["origin", "path", "query"],
                name="catalog_origin_path_query",
            ),
        ]

    @property
    def page_key(self) -> str:
        return f"{self.origin}{self.path}{self.query}"

    @classmethod
    def get_or_create_from_page_key(cls, page_key: str) -> "Catalog":
        identity = page_identity_from_page_key(page_key)
        row, _created = cls.objects.get_or_create(
            origin=identity.origin,
            path=identity.path,
            query=identity.query,
        )
        return row


class CatalogMembership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="catalog_memberships",
    )
    catalog = models.ForeignKey(
        Catalog,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    bookmarked = models.BooleanField(default=False)
    title = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "catalog"],
                name="catalogmembership_user_catalog",
            ),
        ]

    @classmethod
    def upsert(
        cls,
        user,
        catalog: Catalog,
        *,
        title: str = "",
        description: str = "",
        bookmarked: bool | None = None,
    ) -> tuple["CatalogMembership", bool]:
        defaults: dict[str, object] = {"title": title, "description": description}
        if bookmarked is not None:
            defaults["bookmarked"] = bookmarked
        row, created = cls.objects.get_or_create(
            user=user,
            catalog=catalog,
            defaults=defaults,
        )
        if created:
            return row, True
        fields: list[str] = []
        if title:
            row.title = title
            fields.append("title")
        if description:
            row.description = description
            fields.append("description")
        if bookmarked is not None and row.bookmarked != bookmarked:
            row.bookmarked = bookmarked
            fields.append("bookmarked")
        if fields:
            row.save(update_fields=[*fields, "updated_at"])
        return row, False

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "pageKey": self.catalog.page_key,
            "bookmarked": self.bookmarked,
            "title": self.title,
            "description": self.description,
            "createdAt": epoch_ms(self.created_at),
            "updatedAt": epoch_ms(self.updated_at),
        }


class HighlightConflict(Exception):
    """The UUID already belongs to another user."""


class Highlight(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="highlights",
    )
    catalog = models.ForeignKey(
        Catalog,
        on_delete=models.CASCADE,
        related_name="highlights",
    )
    page_key = models.TextField(db_index=True)
    quote = models.TextField()
    prefix = models.TextField(blank=True, default="")
    suffix = models.TextField(blank=True, default="")
    color = models.CharField(max_length=32)
    comment = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "pageKey": self.page_key,
            "quote": self.quote,
            "prefix": self.prefix,
            "suffix": self.suffix,
            "color": self.color,
            "comment": self.comment,
            "createdAt": epoch_ms(self.created_at),
            "updatedAt": epoch_ms(self.updated_at),
        }

    @classmethod
    def upsert_for_user(
        cls,
        user,
        *,
        highlight_id: uuid.UUID,
        page_key: str,
        quote: str,
        color: str,
        prefix: str = "",
        suffix: str = "",
        comment: str = "",
        created_at=None,
        title: str = "",
        description: str = "",
    ) -> tuple["Highlight", bool]:
        catalog = Catalog.get_or_create_from_page_key(page_key)
        CatalogMembership.upsert(
            user,
            catalog,
            title=title,
            description=description,
        )
        existing = cls.objects.filter(id=highlight_id).first()
        if existing is not None and existing.user.pk != user.pk:
            raise HighlightConflict
        if existing is None:
            row = cls.objects.create(
                id=highlight_id,
                user=user,
                catalog=catalog,
                page_key=page_key,
                quote=quote,
                prefix=prefix,
                suffix=suffix,
                color=color,
                comment=comment,
                created_at=created_at or timezone.now(),
            )
            return row, True
        existing.catalog = catalog
        existing.page_key = page_key
        existing.quote = quote
        existing.prefix = prefix
        existing.suffix = suffix
        existing.color = color
        existing.comment = comment
        existing.save(
            update_fields=[
                "catalog",
                "page_key",
                "quote",
                "prefix",
                "suffix",
                "color",
                "comment",
                "updated_at",
            ]
        )
        return existing, False
