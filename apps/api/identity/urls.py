from django.urls import path

from identity import views

urlpatterns = [
    path("login/", views.login_view, name="identity_login"),
    path("logout/", views.logout_view, name="identity_logout"),
    path("settings/", views.settings_view, name="identity_settings"),
    path("settings/token/", views.issue_token_view, name="identity_token"),
]
