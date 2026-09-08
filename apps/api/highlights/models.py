import uuid

from django.db import models


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
