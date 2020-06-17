from django.contrib import admin
from django.utils.html import format_html
from sorl.thumbnail import get_thumbnail

from main import models

@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('isbn', 'title', 'author',)

    def book_cover(self, obj):
        cover = get_thumbnail(obj.cover, '152x131')
        return format_html(
            "<img src='{}'>".format(cover.url)
        )

class LikesInline(admin.TabularInline):
    model = models.Like

class ReviewCommentsInline(admin.TabularInline):
    model = models.ReviewComment

@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'reviewer', 'review')
    inlines = (
        LikesInline,
        ReviewCommentsInline,
    )

    def review(self, obj):
        return obj.body[:60] + '...'

admin.site.register(models.Profile)