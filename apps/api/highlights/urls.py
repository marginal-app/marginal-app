from django.urls import path

from . import views

urlpatterns = [
    path("highlights", views.highlights_view),
    path("highlights/<uuid:id>", views.highlight_detail_view),
    path("bookmarks", views.bookmarks_view),
    path("catalogs", views.catalogs_view),
    path("sync/pull", views.sync_pull_view),
    path("sync/push", views.sync_push_view),
    path("ping", views.ping_view),
]
