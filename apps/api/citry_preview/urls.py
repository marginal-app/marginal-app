from django.urls import path

from citry_preview import views

urlpatterns = [
    path("citry/preview/", views.gallery_view, name="component_gallery"),
    path(
        "citry/preview/<slug:slug>/",
        views.silhouette_view,
        name="component_silhouette",
    ),
]
