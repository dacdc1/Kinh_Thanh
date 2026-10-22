from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from bible.models import Book, Chapter, Verse, ReadingPlan, ReadingPlanDay


class AccountViewsAndPagesTest(TestCase):
    """Kiểm thử hiển thị trang đăng nhập, đăng ký và các nút Social Login."""

    def setUp(self):
        self.client = Client()

    def test_login_page_renders_status_200(self):
        """Trang đăng nhập /accounts/login/ phản hồi HTTP 200 và dùng template account/login.html."""
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertContains(response, 'Đăng Nhập')
        self.assertContains(response, 'Tên tài khoản hoặc Email:')

    def test_login_page_contains_oauth_providers(self):
        """Trang đăng nhập chứa nút đăng nhập qua Google và Facebook."""
        response = self.client.get(reverse('account_login'))
        content = response.content.decode('utf-8')
        self.assertIn('Đăng nhập với Google', content)
        self.assertIn('Đăng nhập với Facebook', content)
        self.assertIn('/accounts/google/login/', content)
        self.assertIn('/accounts/facebook/login/', content)

    def test_signup_page_renders_status_200(self):
        """Trang đăng ký /accounts/signup/ phản hồi HTTP 200 và dùng template account/signup.html."""
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/signup.html')
        self.assertContains(response, 'Tạo Tài Khoản')
        self.assertContains(response, 'Đăng Ký Tài Khoản')

    def test_signup_page_contains_oauth_providers(self):
        """Trang đăng ký chứa tùy chọn đăng ký nhanh với Google và Facebook."""
        response = self.client.get(reverse('account_signup'))
        content = response.content.decode('utf-8')
        self.assertIn('Đăng ký nhanh với Google', content)
        self.assertIn('Đăng ký với Facebook', content)

    def test_social_provider_urls_reverse(self):
        """Kiểm tra URL phân giải chính xác cho các provider Google & Facebook."""
        self.assertEqual(reverse('google_login'), '/accounts/google/login/')
        self.assertEqual(reverse('facebook_login'), '/accounts/facebook/login/')


class AuthenticationFlowTest(TestCase):
    """Kiểm thử luồng đăng nhập, đăng ký, đăng xuất và xử lý lỗi."""

    def setUp(self):
        self.client = Client()
        self.username = 'phero_nguyen'
        self.email = 'phero.nguyen@example.com'
        self.password = 'GiaoDan@1234'
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

    def test_login_with_username_success(self):
        """Đăng nhập thành công bằng Username và điều hướng về trang chủ."""
        response = self.client.post(reverse('account_login'), {
            'login': self.username,
            'password': self.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        # Kiểm tra session đã được xác thực
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.id)

    def test_login_with_email_success(self):
        """Đăng nhập thành công bằng Email đã đăng ký."""
        response = self.client.post(reverse('account_login'), {
            'login': self.email,
            'password': self.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.id)

    def test_login_wrong_password_fails(self):
        """Đăng nhập với mật khẩu sai bị từ chối và hiển thị thông báo lỗi."""
        response = self.client.post(reverse('account_login'), {
            'login': self.username,
            'password': 'WrongPassword123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertContains(response, 'Tên đăng nhập hoặc mật khẩu không chính xác')

    def test_login_nonexistent_user_fails(self):
        """Đăng nhập với tài khoản không tồn tại bị từ chối."""
        response = self.client.post(reverse('account_login'), {
            'login': 'nguoidung_khongtontai',
            'password': 'AnyPassword123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_empty_credentials(self):
        """Gửi form đăng nhập trống không làm sập hệ thống."""
        response = self.client.post(reverse('account_login'), {
            'login': '',
            'password': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_flow(self):
        """Đăng xuất xóa session người dùng và điều hướng về trang chủ."""
        self.client.force_login(self.user)
        self.assertIn('_auth_user_id', self.client.session)

        response = self.client.get(reverse('account_logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_signup_new_user_success(self):
        """Đăng ký tài khoản mới thành công tạo User trong CSDL và tự động đăng nhập."""
        new_username = 'paulo_tran'
        new_email = 'paulo.tran@example.com'
        new_password = 'TuyenXungDucTin#99'

        response = self.client.post(reverse('account_signup'), {
            'username': new_username,
            'email': new_email,
            'password1': new_password,
            'password2': new_password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

        created_user = User.objects.filter(username=new_username).first()
        self.assertIsNotNone(created_user)
        self.assertEqual(created_user.email, new_email)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), created_user.id)

    def test_signup_password_mismatch(self):
        """Đăng ký với mật khẩu xác nhận không khớp sẽ báo lỗi và không tạo user."""
        response = self.client.post(reverse('account_signup'), {
            'username': 'mismatch_user',
            'email': 'mismatch@example.com',
            'password1': 'MatKhau12345!',
            'password2': 'MatKhauKhacNhau!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='mismatch_user').exists())


class ProtectedViewsAccessControlTest(TestCase):
    """Kiểm thử phân quyền các trang yêu cầu đăng nhập (@login_required)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='gioan_baotixita',
            email='gioan@example.com',
            password='TestPassword123'
        )
        self.book = Book.objects.create(
            name='Phúc Âm Gioan',
            code='Ga',
            slug='phuc-am-gioan',
            testament='NT',
            group='Tin Mừng',
            order_num=43,
            total_chapters=21
        )
        self.chapter = Chapter.objects.create(book=self.book, number=1)
        self.verse = Verse.objects.create(chapter=self.chapter, verse_number=1, text='Lúc khởi đầu đã có Ngôi Lời')
        self.plan = ReadingPlan.objects.create(name='Kế hoạch 1 năm', slug='ke-hoach-1-nam', total_days=365)
        self.plan_day = ReadingPlanDay.objects.create(plan=self.plan, day_number=1, title='Ngày 1', readings_label='Ga 1')

    def test_profile_view_requires_login(self):
        """Khách vãng lai truy cập /user/profile/ bị chuyển hướng sang trang đăng nhập."""
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('account_login'), response.url)

    def test_profile_view_authenticated(self):
        """Người dùng đã đăng nhập truy cập /user/profile/ nhận mã 200 và thống kê."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertContains(response, 'gioan_baotixita')
        self.assertContains(response, 'Thống Kê Đọc Lời Chúa')
        self.assertContains(response, 'Chương đã đọc')

    def test_my_library_view_requires_login(self):
        """Khách vãng lai truy cập /tu-sach-ca-nhan/ bị chuyển hướng sang đăng nhập."""
        response = self.client.get(reverse('bible:my_library'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('account_login'), response.url)

    def test_my_library_view_authenticated(self):
        """Người dùng đăng nhập truy cập /tu-sach-ca-nhan/ thành công."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('bible:my_library'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bible/my_library.html')

    def test_bookmark_api_requires_login(self):
        """Chưa đăng nhập gọi API bookmark bị chuyển hướng sang đăng nhập."""
        response = self.client.post(reverse('bible:api_toggle_bookmark', args=[self.verse.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('account_login'), response.url)

    def test_highlight_api_requires_login(self):
        """Chưa đăng nhập gọi API highlight bị chuyển hướng sang đăng nhập."""
        response = self.client.post(
            reverse('bible:api_save_highlight', args=[self.verse.id]),
            {'color': 'yellow'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('account_login'), response.url)

    def test_note_api_requires_login(self):
        """Chưa đăng nhập gọi API ghi chú bị chuyển hướng sang đăng nhập."""
        response = self.client.post(
            reverse('bible:api_save_note', args=[self.verse.id]),
            {'content': 'Suy niệm câu này'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('account_login'), response.url)

    def test_toggle_plan_day_requires_login(self):
        """Chưa đăng nhập gọi API toggle kế hoạch đọc bị chuyển hướng sang đăng nhập."""
        response = self.client.post(reverse('bible:toggle_plan_day', args=[self.plan_day.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('account_login'), response.url)


class AdminDashboardAccessControlTest(TestCase):
    """Kiểm thử bảo mật và hiển thị Bảng điều khiển Quản trị (Admin Dashboard)."""

    def setUp(self):
        self.client = Client()
        self.regular_user = User.objects.create_user(
            username='docgia_thuong',
            password='Password123'
        )
        self.staff_user = User.objects.create_user(
            username='admin_hethong',
            password='AdminPassword123',
            is_staff=True,
            is_superuser=True
        )

    def test_dashboard_requires_login(self):
        """Khách vãng lai chưa đăng nhập truy cập /admin-dashboard/ bị chuyển hướng sang đăng nhập."""
        response = self.client.get(reverse('admin_dashboard_root'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('account_login'), response.url)

    def test_dashboard_forbidden_for_regular_user(self):
        """Người dùng thường (không có quyền is_staff) truy cập /admin-dashboard/ bị chuyển hướng."""
        self.client.force_login(self.regular_user)
        response = self.client.get(reverse('admin_dashboard_root'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_accessible_for_staff_user(self):
        """Quản trị viên (is_staff=True) truy cập thành công HTTP 200 và thấy các chỉ số KPI."""
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('admin_dashboard_root'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/admin_dashboard.html')
        self.assertContains(response, 'Bảng Điều Khiển Quản Trị')
        self.assertContains(response, 'Độc Giả & Thành Viên')
        self.assertContains(response, 'Kho Dữ Liệu Kinh Thánh')
        self.assertContains(response, 'Quản Lý Người Dùng & Tiến Độ Đọc')

    def test_dashboard_url_resolution(self):
        """Kiểm tra URL name phân giải đúng."""
        self.assertEqual(reverse('accounts:admin_dashboard'), '/user/dashboard/')
        self.assertEqual(reverse('admin_dashboard_root'), '/admin-dashboard/')


class GuestReaderLimitAndLoginPromptTest(TestCase):
    """Kiểm thử giới hạn 3 chương đối với khách vãng lai và yêu cầu đăng nhập."""

    def setUp(self):
        self.client = Client()
        self.book = Book.objects.create(
            name='Sáng Thế',
            code='St',
            slug='sach-sang-the',
            testament='OT',
            group='Ngũ Thư',
            order_num=1,
            total_chapters=50
        )
        # Tạo 4 chương, mỗi chương 5 câu
        for ch_num in range(1, 5):
            ch = Chapter.objects.create(book=self.book, number=ch_num)
            for v_num in range(1, 6):
                Verse.objects.create(chapter=ch, verse_number=v_num, text=f'Câu {v_num} chương {ch_num}')

    def test_guest_can_read_up_to_3_chapters(self):
        """Khách vãng lai đọc 3 chương đầu tiên không bị giới hạn."""
        for num in range(1, 4):
            response = self.client.get(reverse('bible:reader', args=[self.book.slug, num]))
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.context['limit_reached'])
            # Đọc đầy đủ 5 câu
            self.assertEqual(len(response.context['verses']), 5)

    def test_guest_reading_4th_chapter_triggers_login_prompt(self):
        """Khách vãng lai đọc đến chương thứ 4 bị kích hoạt limit_reached và hiện modal đăng nhập."""
        # Đọc 3 chương đầu
        for num in range(1, 4):
            self.client.get(reverse('bible:reader', args=[self.book.slug, num]))

        # Đọc chương 4
        response = self.client.get(reverse('bible:reader', args=[self.book.slug, 4]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['limit_reached'])
        # Chỉ hiển thị 3 câu trích đoạn xem trước
        self.assertEqual(len(response.context['verses']), 3)

        # Kiểm tra nội dung modal và banner yêu cầu đăng nhập
        content = response.content.decode('utf-8')
        self.assertIn('guest-limit-modal', content)
        self.assertIn('active', content)
        self.assertIn('Bạn đã hoàn thành 3 chương đọc thử miễn phí', content)
        self.assertIn('tiếp tục đọc không giới hạn', content)
        self.assertIn('Tiếp tục với Google', content)
        self.assertIn('Tiếp tục với Facebook', content)
        self.assertIn('Đăng nhập Email', content)

    def test_authenticated_user_has_no_reading_limits(self):
        """Người dùng đã đăng nhập đọc từ chương 4 trở đi không bị giới hạn và lưu tiến độ."""
        user = User.objects.create_user(username='thanh_vien_doc', password='Password123')
        self.client.force_login(user)

        # Đọc 4 chương liên tiếp
        for num in range(1, 5):
            response = self.client.get(reverse('bible:reader', args=[self.book.slug, num]))
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.context['limit_reached'])
            self.assertEqual(len(response.context['verses']), 5)
