from django.test import TestCase
from django.urls import reverse

class MainTests(TestCase):
    
    def test_home_page_status_code(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)