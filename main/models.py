from django.db import models
from django.db.models.aggregates import Sum
from django.core.validators import RegexValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.db.models.constraints import UniqueConstraint, CheckConstraint
from django.db.models import Q
import datetime
import uuid
import os

class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    isbn = models.CharField(unique=True, max_length=13, validators=[
        RegexValidator(r'^\d{10,13}$')])
    title = models.CharField(max_length=200, unique=True)
    author = models.CharField(max_length=200)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def cover_upload_path(instance, filename):
        _, ext = os.path.splitext(filename)
        return 'book-covers/{}{}'.format(instance.title, ext)

    cover = models.ImageField(blank=True, null=True, upload_to=cover_upload_path)
    
    def __str__(self):
        return '{} - {}'.format(
            self.title,
            self.author,
        )

    def get_book_rating(self):
        ratings = [rating.rating for rating in self.ratings.all()]
        try:
            rating = sum(ratings) / len(ratings)
            return rating
        except ZeroDivisionError:
            return 0

class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='reviews')
    body = models.TextField()
    created = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return self.body[:20] + '...'
    
    def get_likes(self):
        return self.likes.count()
    
class ReviewComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    commentor = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    created = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['review', 'commentor']
        ordering = ['-created']
    
class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(Review, related_name='likes', on_delete=models.CASCADE)
    liker = models.ForeignKey('Profile', related_name='likes', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['review', 'liker']
    
class Rating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField(validators=[
        MaxValueValidator(5)])
    rater = models.ForeignKey('Profile', on_delete=models.PROTECT, related_name='ratings')

    class Meta:
        unique_together = ['book', 'rater']
    
    def __str__(self):
        return '{} - {}'.format(
            self.book.title,
            self.rating
        )
        
class Profile(models.Model):
    
    def avatar_upload_path(instance, filename):
        name, ext = os.path.splitext(filename)
        return '{}/{}'.format(
            instance.user.username,
            uuid.uuid4 + ext,
        )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class Role(models.Model):

    FOUNDER = 1
    ADMIN = 2
    REGULAR = 3
    ROLES = (
        (FOUNDER, 'Founder'),
        (ADMIN, 'Admin'),
        (REGULAR, 'Regular'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.IntegerField(choices=ROLES, default=REGULAR, unique=True)

    def __str__(self):
        return self.ROLES[self.role - 1][1]

################ book club models #################################
class BookClub(models.Model):

    def logo_upload_path(instance, filename):
        _, ext = os.path.splitext(filename)
        return '{}/{}{}'.format(
            'book-clubs-logos', 
            uuid.uuid4(),
            ext)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    location = models.CharField(max_length=200)
    description = models.TextField()
    logo = models.ImageField(blank=True, null=True, upload_to=logo_upload_path)
    members = models.ManyToManyField(Profile, through='BookClubMember', related_name='book_clubs')
    reads = models.ManyToManyField(Book, through='BookClubRead', related_name='book_clubs')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return '{} - {}'.format(
            self.name,
            self.location
        )
    
    def current_read(self):
        read = BookClubRead.objects.get(book_club=self,current_read=True)
        return read.book
    
    def is_founder(self, profile):
        role = Role.objects.get(role=Role.FOUNDER)
        return BookClubMember.objects.filter(profile=profile, role=role).exists()
    
    def is_admin(self, profile):
        role = Role.objects.get(role=Role.ADMIN)
        return BookClubMember.objects.filter(profile=profile, role=role).exists()
    
    def is_regular(self, profile):
        role = Role.objects.get(role=Role.REGULAR)
        return BookClubMember.objects.filter(profile=profile, role=role).exists()
        
class BookClubMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(Role, related_name='members', on_delete=models.CASCADE)
    book_club = models.ForeignKey(BookClub, on_delete=models.CASCADE, related_name='book_club_members')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='book_club_members')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}: {}'.format(self.profile, self.book_club)
    
class BookClubRead(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, related_name='book_club_reads', on_delete=models.CASCADE)
    book_club = models.ForeignKey(BookClub, related_name='book_club_reads', on_delete=models.CASCADE)
    current_read = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    #stipulated time for the read (in days)
    read_duration = models.PositiveIntegerField()
    
    class Meta:
        constraints = (
            UniqueConstraint(fields=['book', 'book_club'], name='unique_book_club_read'),
            UniqueConstraint(fields=['book_club', 'current_read'], name='single_active_book_club_read',
                             condition=Q(current_read=True)),
        )
        ordering = ['-start_date']
    
    def end_date(self):
        duration = datetime.timedelta(days=self.read_duration)
        return self.start_date + duration
    
##########book discussion
class BookDiscussion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=200, unique=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='discussions')
    starter = models.ForeignKey(Profile, on_delete=models.CASCADE,
                                related_name='book_discussions')
    created = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def  __str__(self):
        return '{} : {}'.format(
            self.book,
            self.question)
    
class BookDiscussionComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discussion = models.ForeignKey(BookDiscussion, related_name='comments', 
                                   on_delete=models.CASCADE)
    commentor = models.ForeignKey(Profile, on_delete=models.PROTECT, 
                                  related_name='book_discussions_comments')
    body = models.TextField()
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.body[:60] + '...'
        
class BookCommentReply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(BookDiscussionComment, on_delete=models.CASCADE, 
                                related_name='replies')
    body = models.TextField()
    replier = models.ForeignKey(Profile, on_delete=models.PROTECT, 
                                related_name='book_comments_replies')
    created = models.DateTimeField(auto_now=True)
    
####thread discussion
class BookClubThread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_club = models.ForeignKey(BookClub, on_delete=models.CASCADE, 
                                  related_name='threads')
    title = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return '{} - {}'.format(
            self.title,
            self.book_club.name)

class ThreadDiscussion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(BookClubThread, on_delete=models.CASCADE,
                                         related_name='discussions')
    question = models.CharField(max_length=200, unique=True, default='General')
    starter = models.ForeignKey(BookClubMember, on_delete=models.CASCADE,
                                related_name='thread_discussions')
    created = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.question
    
class ThreadDiscussionComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discussion = models.ForeignKey(ThreadDiscussion, related_name='comments', 
                                   on_delete=models.CASCADE)
    commentor = models.ForeignKey(Profile, on_delete=models.PROTECT, 
                                  related_name='thread_discussions_comments')
    body = models.TextField()
    created = models.DateTimeField(auto_now=True)
    
class ThreadCommentReply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(ThreadDiscussionComment, on_delete=models.CASCADE, 
                                related_name='replies')
    body = models.TextField()
    replier = models.ForeignKey(Profile, on_delete=models.PROTECT, 
                                related_name='thread_comments_replies')
    created = models.DateTimeField(auto_now=True)