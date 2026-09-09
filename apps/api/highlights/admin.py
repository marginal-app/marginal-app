from django.contrib import admin

from .models import Bookmark, Catalog, Highlight

admin.site.register(Bookmark)
admin.site.register(Catalog)
admin.site.register(Highlight)
