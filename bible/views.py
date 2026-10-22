import re
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import (
    Book, Chapter, Verse, Bookmark, Highlight, PersonalNote,
    ReadingPlan, ReadingPlanDay, UserReadingProgress, UserPlanProgress,
    remove_vietnamese_accents
)

def home_view(request):
    """Trang chủ hiển thị danh mục 73 cuốn Kinh Thánh Công Giáo chuẩn mực."""
    books = list(Book.objects.all().order_by('order_num'))
    
    ot_pentateuch = [b for b in books if b.group == 'Ngũ Thư']
    ot_history = [b for b in books if b.group == 'Lịch Sử']
    ot_wisdom = [b for b in books if b.group == 'Giáo Huấn']
    ot_prophets = [b for b in books if b.group == 'Ngôn Sứ']
    
    nt_gospels = [b for b in books if b.group == 'Tin Mừng']
    nt_acts = [b for b in books if b.group == 'Công Vụ']
    nt_pauline = [b for b in books if b.group == 'Thư Phaolô']
    nt_catholic = [b for b in books if b.group == 'Thư Chung']
    nt_revelation = [b for b in books if b.group == 'Khải Huyền']

    # Get sample popular verses for banner/daily bread
    popular_verse = Verse.objects.filter(
        chapter__book__code='Ga', chapter__number=3, verse_number=16
    ).select_related('chapter__book').first()
    if not popular_verse:
        popular_verse = Verse.objects.select_related('chapter__book').first()

    context = {
        'total_books': len(books),
        'ot_pentateuch': ot_pentateuch,
        'ot_history': ot_history,
        'ot_wisdom': ot_wisdom,
        'ot_prophets': ot_prophets,
        'nt_gospels': nt_gospels,
        'nt_acts': nt_acts,
        'nt_pauline': nt_pauline,
        'nt_catholic': nt_catholic,
        'nt_revelation': nt_revelation,
        'popular_verse': popular_verse,
    }
    return render(request, 'bible/index.html', context)

def reader_view(request, book_slug, chapter_number=1):
    """
    Giao diện đọc sách chuyên sâu (Reader View) với khả năng tùy biến hiển thị,
    chọn câu, highlight, bookmark, ghi chú và quản lý giới hạn đọc của khách vãng lai.
    """
    book = get_object_or_404(Book, slug=book_slug)
    chapter = get_object_or_404(Chapter, book=book, number=chapter_number)
    
    # Track guest reading limit (max 3 chapters per session without login)
    limit_reached = False
    guest_read_chapters = request.session.get('guest_chapters_read', [])
    
    if not request.user.is_authenticated:
        chapter_identifier = f"{book.slug}:{chapter.number}"
        if chapter_identifier not in guest_read_chapters:
            if len(guest_read_chapters) >= 3:
                limit_reached = True
            else:
                guest_read_chapters.append(chapter_identifier)
                request.session['guest_chapters_read'] = guest_read_chapters
                request.session.modified = True
    else:
        # Mark as read for authenticated member
        UserReadingProgress.objects.update_or_create(
            user=request.user,
            chapter=chapter,
            defaults={'completed': True, 'last_read_at': timezone.now()}
        )

    # Fetch verses
    verses_query = chapter.verses.all().order_by('verse_number')
    
    # If guest limit reached, restrict to first 3 verses as a preview
    if limit_reached:
        verses = verses_query[:3]
    else:
        verses = verses_query

    # Fetch user annotations if logged in
    user_bookmarks = set()
    user_highlights = {}
    user_notes = {}
    
    if request.user.is_authenticated:
        verse_ids = [v.id for v in verses]
        user_bookmarks = set(Bookmark.objects.filter(user=request.user, verse_id__in=verse_ids).values_list('verse_id', flat=True))
        
        for h in Highlight.objects.filter(user=request.user, verse_id__in=verse_ids):
            user_highlights[h.verse_id] = h.color
            
        for n in PersonalNote.objects.filter(user=request.user, verse_id__in=verse_ids):
            user_notes[n.verse_id] = n.content

    # Previous and Next chapter calculations (eager load book to avoid N+1 queries)
    prev_chapter = Chapter.objects.filter(book=book, number=chapter_number - 1).select_related('book').first()
    next_chapter = Chapter.objects.filter(book=book, number=chapter_number + 1).select_related('book').first()
    
    # Cross-book navigation
    if not prev_chapter and book.order_num > 1:
        prev_book = Book.objects.filter(order_num=book.order_num - 1).first()
        if prev_book:
            prev_chapter = Chapter.objects.filter(book=prev_book, number=prev_book.total_chapters).select_related('book').first()
            
    if not next_chapter and book.order_num < 73:
        next_book = Book.objects.filter(order_num=book.order_num + 1).first()
        if next_book:
            next_chapter = Chapter.objects.filter(book=next_book, number=1).select_related('book').first()

    context = {
        'book': book,
        'chapter': chapter,
        'verses': verses,
        'limit_reached': limit_reached,
        'user_bookmarks': user_bookmarks,
        'user_highlights': user_highlights,
        'user_notes': user_notes,
        'prev_chapter': prev_chapter,
        'next_chapter': next_chapter,
        'all_chapters': book.chapters.all().order_by('number'),
    }
    return render(request, 'bible/reader.html', context)

def search_view(request):
    """
    Tìm kiếm thông minh:
    - Khi người dùng gõ CÓ DẤU: Lọc chính xác theo đúng dấu đó (VD: 'bàn' chỉ tìm đúng chữ 'bàn', không lẫn 'bạn'/'bán').
    - Khi người dùng gõ KHÔNG DẤU: Tìm kiếm mở rộng bao quát tất cả các dấu (VD: 'thien chua' tìm 'Thiên Chúa').
    - Hỗ trợ tra cứu chính xác theo ký hiệu câu (VD: Ga 3,16) và phân trang toàn bộ kết quả.
    """
    query = request.GET.get('q', '').strip()
    testament_filter = request.GET.get('testament', '')
    book_filter = request.GET.get('book', '')
    page_number = request.GET.get('page', 1)
    
    direct_match = None
    total_results_count = 0
    books_matched_count = 0
    page_obj = None
    
    if query:
        # 1. Tra cứu chính xác theo ký hiệu câu: VD "Ga 3, 16" hoặc "St 1, 1" hoặc "Mt 5:3"
        ref_match = re.match(r'^([1-3]?\s*[a-zA-Z0-9Đđ]+)\s*(\d+)[\,\:\.]\s*(\d+)$', query)
        if ref_match:
            b_code, ch_num, v_num = ref_match.groups()
            b_code_clean = b_code.replace(" ", "")
            direct_match = Verse.objects.filter(
                Q(chapter__book__code__iexact=b_code_clean) | Q(chapter__book__slug__icontains=remove_vietnamese_accents(b_code_clean)),
                chapter__number=int(ch_num),
                verse_number=int(v_num)
            ).select_related('chapter__book').first()

        # 2. Tìm kiếm thông minh: Phân biệt dấu khi có dấu, mở rộng khi không dấu
        clean_q = query.strip()
        if clean_q.startswith('"') and clean_q.endswith('"') and len(clean_q) > 2:
            phrase = clean_q.strip('"').strip()
            phrase_unaccent = remove_vietnamese_accents(phrase)
            if phrase.lower() != phrase_unaccent.lower():
                # Cụm từ có dấu: lọc chính xác theo dấu trong text
                verses_qs = Verse.objects.select_related('chapter__book').filter(
                    Q(text__icontains=phrase) | Q(text__icontains=phrase.lower())
                )
            else:
                # Cụm từ không dấu: lọc trên text_unaccent
                verses_qs = Verse.objects.select_related('chapter__book').filter(
                    text_unaccent__icontains=phrase_unaccent
                )
        else:
            words = [w for w in clean_q.split() if w.strip()]
            if words:
                query_filter = Q()
                for w in words:
                    w_low = w.lower()
                    w_un = remove_vietnamese_accents(w_low)
                    if w_low != w_un:
                        # Từ này CÓ DẤU -> Lọc chính xác theo dấu trong text (không phân biệt hoa/thường)
                        query_filter &= (
                            Q(text__icontains=w) |
                            Q(text__icontains=w_low) |
                            Q(text__icontains=w.title()) |
                            Q(text__icontains=w.upper())
                        )
                    else:
                        # Từ này KHÔNG DẤU -> Lọc trên text_unaccent để bao quát mọi dấu
                        query_filter &= Q(text_unaccent__icontains=w_un)
                        
                verses_qs = Verse.objects.select_related('chapter__book').filter(query_filter)
            else:
                verses_qs = Verse.objects.none()

        # 3. Áp dụng bộ lọc Cựu Ước / Tân Ước và Cuốn sách
        if testament_filter in ('OT', 'NT'):
            verses_qs = verses_qs.filter(chapter__book__testament=testament_filter)
            
        if book_filter:
            verses_qs = verses_qs.filter(chapter__book__slug=book_filter)
            
        # Sắp xếp chuẩn theo thứ tự quy điển Kinh Thánh (Sáng Thế -> Khải Huyền, theo chương và câu)
        verses_qs = verses_qs.order_by('chapter__book__order_num', 'chapter__number', 'verse_number')

        total_results_count = verses_qs.count()
        books_matched_count = verses_qs.values('chapter__book').distinct().count()

        # 4. Phân trang: hiển thị tất cả các kết quả mà không bị giới hạn (25 câu/trang)
        paginator = Paginator(verses_qs, 25)
        try:
            page_obj = paginator.get_page(page_number)
        except (PageNotAnInteger, EmptyPage):
            page_obj = paginator.get_page(1)

    context = {
        'query': query,
        'page_obj': page_obj,
        'results': page_obj if page_obj else [],
        'direct_match': direct_match,
        'results_count': total_results_count,
        'total_results_count': total_results_count,
        'books_matched_count': books_matched_count,
        'testament_filter': testament_filter,
        'book_filter': book_filter,
        'books': Book.objects.all().order_by('order_num'),
    }
    return render(request, 'bible/search.html', context)

def reading_plan_view(request):
    """Kế hoạch đọc toàn bộ Kinh Thánh 365 ngày (1 năm)."""
    plan = ReadingPlan.objects.first()
    if not plan:
        return redirect('bible:home')
        
    days = plan.days.all().order_by('day_number')
    
    # Calculate current day of year
    now = datetime.now()
    current_day_number = now.timetuple().tm_yday
    if current_day_number > 365:
        current_day_number = 365
        
    user_completed_days = set()
    if request.user.is_authenticated:
        user_completed_days = set(
            UserPlanProgress.objects.filter(user=request.user, completed=True)
            .values_list('plan_day__day_number', flat=True)
        )

    context = {
        'plan': plan,
        'days': days,
        'current_day_number': current_day_number,
        'user_completed_days': user_completed_days,
        'completion_percent': round((len(user_completed_days) / 365) * 100, 1) if user_completed_days else 0,
    }
    return render(request, 'bible/reading_plan.html', context)

@login_required
@require_POST
def toggle_plan_day(request, day_id):
    """Đánh dấu đã hoàn thành hoặc chưa hoàn thành ngày đọc (Yêu cầu đăng nhập)."""
    plan_day = get_object_or_404(ReadingPlanDay, id=day_id)
    progress, created = UserPlanProgress.objects.get_or_create(user=request.user, plan_day=plan_day)
    
    progress.completed = not progress.completed
    progress.completed_at = timezone.now() if progress.completed else None
    progress.save()
    
    total_completed = UserPlanProgress.objects.filter(user=request.user, completed=True).count()
    return JsonResponse({
        'success': True,
        'completed': progress.completed,
        'total_completed': total_completed,
        'percent': round((total_completed / 365) * 100, 1)
    })

@login_required
@require_POST
def api_toggle_bookmark(request, verse_id):
    """API lưu hoặc bỏ bookmark (Đánh dấu câu)."""
    verse = get_object_or_404(Verse, id=verse_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, verse=verse)
    if not created:
        bookmark.delete()
        saved = False
    else:
        saved = True
    return JsonResponse({'success': True, 'saved': saved})

@login_required
@require_POST
def api_save_highlight(request, verse_id):
    """API bôi màu highlight cho câu kinh thánh."""
    color = request.POST.get('color', 'yellow')
    verse = get_object_or_404(Verse, id=verse_id)
    
    valid_colors = set(dict(Highlight.COLOR_CHOICES).keys())
    if color != 'none' and color not in valid_colors:
        return JsonResponse({'success': False, 'error': 'Màu bôi không hợp lệ'}, status=400)
    
    if color == 'none':
        Highlight.objects.filter(user=request.user, verse=verse).delete()
        return JsonResponse({'success': True, 'color': 'none'})
        
    highlight, created = Highlight.objects.update_or_create(
        user=request.user,
        verse=verse,
        defaults={'color': color}
    )
    return JsonResponse({'success': True, 'color': color})

@login_required
@require_POST
def api_save_note(request, verse_id):
    """API lưu ghi chú suy niệm cá nhân."""
    content = request.POST.get('content', '').strip()
    if len(content) > 5000:
        return JsonResponse({'success': False, 'error': 'Ghi chú không được vượt quá 5.000 ký tự'}, status=400)
        
    verse = get_object_or_404(Verse, id=verse_id)
    
    if not content:
        PersonalNote.objects.filter(user=request.user, verse=verse).delete()
        return JsonResponse({'success': True, 'deleted': True})
        
    note, created = PersonalNote.objects.update_or_create(
        user=request.user,
        verse=verse,
        defaults={'content': content}
    )
    return JsonResponse({'success': True, 'content': note.content})

@login_required
def my_library_view(request):
    """Trang quản lý cá nhân: Tủ sách, Bookmark, Highlight, Ghi chú, Lịch sử đọc."""
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('verse__chapter__book')
    highlights = Highlight.objects.filter(user=request.user).select_related('verse__chapter__book')
    notes = PersonalNote.objects.filter(user=request.user).select_related('verse__chapter__book')
    reading_history = UserReadingProgress.objects.filter(user=request.user).select_related('chapter__book').order_by('-last_read_at')[:20]
    
    context = {
        'bookmarks': bookmarks,
        'highlights': highlights,
        'notes': notes,
        'reading_history': reading_history,
    }
    return render(request, 'bible/my_library.html', context)
