import unittest
from flask import current_app

from app import db, db_session, create_app
from app.models import User, Roles, Posts

def create_user(username, email):
    u = User(username=username, firstname='Test', lastname='D. Test', email=email, password='1234')
    db_session.add(u)
    db_session.commit()
    return u

def create_post(userid):
    p = Posts(content='This is test post', user_id=userid)
    db_session.add(p)
    db_session.commit()
    return p

class UserModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self) -> None:
        db_session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_self_follow_and_chat(self):
        u = create_user('test', 'test@mail.com')
        self.assertIsNone(u.add_self_follows())
        self.assertTrue(u.is_following(u))
        self.assertIsNone(u.add_chat())
        self.assertTrue(u.has_chat())

    def test_new_messages_and_notifications(self):
        u = create_user('test', 'test@mail.com')
        self.assertIsNotNone(u.new_messages())
        self.assertIsNotNone(u.new_notifications())

    def test_follow_activites(self):
        u = create_user('test', 'test@mail.com')
        u2 = create_user('test2', 'test2@mail.com')
        self.assertFalse(u.is_following(u2))
        self.assertFalse(u2.is_followed_by(u))
        u.follow(u2)
        db_session.commit()
        self.assertTrue(u.is_following(u2))
        self.assertFalse(u.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u))
    
    def test_post_activites(self):
        u = create_user('test', 'test@mail.com')
        u2 = create_user('test2', 'test2@mail.com')
        p = create_post(u.id)
        u2.like(p)
        db_session.commit()
        self.assertTrue(u2.has_liked(p))
        u2.book(p)
        db_session.commit()
        self.assertTrue(u2.has_booked(p))
        u2.repost(p)
        db_session.commit()
        self.assertTrue(u2.has_repost(p))
        u2.unbook(p)
        db_session.commit()
        self.assertFalse(u2.has_booked(p))
        u2.unrepost(p)
        db_session.commit()
        self.assertFalse(u2.has_repost(p))
        u2.unliked(p)
        db_session.commit()
        self.assertFalse(u2.has_liked(p))

    def test_user_roles(self):
        u = create_user('test', 'test@mail.com')
        Roles.add_roles()
        admin = Roles.query.filter_by(name='ADMIN').first()
        moderator = Roles.query.filter_by(name='MODERATOR').first()
        user = Roles.query.filter_by(name='USER').first()
        self.assertTrue(admin.has_perm(4))
        self.assertTrue(moderator.has_perm(2))
        self.assertTrue(user.has_perm(1))
        u.role = user
        db_session.commit()
        self.assertTrue(u.role.name == 'USER')
        self.assertFalse(u.role.name == 'MODERATOR')
        self.assertFalse(u.role.name == 'ADMIN')
        u.role = admin
        db_session.commit()
        self.assertTrue(u.role.name == 'ADMIN')
        u.role = moderator
        db_session.commit()
        self.assertTrue(u.role.name == 'MODERATOR')
