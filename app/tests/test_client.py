import json
import unittest
from datetime import datetime
from flask import current_app

from app import db, db_session, create_app
from app.models import User

class ClientTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
    
    def tearDown(self) -> None:
        db_session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_auth(self):
        response = self.client.get('/auth/register')
        self.assertTrue(response.status_code, 200)
        response = self.client.post('/auth/register', data={
            'username': 'demo_test',
            'password': 'demo1234',
            'firstname': 'Demo A.',
            'lastname': 'Test',
            'email': 'demo_test@mail.com',
        }, follow_redirects=True)
        self.assertTrue(response.status_code, 302)

        response = self.client.get('/auth/login')
        self.assertTrue(response.status_code, 200)
        response = self.client.post('/auth/login', data={
            'username': 'demo_test',
            'password': 'demo1234'
        }, follow_redirects=True)
        self.assertTrue(response.status_code, 302)

        response = self.client.get('/auth/settings')
        self.assertTrue(response.status_code, 200)
        response = self.client.post('/auth/settings', data={
            'firstname': 'Demo',
            'lastname': 'Test',
            'username': 'demo_test1234',
            'job': 'Test Pro',
            'city': 'Test City',
            'gender': True,
            'birth_date': datetime.today(),
            'bio': 'Some test bio my test guy'
        })
        self.assertTrue(response.status_code, 302)

        response = self.client.get('/auth/settings/email')
        self.assertTrue(response.status_code, 200)
        response = self.client.post('/auth/settings/email', data={
            'email': 'new_demo@email.com'
        })
        self.assertTrue(response.status_code, 302)

        response = self.client.get('/auth/settings/password')
        self.assertTrue(response.status_code, 200)
        response = self.client.post('/auth/settings/password', data={
            'password': 'new_demo1234'
        })
        self.assertTrue(response.status_code, 302)
    
    def test_main(self):        
        response = self.client.get('/')
        self.assertTrue(response.status_code, 200)

        response = self.client.get('/notifications/all')
        self.assertTrue(response.status_code, 200)
        self.assertTrue(response.get_data(as_text=True))

        response = self.client.get('/notifications/json')
        self.assertTrue(response.status_code, 200)
        self.assertTrue(response.get_data(as_text=True))

        response = self.client.get('/notifications/messages')
        self.assertTrue(response.status_code, 200)
        self.assertTrue(response.get_data(as_text=True))

    def test_pages(self):
        response = self.client.get('/')
        self.assertTrue(response.status_code, 200)

        response = self.client.get('/pages/home')
        self.assertTrue(response.status_code, 200)

        response = self.client.get('/pages/contact')
        self.assertTrue(response.status_code, 200)

        response = self.client.get('/pages/terms')
        self.assertTrue(response.status_code, 200)

        response = self.client.get('/pages/about')
        self.assertTrue(response.status_code, 200)

    def test_posts(self):
        pass
