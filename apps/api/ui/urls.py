from django.urls import path

from citry_components.highlight_card.highlight_card import highlight_card_edit_view
from ui import views

urlpatterns = [
    path("citry/preview/", views.gallery_view, name="component_gallery"),
    path(
        "citry/preview/<slug:slug>/",
        views.silhouette_view,
        name="component_silhouette",
    ),
    path("library/", views.library_highlights_view, name="library_highlights"),
    path("library/settings", views.library_settings_view, name="library_settings"),
    path(
        "library/highlights/<uuid:highlight_id>/comment",
        highlight_card_edit_view,
        name="highlight_comment",
    ),
]
