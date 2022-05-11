from time import time
import json
from datetime import datetime
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin
from flask_bcrypt import generate_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from app import db, login_manager, db_session


class Permessions:
    USER = 1
    MODERATOR = 2
    ADMIN = 4


class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    permession = db.Column(db.Integer, nullable=False)
    default = db.Column(db.Boolean, default=False, index=True)
    users = db.relationship('User', backref='role', lazy=True)

    @staticmethod
    def add_roles():
        roles = {
            'USER': Permessions.USER,
            'MODERATOR': Permessions.MODERATOR,
            'ADMIN': Permessions.ADMIN
        }
        default = roles['USER']
        for r in roles:
            role = Roles.query.filter_by(name=r).first()
            if not role:
                role = Roles(name=r)
            role.clear_perm()
            for perm in roles[r]:
                role.add_perm(perm)
            role.default = (role.name == default)
            db.session.add(role)
        db.session.commit()

    def has_perm(self, perm):
        if self.permession == perm: return True

    def clear_perm(self):
        self.permession = 0
    
    def add_perm(self, perm):
        if not self.has_perm(perm):
            self.permession = perm

    def __repr__(self):
        return f'<Role {self.name} {self.permession}>'


class Follows(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    firstname = db.Column(db.String(25), nullable=False)
    lastname = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    picture = db.Column(db.String(80), default='demo.jpg')
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)
    hashed_password = db.Column(db.String(120), nullable=False)
    local_lang = db.Column(db.String(2), default='en')
    job = db.Column(db.String(30))
    bio = db.Column(db.String(250))
    city = db.Column(db.String(25))
    birth_date = db.Column(db.Date, default=datetime.today)
    confirmed = db.Column(db.Boolean, default=False)
    gender = db.Column(db.Boolean, default=None, nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    posts = db.relationship('Posts', backref='author', lazy=True)
    liked = db.relationship('PostLikes', backref='favorites', lazy=True, )
    booked = db.relationship('PostBookmark', backref='booker', lazy=True)
    reposted = db.relationship('PostRepost', backref='reposter', lazy=True)
    comments = db.relationship('Comments', backref='commenter', lazy=True)
    replier = db.relationship('MessagesReplies', backref='replier', lazy=True)
    setter = db.relationship('Notifications',
                            foreign_keys='Notifications.setter_id',
                            backref='creater', lazy='dynamic')
    getter = db.relationship('Notifications',
                            foreign_keys='Notifications.getter_id',
                            backref='user', lazy='dynamic')
    followed = db.relationship('Follows',
                                foreign_keys=[Follows.follower_id],
                                backref=db.backref('follower', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    followers = db.relationship('Follows',
                                foreign_keys=[Follows.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author',
                                    lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient',
                                        lazy='dynamic')
    last_read_time = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.role:
            if self.email == current_app.config['ADMIN_MAIL']:
                self.role = Roles.query.filter_by(name='ADMIN').first()
            else:
                self.role = Roles.query.filter_by(default=True).first()
    
    @property
    def password(self):
        raise AttributeError('Can\'t access property directly')
    
    @password.setter
    def password(self, password):
        self.hashed_password = generate_password_hash(password)
    
    @property
    def followed_posts(self):
        return Posts.query.join(Follows, Follows.followed_id == Posts.user_id)\
            .filter(Follows.follower_id == self.id, Posts.is_public == True)
    
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()
    
    def new_messages(self):
        return Message.query.filter_by(recipient=self).filter(Message.seen == False).count()
    
    def new_notifications(self):
        return Notifications.query.filter_by(user=self).filter(Notifications.seen == False).count()

    def add_notifications(self, name, user, is_message=False, vote=None, post=None):
        n = Notifications(
            name=name, creater=user, user=self, is_message=is_message, 
            post_id=post, vote_id=vote)
        db_session.add(n)

    def is_following(self, user):
        if user is None:
            return False
        return self.followed.filter_by(followed=user).first() is not None
    
    def is_followed_by(self, user):
        if user is None:
            return False
        return self.followers.filter_by(follower=user).first() is not None
    
    def follow(self, user):
        if not self.is_following(user):
            follow = Follows(followed_id=user.id, follower_id=self.id)
            db_session.add(follow)
    
    def unfollow(self, user):
        if self.is_following(user):
            unfollow = Follows.query.filter_by(followed_id=user.id, follower_id=self.id).first()
            db_session.delete(unfollow)

    def has_liked(self, post):
        return PostLikes.query.filter_by(post_id = post.id, user_id = self.id).count() > 0
    
    def like(self, post):
        if not self.has_repost(post):
            like = PostLikes(post_id=post.id, user_id=self.id)
            db_session.add(like)
    
    def unliked(self, post):
        if self.has_liked(post):
            unliked = PostLikes.query.filter_by(post_id=post.id, user_id=self.id).first()
            db_session.delete(unliked)
    
    def has_booked(self, post):
        return PostBookmark.query.filter_by(post_id = post.id, user_id = self.id).count() > 0
    
    def book(self, post):
        if not self.has_booked(post):
            book = PostBookmark(post_id=post.id, user_id=self.id)
            db_session.add(book)
    
    def unbook(self, post):
        if self.has_booked(post):
            unbook = PostBookmark.query.filter_by(post_id=post.id, user_id=self.id).first()
            db_session.delete(unbook)
    
    def has_voted(self, comment):
        return Upvotes.query.filter_by(comment_id=comment.id, user_id=self.id).count() > 0
    
    def upvote(self, comment):
        if not self.has_upvoted(comment):
            vote = Upvotes(comment_id=comment.id, user_id=self.id)
            db_session.add(vote)
    
    def downvote(self, comment):
        if self.has_upvoted(comment):
            vote = Upvotes.query.filter_by(comment_id=comment.id, user_id=self.id).first()
            vote.upvote = True
        else:
            vote = Upvotes(comment_id=comment.id, user_id=self.id, upvote=False)
            db_session.add(vote)
    
    def get_bookmarked(self):
        return Posts.query.filter(Posts.bookmarked == PostBookmark.saved).all()
    
    def has_repost(self, post):
        return PostRepost.query.filter_by(post_id=post.id, user_id=self.id).count() > 0
    
    def repost(self, post):
        if not self.has_repost(post):
            repost = PostRepost(post_id=post.id, user_id=self.id)
            db_session.add(repost)
    
    def unrepost(self, post):
        if self.has_repost(post):
            unrepost = PostRepost.query.filter_by(post_id=post.id, user_id=self.id).first()
            db_session.delete(unrepost)
    
    def to_dict(self, with_email=False) -> dict:
        data = {
            'id': self.id,
            'fullname': self.full_name,
            'username': self.username,
            '_links': {
               'url': url_for('user.account', id=self.id),
                'profile_pic': self.user_image
            }
        }
        if with_email:
            data['email'] = self.email
        return data
    
    def __repr__(self) -> str:
        return f'<User {self.username} {self.email}>'


class AnonymousUser(AnonymousUserMixin):
    def is_admin(self):
        return False
    
    def is_moderator(self):
        return False
    
    def can(self, perm):
        return False

    def is_anonymous(self):
        return True

login_manager.anonymous_user = AnonymousUser


class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    published_date = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    is_public = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    likes = db.relationship('PostLikes', 
                                backref='post_likes', lazy=True,
                                cascade='all, delete, delete-orphan')
    reposts = db.relationship('PostRepost', 
                                backref='reposts', lazy=True,
                                cascade='all, delete, delete-orphan')
    comments = db.relationship('Comments',
                                backref='comment', lazy=True, 
                                cascade='all, delete, delete-orphan')
    bookmarked = db.relationship('PostBookmark', 
                                backref=db.backref('saved', lazy=True),
                                cascade='all, delete, delete-orphan')
    notifications = db.relationship('Notifications', 
                                backref=db.backref('p_notifications', lazy=True),
                                cascade='all, delete, delete-orphan')

    def to_dict(self) -> dict:
        return {
            'content': self.content,
            'publish_date': self.published_date,
            'likes': self.likes,
            'is_public': self.is_public,
            'author_id': self.user_id
        }

    def __init__(self, **kwargs) -> None:
        super(Posts, self).__init__(**kwargs)
    
    def __repr__(self) -> str:
        return f'<Post {self.id}>'


class PostLikes(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, **kwargs) -> None:
        super(PostLikes, self).__init__(**kwargs)
    
    def __repr__(self) -> str:
        return f'<PostLike {self.id}>'


class PostBookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, **kwargs) -> None:
        super(PostBookmark, self).__init__(**kwargs)
    
    def __repr__(self) -> str:
        return f'<Bookmark {self.id}>'


class PostRepost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, **kwargs) -> None:
        super(PostRepost, self).__init__(**kwargs)
    
    def __repr__(self) -> str:
        return f'<Repost {self.id}>'


class Comments(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    published_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    upvotes = db.relationship('Upvotes', backref='votes', lazy=True)

    def to_dict(self) -> dict:
        return {
            'content': self.content,
            'publish_date': self.published_date,
            'upvote': self.upvote,
            'downvote': self.downvote,
            'author_id': self.user_id
        }

    def __init__(self, **kwargs) -> None:
        super(Comments, self).__init__(**kwargs)
    
    def __repr__(self) -> str:
        return f'<Comment {self.id}>'


class Upvotes(db.Model):
    __tablename__ = 'upvotes'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    upvote = db.Column(db.Boolean, default=True)
    notifications = db.relationship('Notifications', backref='v_notifications', lazy=True)

    def __init__(self, **kwargs) -> None:
        super(Upvotes, self).__init__(**kwargs)
    
    def __repr__(self) -> str:
        return f'<Upvotes {self.user_id}>'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.Text)
    seen = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    replie = db.relationship('MessagesReplies', backref='message_replie', lazy=True)

    def __init__(self, **kwargs) -> None:
        super(Message, self).__init__(**kwargs)

    def __repr__(self) -> str:
        return f'<Message {self.id}>'


class MessagesReplies(db.Model):
    __tablename__ = 'messages_replies'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    seen = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, **kwargs) -> None:
        super(MessagesReplies, self).__init__(**kwargs)

    def __repr__(self) -> str:
        return f'<MessagesReplies {self.id}>'


class Notifications(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    seen = db.Column(db.Boolean, default=False)
    is_message = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.Float, default=time, index=True)
    action_date = db.Column(db.DateTime, default=datetime.utcnow)
    setter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    getter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    vote_id = db.Column(db.Integer, db.ForeignKey('upvotes.id'))

    def __init__(self, **kwargs) -> None:
        super(Notifications, self).__init__(**kwargs)

    def __repr__(self) -> str:
        return f'<Notifications {self.id}>'

