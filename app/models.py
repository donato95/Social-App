from datetime import datetime
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from flask_bcrypt import generate_password_hash

from app import db, login_manager


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

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
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

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
    
    def __repr__(self):
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