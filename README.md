# Hệ Thống Website Đọc Kinh Thánh Công Giáo (Trọn Bộ 73 Cuốn)

Dự án website đọc Kinh Thánh Công Giáo trực tuyến được xây dựng bằng **Python (Django)** và **PostgreSQL**, tối ưu hóa trải nghiệm đọc sách thanh tịnh (Distraction-free Reader), hỗ trợ tra cứu toàn văn không dấu siêu tốc, kế hoạch đọc 365 ngày, hệ thống tương tác câu Kinh Thánh (Bookmark, Highlight, Ghi chú cá nhân) và đăng nhập mạng xã hội (Google / Facebook).

---

## 🌟 Tính Năng Nổi Bật

1. **Chuẩn Quy Điển 73 Cuốn Công Giáo:**
   - **46 Cuốn Cựu Ước:** Bộ Ngũ Thư (5), Các Sách Lịch Sử (16), Giáo Huấn & Khôn Ngoan (7), Các Sách Ngôn Sứ (18).
   - **27 Cuốn Tân Ước:** Bốn Sách Tin Mừng (4), Lịch Sử Giáo Hội - Công Vụ (1), Các Thư Thánh Phaolô (14), Các Thư Chung Tông Đồ (7), Sách Khải Huyền (1).
   - Đầy đủ tên viết tắt chuẩn phụng vụ (*St, Xh, Lv, Tv, Mt, Mc, Lc, Ga...*).

2. **Giao Diện Đọc Sách Chuyên Sâu (Reader Mode):**
   - 3 Chế độ nền: **Sáng (Light)**, **Giấy Ngà (Sepia ấm áp)**, **Tối (Dark mode đọc đêm)**.
   - Tùy chỉnh kích thước chữ (A- / A+) và phông chữ (Serif có chân trang trọng / Sans-serif hiện đại).
   - Tích hợp trình phát âm thanh (Audio) cho từng chương.
   - Thanh điều hướng chuyển chương, chuyển sách liền mạch.

3. **Tìm Kiếm Toàn Văn Không Dấu (Unaccented Search Engine):**
   - Tìm kiếm cực nhanh ngay cả khi gõ không dấu tiếng Việt (ví dụ: `thien chua sang tao`, `duc men`, `tam moi phuc`...).
   - Tra cứu chính xác câu Kinh Thánh theo định dạng chuẩn: `Ga 3,16`, `St 1,1`, `Mt 5,3`...

4. **Tương Tác Lời Chúa Trực Tiếp:**
   - Chọn câu để **Bôi màu (Highlight)** với 5 màu sắc (Vàng, Xanh lá, Xanh lam, Hồng, Tím).
   - **Đánh dấu (Bookmark)** những câu tâm đắc.
   - Thêm **Ghi chú cá nhân / Cảm nghiệm suy niệm** gắn liền với câu.
   - **Chia sẻ câu Kinh Thánh:** Trích dẫn chuẩn Công Giáo kèm nguồn hoặc sao chép nhanh vào clipboard.

5. **Kế Hoạch Đọc Kinh Thánh 1 Năm (365 Ngày):**
   - Lộ trình mỗi ngày gồm 1 đoạn Cựu Ước, 1 bài Thánh Vịnh và 1 trích đoạn Tân Ước.
   - Thanh tiến độ hiển thị phần trăm (%) hoàn thành trực quan.
   - Đánh dấu hoàn thành từng ngày với checkbox tự động lưu vào hệ thống.

6. **Phân Quyền & Giới Hạn Đọc Khách Vãng Lai:**
   - **Khách vãng lai:** Được đọc thử miễn phí tối đa 3 chương. Khi đọc sang chương thứ 4 hoặc khi bấm Bookmark/Highlight/Ghi chú, hệ thống sẽ hiển thị hộp thoại đăng nhập.
   - **Người dùng đăng nhập:** Mở khóa toàn quyền đọc không giới hạn, đồng bộ toàn bộ Bookmark, Ghi chú, Lịch sử đọc và Kế hoạch 365 ngày trên mọi thiết bị. Hỗ trợ đăng nhập nhanh bằng **Google** hoặc **Facebook**.

---

## 🚀 Hướng Dẫn Chạy & Phát Triển Cục Bộ (Local)

### 1. Chuẩn bị môi trường
```bash
# Kích hoạt virtualenv
source .venv/bin/activate

# Cài đặt các gói phụ thuộc (nếu chưa cài)
pip install -r requirements.txt
```

### 2. Cấu hình biến môi trường
Mặc định hệ thống đã có file `.env` sẵn sàng chạy cục bộ với SQLite. Nếu muốn kết nối PostgreSQL cục bộ hoặc từ xa, chỉ cần chỉnh sửa dòng:
```ini
DATABASE_URL=postgres://tên_user:mật_khẩu@localhost:5432/tên_database
```

### 3. Khởi tạo Cơ sở dữ liệu & Nạp dữ liệu mẫu
```bash
# Áp dụng migrations
python manage.py migrate

# Khởi tạo 73 cuốn sách và kế hoạch 365 ngày
python manage.py init_canon

# Nạp sẵn các chương mẫu có văn bản đầy đủ (Sáng Thế, Thánh Vịnh, Mát-thêu, Gio-an, 1 Cô-rin-tô)
python manage.py import_sample
```

### 4. Thu thập thêm văn bản 73 cuốn từ nguồn online
Bạn có thể dùng lệnh crawler để cào thêm văn bản của bất kỳ cuốn nào:
```bash
# Cào sách Sáng Thế từ chương 1 đến chương 50
python manage.py import_bible --book sach-sang-the --start 1 --end 50

# Cào sách Tin Mừng Mát-thêu
python manage.py import_bible --book tin-mung-theo-thanh-mat-theu --start 1 --end 28
```

### 5. Khởi động Web Server
```bash
python manage.py runserver
```
Truy cập vào trình duyệt: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🔑 Tài Khoản Kiểm Thử Cục Bộ (Test Accounts)

Hệ thống đã tạo sẵn 2 tài khoản mẫu phục vụ thử nghiệm và kiểm thử trên môi trường Local:

| Loại tài khoản | Tên đăng nhập (Username) | Mật khẩu (Password) | Email | Quyền hạn & Chức năng |
| :--- | :--- | :--- | :--- | :--- |
| **Quản trị viên (Admin)** | `admin` | `admin123` | `admin@kinhthanh.vn` | Toàn quyền Quản trị: Truy cập **Admin Dashboard** ([`/admin-dashboard/`](http://127.0.0.1:8000/admin-dashboard/)), **Django Admin** ([`/admin/`](http://127.0.0.1:8000/admin/)), quản lý người dùng và dữ liệu. |
| **Độc giả (Member / User)** | `docgia` | `docgia123` | `docgia@kinhthanh.vn` | Mở khóa đọc không giới hạn 73 cuốn Kinh Thánh (vượt qua giới hạn 3 chương của khách vãng lai), lưu Bookmark, bôi màu Highlight, ghi chú suy niệm và Kế hoạch 365 ngày tại **Tủ sách cá nhân** ([`/tu-sach-ca-nhan/`](http://127.0.0.1:8000/tu-sach-ca-nhan/)). |

> [!TIP]
> **Lệnh khởi tạo nhanh tài khoản mẫu:**
> ```bash
> # Khởi tạo hoặc đặt lại 2 tài khoản mẫu admin và docgia:
> python manage.py create_test_user
>
> # Hoặc tự tạo thêm tài khoản tùy chỉnh:
> python manage.py create_test_user --username phero --password matkhau123 --email phero@example.com
> ```

---

## 🐳 Đóng Gói & Deploy Với Thư Mục `docker/` (PostgreSQL 16)

Toàn bộ cấu hình đóng gói độc lập đã được tổ chức gọn gàng trong thư mục [`docker/`](file:///Users/caodac/Documents/Kinh_Thanh_v1/docker/):

```bash
# Cách 1: Khởi động 1 click bằng script tự động
cd docker
./start.sh

# Cách 2: Khởi động bằng Docker Compose tiêu chuẩn
cd docker
docker compose up --build -d
```

Hoặc chạy trực tiếp từ thư mục gốc của dự án:
```bash
docker compose up --build -d
```

Sau khi chạy xong:
- Website hoạt động tại: `http://localhost:8000`
- Bảng điều khiển Quản trị: `http://localhost:8000/admin-dashboard/`
- Cơ sở dữ liệu PostgreSQL lưu trữ bền vững tại Docker volume `kinhthanh_postgres_data`.
- Toàn bộ migrations, 73 cuốn sách, văn bản mẫu và tài khoản test (`admin`/`docgia`) sẽ được tự động khởi tạo hoàn chỉnh khi container khởi động.
- Để dừng hệ thống: `cd docker && ./stop.sh` (hoặc `docker compose down`).
- Xem chi tiết tại tài liệu chuyên sâu: [`docker/README.md`](file:///Users/caodac/Documents/Kinh_Thanh_v1/docker/README.md).

---

## 🧪 Chạy Kiểm Thử Tự Động (Tests)

Hệ thống đi kèm bộ kiểm thử tự động toàn diện:
```bash
# Chạy toàn bộ test suite Django (37 bài test tự động)
python manage.py test
```
Toàn bộ **37/37 bài test** đều đạt (OK 100%) kiểm tra đầy đủ:
- **Bible App**: Trang chủ, Reader mode 3 theme, Tìm kiếm toàn văn không dấu tiếng Việt, Giới hạn 3 chương của khách vãng lai, Bookmark, Highlight, Ghi chú cá nhân, Kế hoạch đọc 365 ngày.
- **Accounts App**: Đăng nhập bằng Username/Email, Đăng ký, Đăng xuất, Bắt lỗi sai thông tin, Phân quyền bảo vệ (@login_required), Social login URLs và **Bảng điều khiển Admin Dashboard** (@staff_member_required).

