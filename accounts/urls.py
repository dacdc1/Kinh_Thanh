from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
]
