from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('apply/<int:job_pk>/', views.apply, name='apply'),
    path('success/', views.apply_success, name='apply_success'),
    path('<int:pk>/', views.application_detail, name='application_detail'),
]