#!/usr/bin/env bash
# ==============================================================================
# Script Khởi Động Nhanh Hệ Thống Kinh Thánh bằng Docker Compose
# ==============================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "=================================================================="
echo "🐳  ĐANG KHỞI ĐỘNG KINH THÁNH CÔNG GIÁO QUA DOCKER COMPOSE"
echo "=================================================================="

# Kiểm tra file cấu hình môi trường
if [ ! -f ".env.docker" ]; then
    echo "📄 Chưa có file .env.docker, đang sao chép từ .env.docker.example..."
    cp .env.docker.example .env.docker
fi

# Build và khởi chạy các containers nền
docker compose up --build -d

echo ""
echo "=================================================================="
echo "✅ HỆ THỐNG ĐÃ KHỞI CHẠY THÀNH CÔNG!"
echo "=================================================================="
echo "🌐 Trang chủ đọc Kinh Thánh:    http://localhost:8000"
echo "📊 Bảng điều khiển Quản trị:   http://localhost:8000/admin-dashboard/"
echo "⚙️  Django Admin:               http://localhost:8000/admin/"
echo ""
echo "🔑 TÀI KHOẢN KIỂM THỬ SẴN SÀNG:"
echo "   - Quản trị (Admin):  admin / admin123"
echo "   - Độc giả (Member):  docgia / docgia123"
echo ""
echo "📋 Lệnh hữu ích:"
echo "   - Xem nhật ký hoạt động:  docker compose logs -f"
echo "   - Dừng hệ thống:           ./stop.sh  (hoặc docker compose down)"
echo "=================================================================="
