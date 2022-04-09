from flask import Flask, request, current_app, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_babelplus import Babel
from flask_cors import CORS
from flask_socketio import SocketIO
from config import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
babel = Babel()
cors = CORS()
socketio = SocketIO()
db_session = db.session

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    babel.init_app(app)
    cors.init_app(app, resources={r"/chat/*": {"origins": "*"}})
    socketio.init_app(app)

    from app.pages import pages
    from app.main import main
    app.register_blueprint(pages)
    app.register_blueprint(main)

    return app


@babel.localeselector
def get_locale():
    if current_user.is_authenticated:
        return current_user.local_lang
    elif current_user.is_anonymous:
        session['lang'] = current_app.config['BABEL_DEFAULT_LOCALE']
        return session['lang']
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])
