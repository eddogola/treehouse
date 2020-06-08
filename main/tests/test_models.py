from django.test import TestCase
from django.core.validators import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
import datetime

from main import models

class BookModelTests(TestCase):
    
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123'
        )
        self.profile = models.Profile.objects.create(
            user=self.user
        )
        self.user1 = get_user_model().objects.create_user(
            username='testuser1',
            email='testuser1@email.com',
            password='testpass123'
        )
        self.profile1 = models.Profile.objects.create(
            user=self.user1
        )       
        self.book1 = models.Book.objects.create(
                isbn='1234567890',
                title='The Pearl',
                author='John Steinbeck',
                description = 'test description'
            )
    
    def test_book_isbn_is_digits_and_correct_length(self):
        book = models.Book(
                isbn='123456789a',
                title='The Pearl',
                author='John Steinbeck',
                description = 'a book on the human trait of good and the'
                'struggle between good and evil'
            )
        with self.assertRaises(ValidationError):
            book.full_clean()
    
    def test_book_review_created(self):
        review = models.Review.objects.create(
            book=self.book1,
            reviewer=self.profile,
            body='very scrumptious',
        )
        models.Review.objects.filter(reviewer=self.profile).exists()
        self.assertIn(review, self.profile.reviews.all())
        self.assertEqual(
            models.Review.objects.first().body, 'very scrumptious' 
        )
     
    def test_book_review_comments(self):
        book2 = models.Book.objects.create(
                isbn='12345678901',
                title='The Cow',
                author='John Stain',
                description = 'test description'
            )
        review = models.Review.objects.create(
            book=book2,
            reviewer=self.profile,
            body='very scrumptious',
        )
        comment1 = models.Comment.objects.create(
            review=review,
            commenter=self.profile1,
            body='check this out:D',
        )
        comment2 = models.Comment.objects.create(
            review=review,
            commenter=self.profile1,
            body='i really love your review',
        )
        self.assertEqual([comment1, comment2], list(review.comments.all()))
        
    def text_book_review_likes(self):
        review = models.Review.objects.create(
            book=self.book1,
            reviewer=self.profile,
            body='very scrumptious',
        )
        models.Like.objects.create(
            review=review,
            liker=self.profile1,
        )
        like = models.Like.objects.first()
        self.assertEqual(like.review.body, 'very scrumptious')
        self.assertEqual(review.get_likes(), 1)
    
    def test_book_rating(self):
        #test max-value
        rating = models.Rating.objects.create(
            book=self.book1,
            rating=6,
            rater=self.profile
        )
        self.assertIn(rating, self.profile.ratings.all())
        with self.assertRaises(ValidationError):
            rating.full_clean()        
    
class BookClubModelTests(TestCase):
    
    def setUp(self):
        super().setUp()
        self.book_club = models.BookClub.objects.create(
            name='Test Book Club',
            location='Nairobi',
            description='lorem ipsum dolor sit amet',
        )
        self.book1 = models.Book.objects.create(
                isbn='1234567890',
                title='The Pearl',
                author='John Steinbeck',
                description = 'test description'
            )
        self.book2 = models.Book.objects.create(
                isbn='12345678901',
                title='The Cow',
                author='John Stain',
                description = 'test description'
            )
        self.read1 = models.BookClubRead.objects.create(
            book=self.book1,
            book_club=self.book_club,
            read_duration=10
        )
    
    def test_book_club_read_end_date(self):
        self.assertEqual(self.read1.current_read, True)
        end_date = self.read1.start_date + datetime.timedelta(days=10)
        self.assertEqual(end_date, self.read1.end_date())
        
    def test_book_club_can_have_only_one_active_read(self):
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                models.BookClubRead.objects.create(
                    book=self.book1,
                    book_club=self.book_club,
                    read_duration=10,
                    current_read=True
                )
            
        self.read1.current_read = False
        self.read1.save()
        
        read2 = models.BookClubRead.objects.create(
            book=self.book2,
            book_club=self.book_club,
            read_duration=10,
            current_read=True,
        )
        self.assertTrue(models.BookClubRead.objects.filter(
            book=self.book2,
            book_club=self.book_club,
        ).exists())
        
    def test_book_club_book_unique_together(self):
        #add another read similar to read1 - raises error
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                models.BookClubRead.objects.create(
                    book=self.book1,
                    book_club=self.book_club,
                    read_duration=10,
                    current_read=True
                )
            
        #add another read different from read1 - no error
        read2 = models.BookClubRead.objects.create(
            book=self.book2,
            book_club=self.book_club,
            read_duration=10,
            current_read=False,
        )
        self.assertTrue(models.BookClubRead.objects.filter(
            book=self.book2,
            book_club=self.book_club,
        ).exists())
            
    def test_book_club_members(self):
        profile = models.Profile.objects.create(
            user=get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123'))
        models.BookClubMember.objects.create(
            book_club=self.book_club,
            member=profile,
        )
        self.assertIn(profile, self.book_club.members.all())
        self.assertIn(self.book_club, profile.book_clubs.all())
    
    def test_book_club_admins(self):
        profile = models.Profile.objects.create(
            user=get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123'))
        models.BookClubAdmin.objects.create(
            book_club=self.book_club,
            admin=profile,
        )
        self.assertIn(profile, self.book_club.admins.all())
        self.assertIn(self.book_club, profile.admin_book_clubs.all())
        
    def test_current_read(self):
        self.assertEqual(
            self.book_club.current_read(), self.book1
        )
        
    def test_profile_is_admin(self):
        profile = models.Profile.objects.create(
            user=get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123'))
        models.BookClubAdmin.objects.create(
            admin=profile,
            book_club=self.book_club,
        )
        self.assertTrue(profile.is_admin())
        self.assertFalse(profile.is_member())
    
    def test_profile_is_member(self):
        profile = models.Profile.objects.create(
            user=get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123'))
        models.BookClubMember.objects.create(
            member=profile,
            book_club=self.book_club,
        )
        self.assertTrue(profile.is_member())
        self.assertFalse(profile.is_admin())
        
class DiscussionTests(TestCase):
    pass