import re
import time
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from bible.models import Book, Chapter, Verse

class Command(BaseCommand):
    help = "Thu thập và nhập khẩu văn bản Kinh Thánh từ nguồn chuẩn Công Giáo"

    def add_arguments(self, parser):
        parser.add_argument('--book', type=str, help='Slug của sách cần cào (VD: sach-sang-the)')
        parser.add_argument('--start', type=int, default=1, help='Chương bắt đầu')
        parser.add_argument('--end', type=int, default=None, help='Chương kết thúc')
        parser.add_argument('--delay', type=float, default=0.5, help='Độ trễ giữa các request (giây)')

    def handle(self, *args, **options):
        book_slug = options.get('book')
        start_ch = options.get('start')
        end_ch = options.get('end')
        delay = options.get('delay')

        if not book_slug:
            self.stdout.write("Vui lòng chỉ định slug của sách, ví dụ: --book sach-sang-the --start 1 --end 5")
            return

        try:
            book = Book.objects.get(slug=book_slug)
        except Book.DoesNotExist:
            self.stderr.write(f"Không tìm thấy sách với slug: {book_slug}")
            return

        if end_ch is None:
            end_ch = book.total_chapters

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        self.stdout.write(f"Bắt đầu thu thập sách '{book.name}' từ chương {start_ch} đến {end_ch}...")

        total_imported = 0
        for ch_num in range(start_ch, end_ch + 1):
            if ch_num == 1:
                url = f"https://augustino.net/{book.slug}"
            else:
                url = f"https://augustino.net/{book.slug}-chuong-{ch_num}"

            self.stdout.write(f"-> Đang tải {book.name} chương {ch_num} ({url})...")
            try:
                resp = requests.get(url, headers=headers, timeout=20)
                if resp.status_code != 200:
                    self.stderr.write(f"   Lỗi HTTP {resp.status_code} khi tải {url}")
                    continue

                chapter, _ = Chapter.objects.get_or_create(
                    book=book,
                    number=ch_num,
                    defaults={"title": f"Chương {ch_num}"}
                )

                # Parse verses
                soup = BeautifulSoup(resp.text, 'html.parser')
                # Find all sub tags representing verse numbers
                sub_tags = soup.find_all('sub')
                if not sub_tags:
                    # Next.js hydration payload parsing
                    html_stream_match = re.search(r'self\.__next_f\.push\(\[1,"(.*?)<hr>\\r\\n<h2>Chương \d+</h2>', resp.text)
                    # Try searching for verses in script blocks
                    pass

                count_in_ch = 0
                for sub in sub_tags:
                    v_id = sub.get('id')
                    if not v_id or not v_id.isdigit():
                        continue
                    v_num = int(v_id)
                    parent = sub.parent
                    if not parent:
                        continue

                    # Extract text after this sub tag until next sub tag or end of paragraph
                    # Simple heuristic: clean text of parent node
                    verse_text = sub.next_sibling
                    if verse_text and isinstance(verse_text, str):
                        clean_t = verse_text.strip()
                    else:
                        clean_t = parent.text.replace(str(v_num), "", 1).strip()

                    clean_t = re.sub(r'[\u200b\ufeff]', '', clean_t) # remove zero-width spaces
                    if clean_t:
                        Verse.objects.update_or_create(
                            chapter=chapter,
                            verse_number=v_num,
                            defaults={"text": clean_t}
                        )
                        count_in_ch += 1

                self.stdout.write(self.style.SUCCESS(f"   Nhập thành công {count_in_ch} câu vào chương {ch_num}."))
                total_imported += count_in_ch
                time.sleep(delay)

            except Exception as e:
                self.stderr.write(f"   Ngoại lệ khi cào chương {ch_num}: {e}")

        self.stdout.write(self.style.SUCCESS(f"==> Hoàn tất thu thập: tổng cộng {total_imported} câu đã được lưu!"))
