"""
    Application configurations file
"""

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret key here'
    TESTING = False
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SSL_REDIRECT = False
    ADMIN_MAIL = os.environ.get('ADMIN_MAIL')
    BABEL_DEFAULT_LOCALE = 'en'
    LANGUAGES = ['en', 'ar', 'fr']
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(basedir + 'app/translations')
    POSTS_PER_PAGE = 10
    USER_PER_PAGE = 20
    MESSAGES_PER_PAGE = 15
    NOTIFICATIONS_PER_PAGE = 30
    MAX_IMG_SIZE = 1024 * 1024 * 1024
    ALLOWED_IMG_EXTENTIONS = ['.jpg', '.jpeg', '.png']
    AVATAR_ROUTE = 'avatar'

    @staticmethod
    def init_app(cls, app):
        pass


class Development(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') \
        or 'sqlite:///' + os.path.join(basedir, 'dev.sqlite')


class Testing(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') \
        or 'sqlite:///' + os.path.join(basedir, 'testing.sqlite')


class Production(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') \
        or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


config = {
    'dev': Development,
    'testing': Testing,
    'production': Production,

    'default': Development
}