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

class BookClubList(ListView):
    model = models.BookClub
    template_name = 'main/book_clubs.html'
    context_object_name = 'book_clubs'

class BookClubDetail(DetailView):
    model = models.BookClub
    template_name = 'main/book_club.html'
    context_object_name = 'book_club'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        founders = models.BookClubMember.objects\
                    .filter(role__role=models.Role.FOUNDER,
                            book_club=self.object)
        admins = models.BookClubMember.objects\
                    .filter(role__role=models.Role.ADMIN,
                            book_club=self.object)
        #obtain Profile instead of BookClubMember objects
        ctx['founders'] = [founder.profile for founder in founders]
        ctx['admins'] = [admin.profile for admin in admins]
        return ctx

class BookClubMemberList(ListView):
    template_name = 'main/book_club_members.html'
    context_object_name = 'members'

    def get_queryset(self):
        book_club = models.BookClub.objects.get(id=self.kwargs.get('pk'))
        members = models.BookClubMember.objects.filter(book_club=book_club)
        return members


    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        book_club = models.BookClub.objects.get(id=self.kwargs.get('pk'))
        ctx['book_club'] = book_club
        return ctx

class BookClubThreadList(ListView):
    template_name = 'main/book_club_threads.html'
    context_object_name = 'threads'

    def get_queryset(self):
        book_club = models.BookClub.objects.get(id=self.kwargs.get('pk'))
        qs = models.BookClubThread.objects.filter(book_club=book_club)
        return qs

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        book_club = models.BookClub.objects.get(id=self.kwargs.get('pk'))
        ctx['book_club'] = book_club
        return ctx
        
class BookClubReadsList(ListView):
    template_name = 'main/book_club_reads.html'
    context_object_name = 'reads'

    def get_queryset(self):
        book_club = models.BookClub.objects.get(pk=self.kwargs.get('pk'))
        qs = models.BookClubRead.objects.filter(book_club=book_club)
        return qs

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        book_club = models.BookClub.objects.get(pk=self.kwargs.get('pk'))
        ctx['book_club'] = book_club
        return ctx

class ThreadDiscussionDetail(DetailView):
    template_name = 'main/thread_discussion.html'
    context_object_name = 'discussion'
    
    def get_queryset(self):
        qs = models.ThreadDiscussion.objects.\
             prefetch_related('comments', 'comments__replies')
        return qs