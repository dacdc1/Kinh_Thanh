from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Tạo tài khoản kiểm thử cục bộ (mặc định tạo admin/admin123 và docgia/docgia123)'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Tên tài khoản tùy chỉnh')
        parser.add_argument('--password', type=str, help='Mật khẩu tùy chỉnh')
        parser.add_argument('--email', type=str, help='Email tùy chỉnh')
        parser.add_argument('--admin', action='store_true', help='Cấp quyền superuser/admin')

    def handle(self, *args, **options):
        username = options.get('username')
        password = options.get('password')
        email = options.get('email')
        is_admin = options.get('admin')

        if username and password:
            user, created = User.objects.get_or_create(username=username)
            user.email = email or f"{username}@example.com"
            user.set_password(password)
            if is_admin:
                user.is_staff = True
                user.is_superuser = True
            user.save()
            action = "Đã tạo mới" if created else "Đã cập nhật"
            self.stdout.write(self.style.SUCCESS(f"{action} tài khoản '{username}' thành công!"))
            return

        # Mặc định: Tạo 2 tài khoản mẫu
        # 1. Admin
        admin_user, created_admin = User.objects.get_or_create(username='admin')
        admin_user.email = 'admin@kinhthanh.vn'
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        # 2. Độc giả bình thường
        docgia_user, created_docgia = User.objects.get_or_create(username='docgia')
        docgia_user.email = 'docgia@kinhthanh.vn'
        docgia_user.set_password('docgia123')
        docgia_user.save()

        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS(" ĐÃ KHỞI TẠO TÀI KHOẢN MẪU ĐỂ ĐĂNG NHẬP TRÊN LOCAL:"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(f" 1. Tài khoản Quản Trị (Admin):")
        self.stdout.write(f"    - Username: admin")
        self.stdout.write(f"    - Mật khẩu: admin123")
        self.stdout.write(f"    - Email:    admin@kinhthanh.vn")
        self.stdout.write(f" 2. Tài khoản Độc Giả (Member):")
        self.stdout.write(f"    - Username: docgia")
        self.stdout.write(f"    - Mật khẩu: docgia123")
        self.stdout.write(f"    - Email:    docgia@kinhthanh.vn")
        self.stdout.write(self.style.SUCCESS("=" * 60))
