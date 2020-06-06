from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from celery.contrib.testing.worker import start_worker
from treehouse.celery import app

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
        
    def test_email_send_done_by_celery_worker(self):
        
        #create test user
        get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123',
        )
        
        #integration test
        data = {
            'email': 'testuser@email.com'
        }
        resp = self.client.post(reverse('account_reset_password'), data)
        self.assertGreaterEqual(len(mail.outbox), 1)