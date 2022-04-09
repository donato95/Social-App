from flask import request, render_template, session
from flask.blueprints import Blueprint
from flask_login import current_user


pages = Blueprint('pages', __name__)


@pages.route('/', methods=['GET'])
@pages.route('/home', methods=['GET'])
def home():
    lang = ''
    if current_user.is_authenticated:
        lang = current_user.local_lang
    if current_user.is_anonymous:
        lang = session['lang']
    return render_template('pages/home.html', lang=lang)


@pages.route('/about', methods=['GET'])
def about():
    return render_template('pages/about.html')


@pages.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('pages/contact.html')