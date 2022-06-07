import unittest
from flask import current_app
from app import create_app, db, db_session

class AppTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self) -> None:
        db_session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_app_exists(self):
        self.assertTrue(current_app is not None)
    
    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
