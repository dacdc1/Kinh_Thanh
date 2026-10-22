from django.db import models
from django.contrib.auth.models import User
import unicodedata

def remove_vietnamese_accents(text: str) -> str:
    """Normalize Vietnamese text by removing tone marks and converting đ/Đ to d/D."""
    if not text:
        return ""
    text = text.replace("đ", "d").replace("Đ", "D")
    nfkd_form = unicodedata.normalize('NFKD', text)
    clean_text = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return clean_text.lower()

class Book(models.Model):
    TESTAMENT_CHOICES = [
        ('OT', 'Cựu Ước (Old Testament)'),
        ('NT', 'Tân Ước (New Testament)'),
    ]
    
    GROUP_CHOICES = [
        ('Ngũ Thư', 'Ngũ Thư'),
        ('Lịch Sử', 'Các Sách Lịch Sử'),
        ('Giáo Huấn', 'Các Sách Giáo Huấn & Khôn Ngoan'),
        ('Ngôn Sứ', 'Các Sách Ngôn Sứ'),
        ('Tin Mừng', 'Sách Tin Mừng'),
        ('Công Vụ', 'Lịch Sử Giáo Hội (Công Vụ)'),
        ('Thư Phaolô', 'Các Thư của Thánh Phaolô'),
        ('Thư Chung', 'Các Thư Chung Tông Đồ'),
        ('Khải Huyền', 'Sách Khải Huyền'),
    ]

    order_num = models.PositiveSmallIntegerField(unique=True, verbose_name="Thứ tự (1-73)")
    name = models.CharField(max_length=100, verbose_name="Tên Sách")
    code = models.CharField(max_length=15, verbose_name="Viết tắt chuẩn", db_index=True)
    slug = models.SlugField(max_length=120, unique=True, verbose_name="Slug URL")
    testament = models.CharField(max_length=2, choices=TESTAMENT_CHOICES, db_index=True, verbose_name="Giao Ước")
    group = models.CharField(max_length=50, choices=GROUP_CHOICES, db_index=True, verbose_name="Nhóm Sách")
    total_chapters = models.PositiveSmallIntegerField(default=1, verbose_name="Tổng số chương")
    description = models.TextField(blank=True, default="", verbose_name="Giới thiệu khái quát")

    class Meta:
        ordering = ['order_num']
        verbose_name = "Sách Kinh Thánh"
        verbose_name_plural = "73 Cuốn Kinh Thánh"

    def __str__(self):
        return f"{self.order_num:02d}. {self.name} ({self.code})"

class Chapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters')
    number = models.PositiveSmallIntegerField(verbose_name="Chương số")
    title = models.CharField(max_length=150, blank=True, default="", verbose_name="Tiêu đề chương")
    audio_url = models.URLField(blank=True, default="", verbose_name="Link Audio (nếu có)")

    class Meta:
        ordering = ['book__order_num', 'number']
        unique_together = ('book', 'number')
        verbose_name = "Chương"
        verbose_name_plural = "Các Chương"

    def __str__(self):
        return f"{self.book.name} - Chương {self.number}"

class Verse(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='verses')
    verse_number = models.PositiveSmallIntegerField(verbose_name="Câu số")
    section_title = models.CharField(max_length=255, blank=True, default="", verbose_name="Tiêu đề mục lớn")
    sub_title = models.CharField(max_length=255, blank=True, default="", verbose_name="Tiêu đề phân đoạn")
    text = models.TextField(verbose_name="Lời Chúa (Có dấu)")
    text_unaccent = models.TextField(db_index=True, verbose_name="Lời Chúa (Không dấu phục vụ tìm kiếm)")
    footnote = models.CharField(max_length=255, blank=True, default="", verbose_name="Tham chiếu/Chú thích")

    class Meta:
        ordering = ['chapter__book__order_num', 'chapter__number', 'verse_number']
        unique_together = ('chapter', 'verse_number')
        verbose_name = "Câu Kinh Thánh"
        verbose_name_plural = "Các Câu Kinh Thánh"

    def save(self, *args, **kwargs):
        # Auto-compute unaccented text for ultra-fast search
        if not self.text_unaccent or kwargs.get('update_fields') is None:
            self.text_unaccent = remove_vietnamese_accents(self.text)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.chapter.book.code} {self.chapter.number},{self.verse_number}"

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'verse')
        ordering = ['-created_at']
        verbose_name = "Đánh dấu (Bookmark)"
        verbose_name_plural = "Danh sách Đánh dấu"

    def __str__(self):
        return f"{self.user.username} bookmarked {self.verse}"

class Highlight(models.Model):
    COLOR_CHOICES = [
        ('yellow', 'Vàng ấm'),
        ('green', 'Xanh lá dịu'),
        ('blue', 'Xanh lam thanh thản'),
        ('pink', 'Hồng nhạt'),
        ('purple', 'Tím phụng vụ'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='highlights')
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE, related_name='highlights')
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='yellow')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'verse')
        ordering = ['-created_at']
        verbose_name = "Bôi màu (Highlight)"
        verbose_name_plural = "Danh sách Bôi màu"

    def __str__(self):
        return f"{self.user.username} highlighted {self.verse} ({self.color})"

class PersonalNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField(verbose_name="Nội dung ghi chú cá nhân / suy niệm")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'verse')
        ordering = ['-updated_at']
        verbose_name = "Ghi chú cá nhân"
        verbose_name_plural = "Các Ghi chú cá nhân"

    def __str__(self):
        return f"Ghi chú của {self.user.username} tại {self.verse}"

class ReadingPlan(models.Model):
    name = models.CharField(max_length=150, verbose_name="Tên Kế Hoạch Đọc")
    slug = models.SlugField(max_length=160, unique=True)
    description = models.TextField(verbose_name="Mô tả kế hoạch")
    total_days = models.PositiveSmallIntegerField(default=365, verbose_name="Tổng số ngày")

    def __str__(self):
        return self.name

class ReadingPlanDay(models.Model):
    plan = models.ForeignKey(ReadingPlan, on_delete=models.CASCADE, related_name='days')
    day_number = models.PositiveSmallIntegerField(verbose_name="Ngày thứ")
    title = models.CharField(max_length=150, verbose_name="Tiêu đề ngày đọc")
    readings_label = models.CharField(max_length=200, verbose_name="Các đoạn cần đọc (VD: St 1-2; Tv 1; Mt 1)")
    ot_reading = models.CharField(max_length=100, blank=True, default="", verbose_name="Cựu Ước")
    psalm_reading = models.CharField(max_length=100, blank=True, default="", verbose_name="Thánh Vịnh")
    nt_reading = models.CharField(max_length=100, blank=True, default="", verbose_name="Tân Ước")

    class Meta:
        ordering = ['plan', 'day_number']
        unique_together = ('plan', 'day_number')
        verbose_name = "Ngày đọc"
        verbose_name_plural = "Lịch trình ngày đọc"

    def __str__(self):
        return f"Ngày {self.day_number}: {self.readings_label}"

class UserReadingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_progress')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    completed = models.BooleanField(default=True)
    last_read_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'chapter')
        verbose_name = "Tiến độ đọc"
        verbose_name_plural = "Tiến độ đọc các chương"

class UserPlanProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plan_progress')
    plan_day = models.ForeignKey(ReadingPlanDay, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'plan_day')
        verbose_name = "Tiến độ kế hoạch"
        verbose_name_plural = "Tiến độ kế hoạch theo ngày"
