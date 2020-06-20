from django.views.generic import ListView, DetailView
from django.db.models import Count

from main import models

class BookListView(ListView):
    model = models.Book
    template_name = 'main/books.html'
    context_object_name = 'books'

class BookDetailView(DetailView):
    model = models.Book
    template_name = 'main/book.html'

class ReviewList(ListView):
    model = models.Review
    template_name = 'main/reviews.html'
    context_object_name = 'reviews'

class ReviewDetail(DetailView):
    model = models.Review
    template_name = 'main/review.html'

class BookDiscussionList(ListView):
    template_name = 'main/book_discussions.html'
    context_object_name = 'books'

    def get_queryset(self):
        qs = models.Book.objects.annotate(discussion_count=Count('discussions'))
        qs = qs.exclude(discussion_count=0)
        qs = qs.order_by('-discussion_count')
        return qs

class BookDiscussionDetail(DetailView):
    template_name = 'main/book_discussion.html'
    context_object_name = 'discussion'
    
    def get_queryset(self):
        qs = models.BookDiscussion.objects.\
             prefetch_related('comments', 'comments__replies')
        return qs

class BookClubDetail(DetailView):
    model = models.BookClub
    template_name = 'main/book_club.html'
    context_obejct_name = 'book_club'