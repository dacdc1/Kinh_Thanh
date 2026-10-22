import re
import time
import requests
from bs4 import BeautifulSoup, NavigableString
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core import serializers
from bible.models import Book, Chapter, Verse, remove_vietnamese_accents

class Command(BaseCommand):
    help = "Nạp trước nội dung tối đa 10 chương cho mỗi cuốn sách trong 73 cuốn Kinh Thánh Công Giáo từ nguồn augustino.net"

    def add_arguments(self, parser):
        parser.add_argument('--max-chapters', type=int, default=10, help='Số chương tối đa cần nạp cho mỗi sách (mặc định 10)')
        parser.add_argument('--workers', type=int, default=6, help='Số luồng tải song song (mặc định 6)')
        parser.add_argument('--force', action='store_true', help='Ghi đè nội dung nếu chương đã có câu')
        parser.add_argument('--book', type=str, default=None, help='Chỉ nạp cho 1 cuốn cụ thể (slug hoặc mã sách)')
        parser.add_argument('--export-fixture', type=str, default=None, help='Đường dẫn file json fixture để xuất sau khi nạp (VD: bible/fixtures/preload_10_chapters.json)')

    def get_chapter_url(self, book_slug, ch_num):
        """Xác định URL chuẩn trên augustino.net cho từng sách và chương."""
        if ch_num == 1:
            return f"https://augustino.net/{book_slug}"
        
        # Ngoại lệ đặc biệt của Thánh Vịnh và Ai Ca trên augustino.net
        if book_slug == 'sach-thanh-vinh':
            return f"https://augustino.net/thanh-vinh-{ch_num}"
        elif book_slug == 'sach-ai-ca':
            return f"https://augustino.net/sach-ai-ca-bai-{ch_num}"
        else:
            return f"https://augustino.net/{book_slug}-chuong-{ch_num}"

    def handle(self, *args, **options):
        max_ch = options['max_chapters']
        workers = options['workers']
        force = options['force']
        target_book = options['book']
        export_fixture = options['export_fixture']

        if target_book:
            books = list(Book.objects.filter(slug=target_book) | Book.objects.filter(code__iexact=target_book))
            if not books:
                self.stderr.write(f"Không tìm thấy sách với mã hoặc slug: {target_book}")
                return
        else:
            books = list(Book.objects.all().order_by('order_num'))

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"=== BẮT ĐẦU NẠP NỘI DUNG TỐI ĐA {max_ch} CHƯƠNG CHO {len(books)} CUỐN SÁCH KINH THÁNH ==="
        ))

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        start_time = time.time()
        total_verses_loaded = 0
        total_chapters_loaded = 0

        # Chuẩn bị danh sách các task cần tải
        tasks = []
        for book in books:
            chapters_to_fetch = min(max_ch, book.total_chapters)
            for ch_num in range(1, chapters_to_fetch + 1):
                existing_count = Verse.objects.filter(chapter__book=book, chapter__number=ch_num).count()
                if existing_count > 0 and not force:
                    continue
                
                url = self.get_chapter_url(book.slug, ch_num)
                tasks.append((book, ch_num, url))

        self.stdout.write(f"Tổng số chương cần tải từ mạng: {len(tasks)} chương (bỏ qua các chương đã có sẵn).")
        
        if not tasks:
            self.stdout.write(self.style.SUCCESS("Tất cả các chương mục tiêu đã có sẵn nội dung trong CSDL!"))
        else:
            def fetch_chapter(task):
                b, ch, u = task
                for attempt in range(2):
                    try:
                        resp = requests.get(u, headers=headers, timeout=15)
                        if resp.status_code == 200:
                            return (b, ch, u, resp.text, None)
                        elif resp.status_code == 404:
                            return (b, ch, u, None, "404 Not Found")
                    except Exception as err:
                        if attempt == 1:
                            return (b, ch, u, None, str(err))
                        time.sleep(0.5)
                return (b, ch, u, None, "Unknown error")

            self.stdout.write(f"Đang tải song song với {workers} luồng...")
            
            book_grouped_tasks = {}
            for t in tasks:
                b = t[0]
                book_grouped_tasks.setdefault(b.id, []).append(t)

            completed_books = 0
            for book in books:
                b_tasks = book_grouped_tasks.get(book.id, [])
                if not b_tasks:
                    completed_books += 1
                    continue

                with ThreadPoolExecutor(max_workers=min(workers, len(b_tasks))) as executor:
                    future_to_task = {executor.submit(fetch_chapter, t): t for t in b_tasks}
                    
                    book_verses = 0
                    book_chapters = 0
                    for future in as_completed(future_to_task):
                        b, ch_num, url, html, error = future.result()
                        if error or not html:
                            self.stderr.write(f"  [LỖI] {b.name} Ch.{ch_num}: {error} ({url})")
                            continue

                        # Parse HTML
                        parsed_verses = self.parse_verses_from_html(html)
                        if not parsed_verses:
                            self.stderr.write(f"  [CẢNH BÁO] Không bóc tách được câu nào từ {b.name} Ch.{ch_num}")
                            continue

                        with transaction.atomic():
                            chapter, _ = Chapter.objects.get_or_create(
                                book=b,
                                number=ch_num,
                                defaults={"title": f"Chương {ch_num}"}
                            )
                            if force:
                                Verse.objects.filter(chapter=chapter).delete()

                            verse_objects = []
                            for v_num, v_text, sec_title, sub_title in parsed_verses:
                                verse_objects.append(Verse(
                                    chapter=chapter,
                                    verse_number=v_num,
                                    section_title=sec_title,
                                    sub_title=sub_title,
                                    text=v_text,
                                    text_unaccent=remove_vietnamese_accents(v_text)
                                ))
                            Verse.objects.bulk_create(verse_objects, ignore_conflicts=True)

                        book_verses += len(parsed_verses)
                        book_chapters += 1

                total_verses_loaded += book_verses
                total_chapters_loaded += book_chapters
                completed_books += 1
                self.stdout.write(
                    f"[{completed_books:2d}/{len(books):2d}] {book.name} ({book.code}): nạp xong {book_chapters} chương ({book_verses} câu)."
                )

        elapsed = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(
            f"\n=== HOÀN TẤT NẠP NỘI DUNG ==="
            f"\n- Thời gian: {elapsed:.1f} giây"
            f"\n- Số chương mới nạp: {total_chapters_loaded}"
            f"\n- Số câu mới nạp: {total_verses_loaded}"
            f"\n- Tổng số câu hiện có trong CSDL: {Verse.objects.count()}"
        ))

        # Xuất fixture nếu có yêu cầu
        if export_fixture:
            self.stdout.write(f"Đang xuất fixture ra file: {export_fixture}...")
            chapters = Chapter.objects.filter(number__lte=max_ch, verses__isnull=False).distinct()
            verses = Verse.objects.filter(chapter__in=chapters)
            
            with open(export_fixture, 'w', encoding='utf-8') as f:
                data = serializers.serialize("json", list(chapters) + list(verses), indent=2, ensure_ascii=False)
                f.write(data)
            self.stdout.write(self.style.SUCCESS(f"Đã xuất thành công {chapters.count()} chương và {verses.count()} câu vào {export_fixture}."))

    def parse_verses_from_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        subs = soup.find_all('sub')
        if not subs:
            return []

        verses = []
        for sub in subs:
            v_id = sub.get('id')
            if not v_id or not v_id.isdigit():
                continue
            v_num = int(v_id)

            text_bits = []
            node = sub.next_sibling
            while node:
                if getattr(node, 'name', None) == 'sub':
                    break
                if isinstance(node, NavigableString):
                    text_bits.append(str(node))
                else:
                    inner_subs = node.find_all('sub')
                    if inner_subs:
                        for child in node.children:
                            if getattr(child, 'name', None) == 'sub':
                                break
                            text_bits.append(child.get_text() if hasattr(child, 'get_text') else str(child))
                        break
                    else:
                        text_bits.append(node.get_text())
                node = node.next_sibling

            raw_text = ' '.join(''.join(text_bits).split())
            clean_text = re.sub(r'[\u200b\ufeff]', '', raw_text).strip()

            if not clean_text:
                parent = sub.parent
                if parent:
                    p_text = parent.get_text()
                    clean_text = re.sub(r'^\d+\s*', '', p_text).strip()

            if clean_text:
                verses.append((v_num, clean_text, "", ""))

        return verses
