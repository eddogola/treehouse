from django.test import TestCase
from django.urls import reverse

class AuthenticationTestCase(TestCase):
    
    def test_signup_form_has_first_name_last_name(self):
        resp = self.client.get(reverse('account_signup'))
        self.assertContains(resp, 'First name')
        self.assertContains(resp, 'Last name')
        
    def test_signup_form_works(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@email.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        resp = self.client.post(reverse('account_signup'), data)
        self.assertRedirects(resp, reverse('home'))
        