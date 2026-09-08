from django.urls import path

from . import views

urlpatterns = [
    path("highlights", views.highlights_view),
    path("highlights/<uuid:id>", views.highlight_detail_view),
    path("ping", views.ping_view),
]
