from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_babel import Babel
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
session = db.session

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

    with app.app_context():
        @babel.localeselector
        def get_local():
            # if current_user.is_authenticated:
            #     return current_user.local
            return request.accept_languages.best_match(app.config['LANGUAGES'])
        
        from app.pages import pages
        from app.main import main
        app.register_blueprint(pages)
        app.register_blueprint(main)

        return app