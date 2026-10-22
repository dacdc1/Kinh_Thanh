from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from bible.models import Book, Chapter, Verse, Bookmark, Highlight, PersonalNote, ReadingPlan, ReadingPlanDay, UserPlanProgress

class CatholicBibleAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        
        # Create sample book (Sách Sáng Thế)
        self.book = Book.objects.create(
            order_num=1,
            code="St",
            name="Sáng Thế",
            slug="sach-sang-the",
            testament="OT",
            group="Ngũ Thư",
            total_chapters=50,
            description="Sách Khởi Nguyên"
        )
        
        # Create chapters
        self.ch1 = Chapter.objects.create(book=self.book, number=1, title="Chương 1")
        self.ch2 = Chapter.objects.create(book=self.book, number=2, title="Chương 2")
        self.ch3 = Chapter.objects.create(book=self.book, number=3, title="Chương 3")
        self.ch4 = Chapter.objects.create(book=self.book, number=4, title="Chương 4")
        
        # Create verses
        self.v1 = Verse.objects.create(chapter=self.ch1, verse_number=1, text="Lúc khởi đầu, Thiên Chúa sáng tạo trời đất.")
        self.v2 = Verse.objects.create(chapter=self.ch1, verse_number=3, text="Thiên Chúa phán: “Phải có ánh sáng.” Liền có ánh sáng.")
        
        # Reading plan
        self.plan = ReadingPlan.objects.create(name="Kế hoạch 365 ngày", slug="ke-hoach-1-nam", total_days=365)
        self.day1 = ReadingPlanDay.objects.create(plan=self.plan, day_number=1, title="Ngày 1", readings_label="St 1-2")

    def test_home_page_loads(self):
        response = self.client.get(reverse('bible:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kinh Thánh Công Giáo")
        self.assertContains(response, "Sáng Thế")

    def test_reader_page_loads(self):
        response = self.client.get(reverse('bible:reader', args=[self.book.slug, 1]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lúc khởi đầu, Thiên Chúa sáng tạo trời đất.")

    def test_unaccented_search(self):
        # Search query without accents: "thien chua sang tao"
        response = self.client.get(reverse('bible:search') + '?q=thien+chua+sang+tao')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lúc khởi đầu, Thiên Chúa sáng tạo trời đất.")
        
        # Search direct reference: "St 1, 1"
        response2 = self.client.get(reverse('bible:search') + '?q=St+1%2C1')
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, "Khớp chính xác câu tra cứu")

    def test_guest_reading_limit(self):
        # Read ch1
        self.client.get(reverse('bible:reader', args=[self.book.slug, 1]))
        # Read ch2
        self.client.get(reverse('bible:reader', args=[self.book.slug, 2]))
        # Read ch3
        self.client.get(reverse('bible:reader', args=[self.book.slug, 3]))
        
        # Read ch4 (Limit reached!)
        res4 = self.client.get(reverse('bible:reader', args=[self.book.slug, 4]))
        self.assertTrue(res4.context['limit_reached'])
        self.assertContains(res4, "Bạn đã hoàn thành 3 chương đọc thử miễn phí!")

    def test_authenticated_user_unlimited(self):
        self.client.login(username='testuser', password='password123')
        # Authenticated user reading ch4 should NOT be limited
        res = self.client.get(reverse('bible:reader', args=[self.book.slug, 4]))
        self.assertFalse(res.context['limit_reached'])

    def test_bookmark_api(self):
        self.client.login(username='testuser', password='password123')
        res = self.client.post(reverse('bible:api_toggle_bookmark', args=[self.v1.id]))
        self.assertEqual(res.status_code, 200)
        self.assertTrue(Bookmark.objects.filter(user=self.user, verse=self.v1).exists())

    def test_highlight_api(self):
        self.client.login(username='testuser', password='password123')
        res = self.client.post(reverse('bible:api_save_highlight', args=[self.v1.id]), {'color': 'yellow'})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(Highlight.objects.filter(user=self.user, verse=self.v1, color='yellow').exists())

    def test_note_api(self):
        self.client.login(username='testuser', password='password123')
        res = self.client.post(reverse('bible:api_save_note', args=[self.v1.id]), {'content': 'Cảm nghiệm sâu sắc về tạo dựng.'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(PersonalNote.objects.get(user=self.user, verse=self.v1).content, 'Cảm nghiệm sâu sắc về tạo dựng.')

    def test_reading_plan_toggle(self):
        self.client.login(username='testuser', password='password123')
        res = self.client.post(reverse('bible:toggle_plan_day', args=[self.day1.id]))
        self.assertEqual(res.status_code, 200)
        self.assertTrue(UserPlanProgress.objects.filter(user=self.user, plan_day=self.day1, completed=True).exists())
