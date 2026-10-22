import platform
from datetime import timedelta
import django
from django.conf import settings
from django.db import connection
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from bible.models import (
    Book, Chapter, Verse, Bookmark, Highlight, PersonalNote,
    UserReadingProgress, UserPlanProgress, ReadingPlan
)

@login_required
def profile_view(request):
    """Trang thông tin tài khoản, thống kê tiến độ đọc và thành tích cá nhân."""
    total_chapters_read = UserReadingProgress.objects.filter(user=request.user, completed=True).count()
    total_plan_days_done = UserPlanProgress.objects.filter(user=request.user, completed=True).count()
    total_bookmarks = Bookmark.objects.filter(user=request.user).count()
    total_highlights = Highlight.objects.filter(user=request.user).count()
    total_notes = PersonalNote.objects.filter(user=request.user).count()

    # Catholic Bible has 1,328 chapters across 73 books
    progress_percentage = round((total_chapters_read / 1328) * 100, 2)
    plan_percentage = round((total_plan_days_done / 365) * 100, 1)

    context = {
        'total_chapters_read': total_chapters_read,
        'total_plan_days_done': total_plan_days_done,
        'total_bookmarks': total_bookmarks,
        'total_highlights': total_highlights,
        'total_notes': total_notes,
        'progress_percentage': progress_percentage,
        'plan_percentage': plan_percentage,
    }
    return render(request, 'accounts/profile.html', context)


@staff_member_required(login_url='account_login')
def admin_dashboard_view(request):
    """
    Bảng điều khiển Quản trị Hệ thống Kinh Thánh Công Giáo (Admin Dashboard).
    Dành riêng cho Quản trị viên (Staff / Superuser) theo dõi người dùng,
    tiến độ dữ liệu Kinh Thánh và tương tác cộng đồng.
    """
    now = timezone.now()
    seven_days_ago = now - timedelta(days=7)

    # 1. Thống kê Người Dùng (Users)
    total_users = User.objects.count()
    new_users_7d = User.objects.filter(date_joined__gte=seven_days_ago).count()
    active_readers = UserReadingProgress.objects.values('user').distinct().count()
    plan_participants = UserPlanProgress.objects.values('user').distinct().count()

    recent_users = (
        User.objects.annotate(
            chapters_read=Count('reading_progress', distinct=True),
            notes_count=Count('notes', distinct=True),
            bookmarks_count=Count('bookmarks', distinct=True)
        )
        .order_by('-date_joined')[:12]
    )

    # 2. Thống kê Dữ Liệu Kinh Thánh (Scripture Data)
    total_books = Book.objects.count()
    ot_books_count = Book.objects.filter(testament='OT').count()
    nt_books_count = Book.objects.filter(testament='NT').count()
    total_chapters = Chapter.objects.count()
    total_verses = Verse.objects.count()
    books_with_verses = Book.objects.filter(chapters__verses__isnull=False).distinct().count()

    # Tổng số câu Kinh Thánh Công Giáo trọn bộ ước tính khoảng 35.500 câu
    estimated_verses = 35500
    verse_fill_percentage = round((total_verses / estimated_verses) * 100, 1) if total_verses else 0

    # 3. Thống kê Tương tác (Engagement)
    total_bookmarks = Bookmark.objects.count()
    total_highlights = Highlight.objects.count()
    total_notes = PersonalNote.objects.count()
    total_read_events = UserReadingProgress.objects.filter(completed=True).count()
    total_plan_days_done = UserPlanProgress.objects.filter(completed=True).count()

    # Phân loại bôi màu theo màu sắc
    color_map = {
        'yellow': {'name': 'Vàng ấm', 'color': '#fef08a'},
        'green': {'name': 'Xanh lá', 'color': '#bbf7d0'},
        'blue': {'name': 'Xanh lam', 'color': '#bfdbfe'},
        'pink': {'name': 'Hồng nhạt', 'color': '#fbcfe8'},
        'purple': {'name': 'Tím phụng vụ', 'color': '#e9d5ff'},
    }
    highlight_color_stats = []
    raw_color_counts = dict(
        Highlight.objects.values('color').annotate(count=Count('id')).values_list('color', 'count')
    )
    for c_code, meta in color_map.items():
        count = raw_color_counts.get(c_code, 0)
        pct = round((count / total_highlights) * 100, 1) if total_highlights > 0 else 0
        highlight_color_stats.append({
            'code': c_code,
            'name': meta['name'],
            'hex': meta['color'],
            'count': count,
            'percentage': pct,
        })

    # 4. Top nội dung được tương tác nhiều nhất
    top_bookmarked_verses = (
        Verse.objects.annotate(count=Count('bookmarks'))
        .filter(count__gt=0)
        .select_related('chapter__book')
        .order_by('-count')[:5]
    )

    top_highlighted_verses = (
        Verse.objects.annotate(count=Count('highlights'))
        .filter(count__gt=0)
        .select_related('chapter__book')
        .order_by('-count')[:5]
    )

    recent_notes = (
        PersonalNote.objects.select_related('user', 'verse__chapter__book')
        .order_by('-updated_at')[:6]
    )

    # 5. Thông tin máy chủ & CSDL
    system_info = {
        'django_version': django.get_version(),
        'python_version': platform.python_version(),
        'db_vendor': connection.vendor.upper(),
        'debug_mode': settings.DEBUG,
        'server_time': now,
        'guest_max_free': getattr(settings, 'GUEST_MAX_FREE_CHAPTERS', 3),
    }

    context = {
        # Users
        'total_users': total_users,
        'new_users_7d': new_users_7d,
        'active_readers': active_readers,
        'plan_participants': plan_participants,
        'recent_users': recent_users,
        # Scripture
        'total_books': total_books,
        'ot_books_count': ot_books_count,
        'nt_books_count': nt_books_count,
        'total_chapters': total_chapters,
        'total_verses': total_verses,
        'books_with_verses': books_with_verses,
        'verse_fill_percentage': verse_fill_percentage,
        # Engagement
        'total_bookmarks': total_bookmarks,
        'total_highlights': total_highlights,
        'total_notes': total_notes,
        'total_read_events': total_read_events,
        'total_plan_days_done': total_plan_days_done,
        'highlight_color_stats': highlight_color_stats,
        'top_bookmarked_verses': top_bookmarked_verses,
        'top_highlighted_verses': top_highlighted_verses,
        'recent_notes': recent_notes,
        # System
        'system_info': system_info,
    }
    return render(request, 'accounts/admin_dashboard.html', context)
