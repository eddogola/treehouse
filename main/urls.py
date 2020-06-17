from django.views.generic import TemplateView
from django.urls import path

from main import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('books/', views.BookListView.as_view(), name='book_list'),
]