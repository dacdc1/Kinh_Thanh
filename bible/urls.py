from django.urls import path
from . import views

app_name = 'bible'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('tim-kiem/', views.search_view, name='search'),
    path('ke-hoach-doc-365-ngay/', views.reading_plan_view, name='reading_plan'),
    path('ke-hoach-doc/toggle/<int:day_id>/', views.toggle_plan_day, name='toggle_plan_day'),
    path('tu-sach-ca-nhan/', views.my_library_view, name='my_library'),
    path('api/bookmark/<int:verse_id>/', views.api_toggle_bookmark, name='api_toggle_bookmark'),
    path('api/highlight/<int:verse_id>/', views.api_save_highlight, name='api_save_highlight'),
    path('api/note/<int:verse_id>/', views.api_save_note, name='api_save_note'),
    path('<slug:book_slug>/', views.reader_view, name='reader_book'),
    path('<slug:book_slug>/chuong-<int:chapter_number>/', views.reader_view, name='reader'),
]
