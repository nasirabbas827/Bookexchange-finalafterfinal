from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_create, name='book_create'),
    path('books/edit/<int:book_id>/', views.book_edit, name='book_edit'),
    path('books/delete/<int:book_id>/', views.book_delete, name='book_delete'),
    path('books/request/<int:book_id>/', views.request_book, name='request_book'),
    path('seeker/requests/', views.seeker_requests, name='seeker_requests'),
    path('seeker/requests/delete/<int:request_id>/', views.delete_request, name='delete_request'),
    path('seeker/messages/<int:owner_id>/<int:seeker_id>/<int:book_id>/', views.message_thread, name='message_thread'),
    path('books/review/<int:book_id>/', views.book_review, name='book_review'),
    path('owner/messages/<int:owner_id>/<int:seeker_id>/<int:book_id>/', views.ownermessage_thread, name='owner_message_thread'),
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('wishlist/add/', views.add_to_wishlist_manual, name='add_to_wishlist_manual'),
    path('wishlist/delete/<int:wishlist_id>/', views.wishlist_delete, name='wishlist_delete'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset-confirm/', views.password_reset_confirm, name='password_reset_confirm'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
