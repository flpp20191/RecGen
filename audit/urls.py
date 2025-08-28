from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views
from .forms import WizardPage1
from .views import UpdateTrackingStatusView, UserWizardView
app_name = "audit"
urlpatterns = [
    path(
        "dataWizard/<str:pk>/",
        UserWizardView.as_view([WizardPage1]),
        name="Wizard",
    ),
    path("", views.audits, name="Audits"),
    path("update_tracking_status/", UpdateTrackingStatusView.as_view(), name="update_tracking_status"),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category-add'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category-edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),

    path('recommendations/', views.RecommendationListView.as_view(), name='recommendation-list'),
    path('recommendations/add/', views.RecommendationCreateView.as_view(), name='recommendation-add'),
    path('recommendations/<int:pk>/edit/', views.RecommendationUpdateView.as_view(), name='recommendation-edit'),
    path('recommendations/<int:pk>/delete/', views.RecommendationDeleteView.as_view(), name='recommendation-delete'),

    path('questions/', views.QuestionListView.as_view(), name='question-list'),
    path('questions/add/', views.QuestionCreateView.as_view(), name='question-add'),
    path('questions/<int:pk>/edit/', views.QuestionUpdateView.as_view(), name='question-edit'),
    path('questions/<int:pk>/delete/', views.QuestionDeleteView.as_view(), name='question-delete'),

    path("recommendations", views.recommendation_view, name="Recommendations"),
    path("fullcategories", views.categories, name='Categories'),

    path('data_upload/', views.upload_data_input_excel, name='upload_input_data_excel'),
    path('data_upload/<str:filename>/', views.download_template, name='download_template'),
] 

# Serving media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serving static files during development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)