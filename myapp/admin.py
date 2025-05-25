from django.contrib import admin
from .models import User, Books, BookRequest, Reviews, Wishlists, Message

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'role', 'location', 'created_at')
    search_fields = ('name', 'email')
    list_filter = ('role', 'location')


@admin.register(Books)
class BooksAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'genre', 'condition', 'status', 'owner', 'created_at')
    search_fields = ('title', 'author', 'genre')
    list_filter = ('condition', 'status', 'genre', 'owner')


@admin.register(BookRequest)
class BookRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'seeker', 'status', 'requested_at', 'updated_at')
    search_fields = ('book__title', 'seeker__name')
    list_filter = ('status',)


@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'reviewer', 'book', 'rating', 'reviewed_at')
    search_fields = ('reviewer__name', 'book__title')
    list_filter = ('rating',)


@admin.register(Wishlists)
class WishlistsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'author', 'genre', 'added_at')
    search_fields = ('user__name', 'title', 'author', 'genre')
    list_filter = ('genre',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'book', 'sent_at')
    search_fields = ('sender__name', 'receiver__name', 'book__title')
    list_filter = ('sent_at',)
