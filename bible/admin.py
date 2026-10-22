from django.contrib import admin
from .models import (
    Book, Chapter, Verse, Bookmark, Highlight, PersonalNote,
    ReadingPlan, ReadingPlanDay, UserReadingProgress, UserPlanProgress
)

# Custom admin site branding
admin.site.site_header = "Kinh Thánh Công Giáo — Hệ Thống Quản Trị"
admin.site.site_title = "Quản Trị Kinh Thánh"
admin.site.index_title = "Trung Tâm Điều Hành Dữ Liệu & Độc Giả"

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('order_num', 'name', 'code', 'slug', 'testament', 'group', 'total_chapters')
    list_filter = ('testament', 'group')
    search_fields = ('name', 'code', 'slug')
    ordering = ('order_num',)

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('book', 'number', 'title', 'audio_url')
    list_filter = ('book__testament', 'book')
    search_fields = ('book__name', 'title')

@admin.register(Verse)
class VerseAdmin(admin.ModelAdmin):
    list_display = ('chapter', 'verse_number', 'sub_title', 'short_text')
    list_filter = ('chapter__book__testament', 'chapter__book')
    search_fields = ('text', 'text_unaccent')

    def short_text(self, obj):
        return obj.text[:60] + "..." if len(obj.text) > 60 else obj.text

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'verse', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'verse__text')

@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ('user', 'verse', 'color', 'created_at')
    list_filter = ('color', 'created_at')
    search_fields = ('user__username', 'verse__text')

@admin.register(PersonalNote)
class PersonalNoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'verse', 'updated_at')
    search_fields = ('user__username', 'content')

@admin.register(ReadingPlan)
class ReadingPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_days')

@admin.register(ReadingPlanDay)
class ReadingPlanDayAdmin(admin.ModelAdmin):
    list_display = ('plan', 'day_number', 'title', 'readings_label')
    list_filter = ('plan',)

admin.site.register(UserReadingProgress)
admin.site.register(UserPlanProgress)
