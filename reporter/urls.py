from django.urls import path
from .views import generate_overall_report
from django.conf.urls.static import static
from django.conf import settings
app_name = 'reporter'
urlpatterns = [
    path("", generate_overall_report, name="GenerateOverallReport"),
]

# Serving media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serving static files during development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)