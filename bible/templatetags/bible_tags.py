from django import template
import re
from django.utils.html import escape, mark_safe
from bible.models import remove_vietnamese_accents

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Safely get value from dictionary by key in Django templates."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def in_set(value, collection):
    """Check if value exists in a set, list, or iterable collection."""
    if collection is None:
        return False
    try:
        return value in collection
    except TypeError:
        return False

@register.filter(is_safe=True)
def highlight_keywords(text, query):
    """
    Tô màu làm nổi bật các từ khóa tìm kiếm:
    - Nếu người dùng gõ CÓ DẤU: Chỉ highlight đúng từ có dấu tương ứng (VD: 'bàn' chỉ highlight 'bàn', không highlight 'bạn').
    - Nếu người dùng gõ KHÔNG DẤU: Highlight tất cả các biến thể có dấu (VD: 'ban' highlight cả 'bàn', 'bạn', 'bán').
    """
    if not query or not text:
        return escape(text)
    
    clean_q = query.strip()
    if clean_q.startswith('"') and clean_q.endswith('"') and len(clean_q) > 2:
        raw_words = [clean_q.strip('"').strip()]
    else:
        raw_words = [w for w in clean_q.split() if w.strip()]
        
    if not raw_words:
        return escape(text)

    accented_words = set()
    unaccented_words = set()
    for w in raw_words:
        w_low = w.lower()
        w_un = remove_vietnamese_accents(w_low)
        if w_low != w_un:
            accented_words.add(w_low)
        else:
            unaccented_words.add(w_un)

    tokens = re.split(r'(\s+|[^\w\s]+)', text)
    highlighted = []
    for t in tokens:
        if not t:
            continue
        t_low = t.lower()
        t_un = remove_vietnamese_accents(t_low)
        
        is_match = False
        if t_low in accented_words:
            is_match = True
        elif t_un in unaccented_words:
            is_match = True

        if is_match:
            highlighted.append(f'<mark class="search-highlight">{escape(t)}</mark>')
        else:
            highlighted.append(escape(t))
            
    return mark_safe(''.join(highlighted))
