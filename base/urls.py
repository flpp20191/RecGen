from django.urls import include, path

# from base.forms import WasteForecastForm
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'base'
urlpatterns = [

    path("", views.home_redirect, name="home_redirect"),
    path("dashboard/", views.dashboard, name="Dashboard"),
]
# Serving media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serving static files during development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)