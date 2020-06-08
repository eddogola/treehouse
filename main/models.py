from django.db import models
from django.db.models.aggregates import Sum
from django.core.validators import RegexValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.db.models.constraints import UniqueConstraint
from django.db.models.query import Q
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
    
    def __str__(self):
        return '{} - {}'.format(
            self.title,
            self.author,
        )

class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='reviews')
    body = models.TextField()
    
    def __str__(self):
        return self.body[:20] + '...'
    
    def get_likes(self):
        return self.likes.count()
    
class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    created = models.DateTimeField(auto_now=True)
    
class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(Review, related_name='likes', on_delete=models.CASCADE)
    liker = models.ForeignKey('Profile', related_name='likes', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)
    
class Rating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField(validators=[
        MaxValueValidator(5)])
    rater = models.ForeignKey('Profile', on_delete=models.PROTECT, related_name='ratings')
    
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
    
    def is_admin(self):
        if self.book_club_admins.exists():
            return True
        return False
    
    def is_member(self):
        if self.book_club_members.exists():
            return True
        return False
    
    def upvote(self, discussion_comment_id):
        comment = DiscussionComment.objects.get(id=discussion_comment_id)
        CommentVote.objects.create(
            comment=comment,
            voter=self,
            up=1,
        )
        
    def downvote(self, discussion_comment_id):
        comment = DiscussionComment.objects.get(id=discussion_comment_id)
        CommentVote.objects.create(
            comment=comment,
            voter=self,
            down=1,
        )
    
class BookClub(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    location = models.CharField(max_length=200)
    description = models.TextField()
    members = models.ManyToManyField(Profile, through='BookClubMember', related_name='book_clubs')
    reads = models.ManyToManyField(Book, through='BookClubRead', related_name='book_clubs')
    admins = models.ManyToManyField(Profile, through='BookClubAdmin', related_name='admin_book_clubs')
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
        
class BookClubMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_club = models.ForeignKey(BookClub, on_delete=models.CASCADE, related_name='book_club_members')
    member = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='book_club_members')
    created = models.DateTimeField(auto_now_add=True)
    
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
    
    def end_date(self):
        duration = datetime.timedelta(days=self.read_duration)
        return self.start_date + duration

class BookClubAdmin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin = models.ForeignKey(Profile, related_name='book_club_admins', on_delete=models.CASCADE)
    book_club = models.ForeignKey(BookClub, related_name='book_club_admins', on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
  
class BookClubThread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_club = models.ForeignKey(BookClub, on_delete=models.CASCADE, 
                                  related_name='threads')
    title = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now=True)
    
class Discussion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=200, unique=True)
    comments = models.ForeignKey('DiscussionComment', on_delete=models.CASCADE, 
                                 related_name='%(class)ss')
    created = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
    
class DiscussionComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    commenter = models.ForeignKey(Profile, on_delete=models.PROTECT, 
                                  related_name='discussion_comments')
    body = models.TextField()
    created = models.DateTimeField(auto_now=True)
    
    def get_upvote_count(self):
        upvotes = self.votes.filter(up=1)
        return len(list(upvotes))
    
    def get_downvote_count(self):
        downvotes = self.votes.filter(down=1)
        return len(list(downvotes))
    
class CommentVote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(DiscussionComment, on_delete=models.CASCADE, 
                                related_name='votes')
    voter = models.ForeignKey(Profile, on_delete=models.CASCADE, 
                              related_name='votes')
    up = models.PositiveIntegerField()
    down = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('comment', 'voter',)
    
class CommentReply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(DiscussionComment, on_delete=models.CASCADE, 
                                related_name='replies')
    body = models.TextField()
    replier = models.ForeignKey(Profile, on_delete=models.PROTECT, 
                                related_name='comment_replies')
    created = models.DateTimeField(auto_now=True)
    
class BookDiscussion(Discussion):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='discussions')
    starter = models.ForeignKey(Profile, on_delete=models.CASCADE,
                                related_name='started_discussions')
    
class ThreadDiscussion(Discussion):
    book_club_thread = models.ForeignKey(BookClubThread, on_delete=models.CASCADE,
                                         related_name='discussions')
    starter = models.ForeignKey(BookClubAdmin, on_delete=models.CASCADE,
                                related_name='started_discussions')
    