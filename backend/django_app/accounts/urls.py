from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path("register/", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", views.user_profile, name="profile"),
    path("consent/update/", views.update_consent, name="update_consent"),
    path("account/delete/", views.request_account_deletion, name="delete_account"),
    path("data/export/", views.export_user_data, name="export_data"),
]
