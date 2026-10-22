# ==============================================================================
# Dockerfile Production cho Kinh Thánh Công Giáo (73 Cuốn)
# ==============================================================================
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Cài đặt thư viện hệ thống cần thiết cho PostgreSQL và Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt các gói Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn dự án vào container
COPY . /app/

# Sao chép entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Tạo thư mục media và staticfiles
RUN mkdir -p /app/media /app/staticfiles

EXPOSE 8000

# Sử dụng entrypoint script tự động kiểm tra CSDL, nạp 73 cuốn và test accounts
ENTRYPOINT ["/entrypoint.sh"]

# Lệnh mặc định khởi chạy Gunicorn WSGI Server
CMD ["gunicorn", "kinhthanh_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
