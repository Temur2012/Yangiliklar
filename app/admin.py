from django.contrib import admin
from app.models import Category, News, ContactMessage, Comment


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display       = ('title', 'category', 'views', 'is_breaking', 'is_main_slider', 'created_at')
    list_filter        = ('category', 'is_breaking', 'is_main_slider')
    search_fields      = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable      = ('is_breaking', 'is_main_slider')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display        = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display    = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter     = ('is_read',)
    search_fields   = ('name', 'email', 'subject')
    list_editable   = ('is_read',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    actions         = ['mark_read', 'mark_unread']

    def mark_read(self, request, qs):
        qs.update(is_read=True)
    mark_read.short_description = "✅ O'qildi deb belgilash"

    def mark_unread(self, request, qs):
        qs.update(is_read=False)
    mark_unread.short_description = "❌ O'qilmagan deb belgilash"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ('user', 'news', 'text', 'created_at')
    search_fields = ('user__username', 'text')
    list_filter   = ('created_at',)