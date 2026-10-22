from .models import Book

_CACHED_BOOKS = None

def get_cached_books():
    global _CACHED_BOOKS
    if _CACHED_BOOKS is None:
        try:
            _CACHED_BOOKS = list(Book.objects.all().order_by('order_num'))
        except Exception:
            return []
    return _CACHED_BOOKS

def clear_books_cache():
    global _CACHED_BOOKS
    _CACHED_BOOKS = None

def canon_nav(request):
    """Context processor providing Catholic 73 books organized by groups for header/sidebar menus."""
    books = get_cached_books()
    
    ot_books = [b for b in books if b.testament == 'OT']
    nt_books = [b for b in books if b.testament == 'NT']
    
    # Guest reading stats from session
    guest_chapters_read = request.session.get('guest_chapters_read', [])
    guest_read_count = len(guest_chapters_read)
    
    import os
    has_google_oauth = bool(os.getenv('GOOGLE_CLIENT_ID', '').strip())
    has_facebook_oauth = bool(os.getenv('FACEBOOK_CLIENT_ID', '').strip())

    return {
        'all_books': books,
        'ot_books': ot_books,
        'nt_books': nt_books,
        'guest_read_count': guest_read_count,
        'guest_max_free': 3,
        'is_guest_limit_reached': (not request.user.is_authenticated) and (guest_read_count >= 3),
        'has_google_oauth': has_google_oauth,
        'has_facebook_oauth': has_facebook_oauth,
    }
