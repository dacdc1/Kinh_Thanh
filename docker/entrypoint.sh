#!/bin/sh
# ==============================================================================
# Docker Container Entrypoint cho Kinh Thánh Công Giáo (73 Cuốn)
# ==============================================================================
set -e

echo "=================================================================="
echo "🕊️  KHỞI TẠO CONTAINER KINH THÁNH CÔNG GIÁO"
echo "=================================================================="

# 1. Chờ CSDL PostgreSQL sẵn sàng kết nối
if [ -n "$DATABASE_URL" ]; then
    echo "⏳ Đang kiểm tra kết nối Cơ sở dữ liệu PostgreSQL..."
    python << 'END'
import sys
import time
import urllib.parse
import psycopg2
import os

db_url = os.environ.get('DATABASE_URL', '')
if db_url.startswith(('postgres://', 'postgresql://')):
    url = urllib.parse.urlparse(db_url)
    max_tries = 30
    for i in range(max_tries):
        try:
            conn = psycopg2.connect(
                dbname=url.path[1:],
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port or 5432,
                connect_timeout=3
            )
            conn.close()
            print("✅ Kết nối PostgreSQL thành công!")
            sys.exit(0)
        except Exception as e:
            print(f"⏳ Chờ PostgreSQL sẵn sàng ({i+1}/{max_tries})...")
            time.sleep(1)
    print("❌ Lỗi: Không thể kết nối tới PostgreSQL sau 30 giây.")
    sys.exit(1)
END
fi

# 2. Thực thi migrations
echo "📦 1. Thực thi database migrations..."
python manage.py migrate --noinput

# 3. Khởi tạo 73 cuốn Kinh Thánh và kế hoạch 365 ngày
echo "📖 2. Khởi tạo quy điển 73 cuốn Kinh Thánh & Kế hoạch 365 ngày..."
python manage.py init_canon

# 4. Nạp dữ liệu văn bản mẫu
echo "✍️ 3. Nạp các chương sách mẫu có văn bản đầy đủ..."
python manage.py import_sample

# 5. Khởi tạo tài khoản test (admin & docgia)
echo "👤 4. Khởi tạo tài khoản kiểm thử mặc định (admin/admin123 & docgia/docgia123)..."
python manage.py create_test_user

# 6. Gom static files cho Whitenoise / Nginx
echo "🎨 5. Thu thập Static files (collectstatic)..."
python manage.py collectstatic --noinput

echo "=================================================================="
echo "🚀 6. KHỞI CHẠY GUNICORN SERVER..."
echo "=================================================================="

# Thực thi lệnh truyền vào CMD (gunicorn)
exec "$@"
