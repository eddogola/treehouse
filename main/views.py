from django.views.generic import ListView, DetailView

from main import models

class BookListView(ListView):
    model = models.Book
    template_name = 'main/books.html'
    context_object_name = 'books'

class BookDetailView(DetailView):
    model = models.Book
    template_name = 'main/book.html'

class ReviewDetail(DetailView):
    model = models.Review
    template_name = 'main/review.html'