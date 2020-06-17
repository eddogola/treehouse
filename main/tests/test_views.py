from django.test import TestCase
from django.urls import reverse

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
        resp = self.client.get(reverse('book_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Misery')
        self.assertContains(resp, 'Stephen King')

    
        