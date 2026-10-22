from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-dashboard/', accounts_views.admin_dashboard_view, name='admin_dashboard_root'),
    path('accounts/', include('allauth.urls')),
    path('user/', include('accounts.urls')),
    path('', include('bible.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
