# 🐳 Hướng Dẫn Triển Khai Kinh Thánh Công Giáo Bằng Docker

Thư mục này chứa toàn bộ cấu hình đóng gói độc lập để khởi chạy hệ thống **Kinh Thánh Công Giáo (Trọn Bộ 73 Cuốn)** trên bất kỳ máy chủ nào (Local, VPS Ubuntu/Debian, Cloud) có cài đặt Docker.

---

## 📁 Cấu Trúc Thư Mục `docker/`

```
docker/
├── Dockerfile                   # Docker image production Python 3.9
├── entrypoint.sh                # Script tự động chờ DB, migrate, nạp 73 cuốn & tài khoản test
├── docker-compose.yml           # Stack chuẩn: PostgreSQL 16 + Web Django Gunicorn (Port 8000)
├── docker-compose.nginx.yml     # Stack mở rộng: Có thêm Nginx Reverse Proxy (Port 80)
├── .env.docker                  # File cấu hình biến môi trường
├── .env.docker.example          # File mẫu biến môi trường
├── start.sh                     # Script 1-click khởi chạy toàn bộ hệ thống
├── stop.sh                      # Script 1-click dừng hệ thống an toàn
├── nginx/
│   └── default.conf             # Cấu hình Nginx reverse proxy, gzip và static cache
└── README.md                    # Tài liệu hướng dẫn này
```

---

## 🚀 1. Khởi Chạy Nhanh (1 Click)

Chỉ cần vào thư mục `docker/` và chạy script:

```bash
cd docker
./start.sh
```

Hoặc sử dụng lệnh Docker Compose tiêu chuẩn:
```bash
cd docker
docker compose up --build -d
```

*(Hoặc từ thư mục gốc của dự án: `docker compose -f docker/docker-compose.yml up --build -d`)*

### Quá trình tự động diễn ra:
1. Khởi động container CSDL **PostgreSQL 16**.
2. Chờ PostgreSQL sẵn sàng nhận kết nối.
3. Tự động áp dụng các database migrations.
4. Tự động khởi tạo trọn bộ **73 cuốn Kinh Thánh Công Giáo** và lịch trình 365 ngày.
5. Tự động nạp các chương mẫu có văn bản đầy đủ (*Sáng Thế, Thánh Vịnh, Tin Mừng Mát-thêu, Gio-an, 1 Cô-rin-tô*).
6. Tự động khởi tạo sẵn 2 tài khoản kiểm thử:
   * **Quản trị (Admin)**: `admin` / `admin123`
   * **Độc giả (Member)**: `docgia` / `docgia123`
7. Thu thập static files qua **Whitenoise**.
8. Khởi chạy **Gunicorn WSGI Server** (3 workers).

---

## 🌐 2. Địa Chỉ Truy Cập Sau Khi Chạy

| Dịch vụ | URL |
| :--- | :--- |
| **Trang chủ đọc Kinh Thánh** | [http://localhost:8000](http://localhost:8000) |
| **Bảng điều khiển Quản trị (Admin Dashboard)** | [http://localhost:8000/admin-dashboard/](http://localhost:8000/admin-dashboard/) |
| **Trang Đăng Nhập** | [http://localhost:8000/accounts/login/](http://localhost:8000/accounts/login/) |
| **Django Admin** | [http://localhost:8000/admin/](http://localhost:8000/admin/) |

---

## 🛡️ 3. Khởi Chạy Với Nginx (Cổng 80)

Nếu muốn đưa hệ thống chạy trực tiếp trên cổng Web tiêu chuẩn `80` kèm bộ đệm Nginx:

```bash
cd docker
docker compose -f docker-compose.nginx.yml up --build -d
```
Truy cập tại: [http://localhost](http://localhost)

---

## 📋 4. Các Lệnh Vận Hành Thường Dùng

### Xem nhật ký hoạt động (Logs)
```bash
# Xem log toàn bộ hệ thống theo thời gian thực
docker compose logs -f

# Chỉ xem log web Django
docker compose logs -f web

# Chỉ xem log CSDL PostgreSQL
docker compose logs -f db
```

### Chạy crawler cào thêm dữ liệu văn bản vào container
```bash
# Cào thêm sách Sáng Thế từ chương 1 đến 50
docker compose exec web python manage.py import_bible --book sach-sang-the --start 1 --end 50

# Cào sách Tin Mừng Mát-thêu
docker compose exec web python manage.py import_bible --book tin-mung-theo-thanh-mat-theu --start 1 --end 28
```

### Tạo thêm tài khoản Superadmin
```bash
docker compose exec web python manage.py createsuperuser
```

### Sao lưu Cơ sở dữ liệu (Backup)
```bash
docker compose exec db pg_dump -U kinhthanh_user kinhthanh_db > backup_kinhthanh_$(date +%Y%m%d).sql
```

### Khôi phục Cơ sở dữ liệu (Restore)
```bash
cat backup_kinhthanh_20261018.sql | docker compose exec -T db psql -U kinhthanh_user -d kinhthanh_db
```

### Dừng hệ thống
```bash
./stop.sh
# hoặc:
docker compose down
```
*(Dữ liệu PostgreSQL, Bookmark, Ghi chú của độc giả được bảo toàn an toàn trong Docker Volume `kinhthanh_postgres_data`)*
