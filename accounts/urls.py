from django.urls import path
from django.conf.urls.static import static
from .views import *
app_name = "accounts"
urlpatterns = [
    path("", login_user, name="login"),
    path("password-reset/", password_reset_request, name="Password_reset"),
    path("logout_user", logout_user, name="logout"),
    path("user_settings", user_settings, name="User_settings"),
    path("register", register, name="Register"),
    path("password_change", password_change, name="Password_change"),
    path("password_change/done", password_change_done, name="password_change_done"),
    path("password-reset/done/", password_reset_done, name="password_reset_done"),
    path("password-reset/confirm/<uidb64>/<token>/", password_reset_confirm, name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        password_reset_complete,
        name="password_reset_complete",
    ),
]


# Serving media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serving static files during development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)