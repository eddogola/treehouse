from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
import datetime

from main import models

class MainTests(TestCase):

    def setUp(self):
        super().setUp()
        self.profile = models.Profile.objects.create(
                    user=get_user_model().objects.create_user(
                    username='testuser',
                    email='testuser@email.com',
                    password='testpass123'))
        self.book = models.Book.objects.create(
            isbn='123456789',
            title='Misery',
            author='Stephen King',
            description='test book description')
    
    def test_home_page_status_code(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)

    def test_book_list_view(self):
        models.Book.objects.create(
            isbn='453456789',
            title='Ultralearning',
            author='Scott H.Young',
            description='test book description',
        )
        resp = self.client.get(reverse('book_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Misery')
        self.assertContains(resp, 'Stephen King')
        self.assertContains(resp, 'Ultralearning')
        self.assertContains(resp, 'Scott H.Young')

    def test_book_detail(self):
        review = models.Review.objects.create(
            book=self.book,
            reviewer=self.profile,
            body='very scrumptious')
        resp = self.client.get(reverse('book_detail', args=[self.book.id]))

        self.assertEqual(resp.status_code, 200)        
        self.assertContains(resp, '123456789')
        self.assertContains(resp, 'test book description')
        self.assertContains(resp, 'very scrumptious')

    def test_review_list(self):
        review = models.Review.objects.create(
            book=self.book,
            reviewer=self.profile,
            body='very scrumptious')
        profile1 = models.Profile.objects.create(
                    user=get_user_model().objects.create_user(
                    username='johndoe',
                    email='johndoe@email.com',
                    password='testpass123'))
        review1 = models.Review.objects.create(
            book=self.book,
            reviewer=profile1,
            body='breathtaking')
        resp = self.client.get(reverse('review_list'))

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'breathtaking')
        self.assertContains(resp, 'very scrumptious')

    def test_review_detail(self):
        review = models.Review.objects.create(
            book=self.book,
            reviewer=self.profile,
            body='very scrumptious')
        comment = models.ReviewComment.objects.create(
            review=review,
            commentor=self.profile,
            body = 'i can really write long lol')
        resp = self.client.get(reverse('review_detail', args=[review.id]))

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'i can really write long lol')

    def test_book_discussion_list(self):
        models.BookDiscussion.objects.create(
            question='How many problems ya got?',
            book=self.book,
            starter=self.profile)
        resp = self.client.get(reverse('book_discussion_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.book.title)
        self.assertContains(resp, 'How many problems ya got?')
        self.assertContains(resp, self.profile.user.username)

    def test_book_discussion_detail(self):
        discussion = models.BookDiscussion.objects.create(
            question='How many problems ya got?',
            book=self.book,
            starter=self.profile)
        profile = models.Profile.objects.create(
            user=get_user_model().objects.create_user(
                username='janedoe',
                password='janedoe@email.com'))
        comment = models.BookDiscussionComment.objects.create(
            discussion=discussion,
            commentor=profile,
            body='A lot lol!')
        models.BookCommentReply.objects.create(
            comment=comment,
            replier=self.profile,
            body='lmao')
        resp = self.client.get(reverse('book_discussion_detail', kwargs={'pk' : discussion.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'How many problems ya got?')
        self.assertContains(resp, 'A lot lol!')
        self.assertContains(resp, 'lmao')

class BookClubTests(TestCase):
    
    def setUp(self):
        super().setUp()
        self.book_club = models.BookClub.objects.create(
            name='Oprah Winfrey Book Club',
            location='Kilimani',
            description = 'nano')
        self.book = models.Book.objects.create(
                isbn='1234238189',
                title='The cathedral and the bazaar',
                author='Plato',
                description='antique')
        self.profile = models.Profile.objects.create(
                    user=get_user_model().objects.create_user(
                    username='testuser',
                    email='testuser@email.com',
                    password='testpass123'))

    def test_book_club_list(self):
        models.BookClub.objects.create(
            name='Ogola Book Club',
            location='Kitengela',
            description = 'nona')
        resp = self.client.get(reverse('book_club_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Oprah Winfrey Book Club')
        self.assertContains(resp, 'Ogola Book Club')

    def test_book_club_detail(self):
        read = models.BookClubRead.objects.create(
            book=self.book,
            book_club = self.book_club,
            start_date = datetime.datetime.today(),
            read_duration = 16)
        resp = self.client.get(reverse('book_club_detail', args=[self.book_club.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'nano')
        #current read displayed
        self.assertContains(resp, 'The cathedral and the bazaar')

    def test_book_club_threads_discussions(self):
        thread = models.BookClubThread.objects.create(
            book_club=self.book_club,
            title='General')
        discussion = models.ThreadDiscussion.objects.create(
            thread=thread,
            question='Introduced yourself yet?',
            starter=models.BookClubMember.objects.create(
                book_club=self.book_club,
                profile=self.profile,
                role=models.Role.objects.create(role=models.Role.REGULAR)))
        resp = self.client.get(reverse('book_club_threads', args=[self.book_club.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'General')
        self.assertContains(resp, 'Introduced yourself yet?')

    def test_book_club_reads(self):
        read = models.BookClubRead.objects.create(
            book_club=self.book_club,
            book=self.book,
            start_date=datetime.datetime.today(),
            read_duration=12)
        resp = self.client.get(reverse('book_club_reads', args=[self.book_club.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.book.title)

    def test_book_club_members(self):
        member = models.BookClubMember.objects.create(
            book_club=self.book_club,
            profile=self.profile,
            role=models.Role.objects.create(role=models.Role.REGULAR))
        resp = self.client.get(reverse('book_club_members', args=[self.book_club.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.profile.user.username)
        self.assertContains(resp, 'Regular')