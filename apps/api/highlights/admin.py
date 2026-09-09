from django.contrib import admin

from .models import Catalog, CatalogMembership, Highlight

admin.site.register(Catalog)
admin.site.register(CatalogMembership)
admin.site.register(Highlight)
