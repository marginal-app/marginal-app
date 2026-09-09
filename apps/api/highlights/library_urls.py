from django.urls import path

from highlights import catalog_views, library_views
from highlights.components.highlight_card.highlight_card import highlight_card_edit_view

urlpatterns = [
    path("catalog/", catalog_views.catalog_desk_view, name="catalog_desk"),
    path(
        "catalog/<int:catalog_id>/",
        catalog_views.catalog_desk_detail_view,
        name="catalog_desk_detail",
    ),
    path("library/", library_views.library_highlights_view, name="library_highlights"),
    path("library/settings", library_views.library_settings_view, name="library_settings"),
    path(
        "library/highlights/<uuid:highlight_id>/comment",
        highlight_card_edit_view,
        name="highlight_comment",
    ),
]
