import os
from flask import Flask, request, current_app, session, g
from flask_login import LoginManager, current_user
from flask_babelplus import Babel, lazy_gettext as _l
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_cors import CORS
from flask_mail import Mail
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from config import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
babel = Babel()
cors = CORS()
moment = Moment()
mail = Mail()
csrf = CSRFProtect()
socketio = SocketIO()
db_session = db.session

login_manager.login_view = 'auth.login'
login_manager.login_message = None
# login_manager.refresh_view = 'auth.refresh'
# login_manager.needs_refresh_message = _l('You have to re enter yout credintials')
# login_manager.needs_refresh_message_category = 'info'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config.update(dict(
        MAIL_SERVER = 'smtp.googlemail.com',
        MAIL_PORT = 587,
        MAIL_USE_TLS = True,
        MAIL_USERNAME = os.environ.get('MAIL_USERNAME'),
        MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ))

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    babel.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "http://127.0.0.1:5000"}})
    socketio.init_app(app)

    from app.main import main
    app.register_blueprint(main)

    from app.pages import pages
    app.register_blueprint(pages, url_prefix='/pages')

    from app.auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

    from app.user import user
    app.register_blueprint(user, url_prefix='/user')

    from app.posts import posts
    app.register_blueprint(posts, url_prefix='/posts')

    from app.api import api
    app.register_blueprint(api, url_prefix='/api/v1')

    from app.admin import admin
    app.register_blueprint(admin, url_prefix='/admin')

    from app.errors.handlers import (
                                forbidden_access, not_found_error,
                                unautherized_access, bad_request,
                                internerl_error, method_not_allowed)

    app.register_error_handler(400, bad_request)
    app.register_error_handler(401, unautherized_access)
    app.register_error_handler(403, forbidden_access)
    app.register_error_handler(404, not_found_error)
    app.register_error_handler(405, method_not_allowed)
    app.register_error_handler(500, internerl_error)

    return app

@babel.localeselector
def get_locale():
    if current_user.is_authenticated:
        session['lang'] = current_user.local_lang
        return session['lang']
    if 'lang' in session.keys():
        return session['lang']
    if not 'lang' in session.keys():
        session['lang'] = request.accept_languages.best_match(current_app.config['LANGUAGES'])
        return session['lang']
