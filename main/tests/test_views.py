from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from main import models

class MainTests(TestCase):
    
    def test_home_page_status_code(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)

    def test_book_list_view(self):
        models.Book.objects.create(
            isbn='123456789',
            title='Misery',
            author='Stephen King',
            description='test book description',
        )
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
        book = models.Book.objects.create(
            isbn='123456789',
            title='Misery',
            author='Stephen King',
            description='test book description',
        )
        review = models.Review.objects.create(
            book=book,
            reviewer=models.Profile.objects.create(
            user=get_user_model().objects.create_user(
                username='testuser',
                email='testuser@email.com',
                password='testpass123')),
            body='very scrumptious',
        )
        resp = self.client.get(reverse('book_detail', args=[book.id]))
        self.assertEqual(resp.status_code, 200)        
        self.assertContains(resp, '123456789')
        self.assertContains(resp, 'test book description')
        self.assertContains(resp, 'very scrumptious')

    def test_review_detail(self):
        profile = models.Profile.objects.create(
                    user=get_user_model().objects.create_user(
                    username='testuser',
                    email='testuser@email.com',
                    password='testpass123'))
        book = models.Book.objects.create(
            isbn='123456789',
            title='Misery',
            author='Stephen King',
            description='test book description',
        )
        review = models.Review.objects.create(
            book=book,
            reviewer=profile,
            body='very scrumptious',
        )
        comment = models.ReviewComment.objects.create(
            review=review,
            commentor=profile,
            body = 'i can really write long lol'
        )
        resp = self.client.get(reverse('review_detail', args=[review.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'i can really write long lol')
