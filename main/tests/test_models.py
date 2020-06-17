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
        comment1 = models.ReviewComment.objects.create(
            review=review,
            commentor=self.profile1,
            body='check this out:D',
        )
        comment2 = models.ReviewComment.objects.create(
            review=review,
            commentor=self.profile,
            body='i really love your review',
        )
        self.assertIn(comment1, review.comments.all())
        self.assertIn(comment2, review.comments.all())

    def test_book_review_can_be_commented_only_once_by_a_single_profile(self):
        review = models.Review.objects.create(
            book=self.book1,
            reviewer=self.profile,
            body='very scrumptious',
        )
        models.ReviewComment.objects.create(
            review=review,
            commentor=self.profile,
            body='funny review lol')
        with self.assertRaises(IntegrityError):
            models.ReviewComment.objects.create(
                review=review,
                commentor=self.profile,
                body='yadda yadda')
        
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

    def test_review_can_be_liked_by_a_profile_only_once(self):
        review = models.Review.objects.create(
            book=self.book1,
            reviewer=self.profile,
            body='very scrumptious',
        )
        models.Like.objects.create(
            review=review,
            liker=self.profile1,
        )
        with self.assertRaises(IntegrityError):
            models.Like.objects.create(
            review=review,
            liker=self.profile1)
    
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

    def test_book_can_be_rated_only_once_by_a_single_profile(self):
        models.Rating.objects.create(
            book=self.book1,
            rater=self.profile,
            rating=4)
        with self.assertRaises(IntegrityError):
                models.Rating.objects.create(
                book=self.book1,
                rater=self.profile,
                rating=3)            

    def test_get_book_rating(self):
        models.Rating.objects.create(
            book=self.book1,
            rater=self.profile,
            rating=4)
        models.Rating.objects.create(
                book=self.book1,
                rater=self.profile1,
                rating=3)
        self.assertEqual(self.book1.get_book_rating(), 3.5)   
    
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
        models.Role.objects.create(role=models.Role.FOUNDER)
        models.Role.objects.create(role=models.Role.ADMIN)
        models.Role.objects.create(role=models.Role.REGULAR)
    
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
        
    def test_current_read(self):
        self.assertEqual(
            self.book_club.current_read(), self.book1
        ) 
        
    def test_book_club_regular_member(self):
        profile = models.Profile.objects.create(
            user=get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123'))
        models.BookClubMember.objects.create(
            role=models.Role.objects.get(role=models.Role.REGULAR),
            book_club=self.book_club,
            profile=profile,
        )
        self.assertIn(profile, self.book_club.members.all())
        self.assertIn(self.book_club, profile.book_clubs.all())
        self.assertTrue(self.book_club.is_regular(profile))
        self.assertFalse(self.book_club.is_admin(profile))
        self.assertFalse(self.book_club.is_founder(profile))
    
    def test_book_club_admin_member(self):
        profile = models.Profile.objects.create(
            user=get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123'))
        models.BookClubMember.objects.create(
            role=models.Role.objects.get(role=models.Role.ADMIN),
            book_club=self.book_club,
            profile=profile,
        )
        self.assertIn(profile, self.book_club.members.all())
        self.assertIn(self.book_club, profile.book_clubs.all())
        self.assertTrue(self.book_club.is_admin(profile))
        self.assertFalse(self.book_club.is_founder(profile))
        self.assertFalse(self.book_club.is_regular(profile))
        
    def test_book_club_founder_member(self):
        profile = models.Profile.objects.create(
            user=get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123'))
        models.BookClubMember.objects.create(
            role=models.Role.objects.get(role=models.Role.FOUNDER),
            book_club=self.book_club,
            profile=profile,
        )
        self.assertIn(profile, self.book_club.members.all())
        self.assertIn(self.book_club, profile.book_clubs.all())
        self.assertTrue(self.book_club.is_founder(profile))
        self.assertFalse(self.book_club.is_admin(profile))
        self.assertFalse(self.book_club.is_regular(profile))
        
class BookDiscussionTests(TestCase):
    
    def setUp(self):
        super().setUp()
        self.profile = models.Profile.objects.create(
                user=get_user_model().objects.create_user(
                    username='test', email='testuser@email.com',
                    password='testpass123'
                )
            )
        self.book_discussion = models.BookDiscussion.objects.create(
            question="Is Kino's only dream is to see his community rise in the socio-economic ladder?",
            book=models.Book.objects.create(
                isbn='1234567890',
                title='The Pearl',
                author='John Steinbeck',
                description = 'test description'
            ),
            starter=self.profile
        )
        
    def test_details(self):
        self.assertTrue(
            models.BookDiscussion.objects.filter(book__isbn='1234567890').exists()
        )
        self.assertEqual(
            models.Book.objects.get(isbn='1234567890').discussions.first().starter,
            self.profile
        )
        self.assertEqual(
            self.profile.book_discussions.first().book.author, 'John Steinbeck'
        )
        
    def test_comment_details(self):
        profile = models.Profile.objects.create(
                user=get_user_model().objects.create_user(
                    username='johndoe', email='jondoe@email.com',
                    password='testpass123'
                )
            )
        comment = models.BookDiscussionComment.objects.create(
            discussion=self.book_discussion,
            commentor=profile,
            body='I believe so since he mainly wanted the education of his son.'
        )
        self.assertEqual(
            profile.book_discussions_comments.first().body,
            'I believe so since he mainly wanted the education of his son.'
        )
        self.assertEqual(
            self.book_discussion.comments.first(), comment
        )
        
    def test_comment_replies(self):
        comment = models.BookDiscussionComment.objects.create(
            discussion=self.book_discussion,
            commentor=models.Profile.objects.create(
                user=get_user_model().objects.create_user(
                    username='johndoe', email='jondoe@email.com',
                    password='testpass123'
                )
            ),
            body='lorem ipsum dolor sit amet.',
        )
        models.BookCommentReply.objects.create(
            comment=comment,
            replier=self.profile,
            body='i like your content',
        )
        self.assertEqual(
            comment.replies.first().body, 
            'i like your content',
        )
        self.assertEqual(
            self.profile.book_comments_replies.first().body,
            'i like your content'
        )
        
class ThreadDiscussionTests(TestCase):
    
    def setUp(self):
        super().setUp()
        self.profile = models.Profile.objects.create(
                user=get_user_model().objects.create_user(
                    username='test', email='testuser@email.com',
                    password='testpass123'
                )
            )
        self.book_club = models.BookClub.objects.create(
            name='Test Book Club',
            location='Nairobi',
            description='lorem ipsum dolor sit amet',
        )
        self.thread = models.BookClubThread.objects.create(
            book_club=self.book_club,
            title='General',
        )
        self.thread_discussion = models.ThreadDiscussion.objects.create(
            thread=self.thread,
            question="Test Q/A",
            starter=models.BookClubMember.objects.create(
                book_club=self.book_club,
                profile=self.profile,
                role=models.Role.objects.create(role=models.Role.REGULAR)
            )
        )
        
    def test_details(self):
        self.assertTrue(
            models.BookClubThread.objects.filter(title='General').exists()
        )
        self.assertIn(self.thread, self.book_club.threads.all())
        self.assertEqual(
            self.book_club.threads.first().discussions.first().question, 
            "Test Q/A"
        )
        
    def test_comment_details(self):
        comment = models.ThreadDiscussionComment.objects.create(
            discussion=self.thread_discussion,
            commentor=self.profile,
            body='test qomment'
        )
        self.assertEqual(
            self.profile.thread_discussions_comments.first().body,
            'test qomment'
        )
        self.assertEqual(
            self.thread_discussion.comments.first(), comment
        )
        
    def test_comment_replies(self):
        comment = models.ThreadDiscussionComment.objects.create(
            discussion=self.thread_discussion,
            commentor=self.profile,
            body='lorem ipsum dolor sit amet.',
        )
        models.ThreadCommentReply.objects.create(
            comment=comment,
            replier=self.profile,
            body='i like your content',
        )
        self.assertEqual(
            comment.replies.first().body, 
            'i like your content',
        )
        self.assertEqual(
            self.profile.thread_comments_replies.first().body,
            'i like your content'
        )