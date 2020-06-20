from django.contrib import admin
from django.utils.html import format_html
from sorl.thumbnail import get_thumbnail

from main import models

class BookDiscussionsInline(admin.TabularInline):
    model = models.BookDiscussion

@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('isbn', 'title', 'author',)
    inlines = (
        BookDiscussionsInline,
    )

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

class BookDiscussionCommentInline(admin.TabularInline):
    model = models.BookDiscussionComment

@admin.register(models.BookDiscussion)
class BookDiscussionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'starter', 'created')
    inlines = (
        BookDiscussionCommentInline,
    )

class BookDiscussionCommentReply(admin.TabularInline):
    model = models.BookCommentReply

@admin.register(models.BookDiscussionComment)
class BookDiscussionCommentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'commentor', 'created')
    inlines = (
        BookDiscussionCommentReply,
    )

class BookClubReadInline(admin.TabularInline):
    model = models.BookClubRead

class BookClubMemberInline(admin.TabularInline):
    model = models.BookClubMember

class BookClubThreadInline(admin.TabularInline):
    model = models.BookClubThread

class BookClubAdmin(admin.ModelAdmin):
    inlines = (
        BookClubReadInline,
        BookClubMemberInline,
        BookClubThreadInline,
    )

class ThreadDiscussionCommentInline(admin.TabularInline):
    model = models.ThreadDiscussionComment

@admin.register(models.ThreadDiscussion)
class BookDiscussionAdmin(admin.ModelAdmin):
    inlines = (
        ThreadDiscussionCommentInline,
    )

class ThreadDiscussionCommentReply(admin.TabularInline):
    model = models.ThreadCommentReply

@admin.register(models.ThreadDiscussionComment)
class BookDiscussionCommentAdmin(admin.ModelAdmin):
    inlines = (
        ThreadDiscussionCommentReply,
    )

admin.site.register(models.Profile)
admin.site.register(models.Role)