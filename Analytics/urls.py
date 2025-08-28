from django.urls import path
from .views import *
from django.conf.urls.static import static
app_name = "analyst" 
urlpatterns = [
    path('data_export/', export_user_information_data, name='export_user_information_data'),
    path('selection/', select_data_to_export, name='select_data_to_export'),
    path('user-summary/', user_information_summary, name='user_information_summary'),
    path('toggle-analyst-group/', toggle_analyst_group, name='toggle_analyst_group'),
    path('user-detail/<int:user_id>/', user_information_detail, name='user_details'),
]

# Serving media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serving static files during development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)