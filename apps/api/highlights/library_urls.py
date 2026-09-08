from django.urls import path

from highlights import library_views
from highlights.components.highlight_card.highlight_card import highlight_card_edit_view

urlpatterns = [
    path("library/", library_views.library_highlights_view, name="library_highlights"),
    path("library/settings", library_views.library_settings_view, name="library_settings"),
    path(
        "library/highlights/<uuid:highlight_id>/comment",
        highlight_card_edit_view,
        name="highlight_comment",
    ),
]
