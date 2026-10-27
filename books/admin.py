from django.contrib import admin
from .models import (
    UserProfile, Friendship, Book, ReadList, ReadListItem,
    RatingReview, ReviewComment, Activity, FAQ, SupportTicket
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'favorite_genres', 'created_at')
    search_fields = ('user__username', 'bio')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'first_publish_year', 'genre', 'average_rating', 'ratings_count')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('genre',)


@admin.register(ReadList)
class ReadListAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'list_type', 'is_default', 'is_public', 'created_at')
    list_filter = ('list_type', 'is_default', 'is_public')
    search_fields = ('name', 'user__username')


@admin.register(ReadListItem)
class ReadListItemAdmin(admin.ModelAdmin):
    list_display = ('readlist', 'book', 'added_at')
    search_fields = ('book__title', 'readlist__name')


@admin.register(RatingReview)
class RatingReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'rating', 'contains_spoilers', 'created_at')
    list_filter = ('rating', 'contains_spoilers')
    search_fields = ('user__username', 'book__title', 'review_text')


@admin.register(ReviewComment)
class ReviewCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'review', 'created_at')
    search_fields = ('user__username', 'comment_text')


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'created_at')
    search_fields = ('from_user__username', 'to_user__username')


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'book', 'created_at')
    list_filter = ('activity_type',)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('question', 'answer')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'subject', 'user', 'priority', 'status', 'created_by_ai', 'created_at')
    list_filter = ('status', 'priority', 'created_by_ai')
    search_fields = ('ticket_id', 'subject', 'message', 'guest_email')
