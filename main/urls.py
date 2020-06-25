from django.views.generic import TemplateView
from django.urls import path

from main import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('books/<uuid:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('reviews/', views.ReviewList.as_view(), name='review_list'),
    path('reviews/<uuid:pk>/', views.ReviewDetail.as_view(), name='review_detail'),
    path('books/discussions/', views.BookDiscussionList.as_view(), name='book_discussion_list'),
    path('books/discussions/<uuid:pk>', views.BookDiscussionDetail.as_view(), name='book_discussion_detail'),
    path('book-clubs/', views.BookClubList.as_view(), name='book_club_list'),
    path('book-clubs/<uuid:pk>/', views.BookClubDetail.as_view(), name='book_club_detail'),
    path('book-clubs/<uuid:pk>/members/', views.BookClubMemberList.as_view(), name='book_club_members'),
    path('book-clubs/<uuid:pk>/threads/', views.BookClubThreadList.as_view(), name='book_club_threads'),
    path('book-clubs/<uuid:pk>/reads/', views.BookClubReadsList.as_view(), name='book_club_reads'),
    path('thread-discussions/<uuid:pk>/', views.ThreadDiscussionDetail.as_view(), name='thread_discussion_detail'),
]