import uuid

from django.db import models

from .page_key import page_identity_from_page_key


class Catalog(models.Model):
    origin = models.TextField()
    path = models.TextField()
    query = models.TextField(blank=True, default="")
    title = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
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
    def upsert_from_page_key(
        cls,
        page_key: str,
        *,
        title: str = "",
        description: str = "",
    ) -> "Catalog":
        identity = page_identity_from_page_key(page_key)
        row, created = cls.objects.get_or_create(
            origin=identity.origin,
            path=identity.path,
            query=identity.query,
            defaults={"title": title, "description": description},
        )
        if not created:
            fields = ["updated_at"]
            if title:
                row.title = title
                fields.append("title")
            if description:
                row.description = description
                fields.append("description")
            row.save(update_fields=fields)
        return row


class Bookmark(models.Model):
    catalog = models.OneToOneField(
        Catalog,
        on_delete=models.CASCADE,
        related_name="bookmark",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def upsert_from_page_key(
        cls,
        page_key: str,
        *,
        title: str = "",
        description: str = "",
    ) -> tuple["Bookmark", bool]:
        catalog = Catalog.upsert_from_page_key(
            page_key,
            title=title,
            description=description,
        )
        row, created = cls.objects.get_or_create(catalog=catalog)
        if not created:
            row.save(update_fields=["updated_at"])
        return row, created

    def to_dict(self) -> dict:
        page_key = self.catalog.origin + self.catalog.path + self.catalog.query
        return {
            "id": self.id,
            "pageKey": page_key,
            "createdAt": int(self.created_at.timestamp() * 1000),
            "updatedAt": int(self.updated_at.timestamp() * 1000),
        }


class Highlight(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page_key = models.TextField(db_index=True)
    quote = models.TextField()
    prefix = models.TextField(blank=True, default="")
    suffix = models.TextField(blank=True, default="")
    color = models.CharField(max_length=32)
    comment = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
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
            "createdAt": int(self.created_at.timestamp() * 1000),
            "updatedAt": int(self.updated_at.timestamp() * 1000),
        }
