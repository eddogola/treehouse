from django.views.generic import TemplateView
from django.urls import path

from main import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('books/<uuid:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('reviews/<uuid:pk>/', views.ReviewDetail.as_view(), name='review_detail'),
]