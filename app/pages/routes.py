from flask import redirect, request, render_template, session, url_for
from flask.blueprints import Blueprint
from flask_login import current_user
from flask_babelplus import lazy_gettext as _l


pages = Blueprint('pages', __name__)

# @pages.route('/', methods=['GET'])
# @pages.route('/home', methods=['GET'])
# def home():
#     # title = _l('Home')
#     # lang = ''
#     # if current_user.is_authenticated:
#     #     lang = current_user.local_lang
#     # if current_user.is_anonymous:
#     #     lang = session['lang']
#     # print(f'languages is - - [{lang}]')
#     # print(f'All sessions keys -- {session.values()}')
#     # return render_template('auth/home.html', lang=lang, title=title)
#     return redirect(url_for('auth.login'))


@pages.route('/about', methods=['GET'])
def about():
    title = _l('About Us')
    lang = session['lang']
    return render_template('pages/about.html', lang=lang, title=title)


@pages.route('/contact', methods=['GET', 'POST'])
def contact():
    title = _l('Contact Us')
    lang = session['lang']
    return render_template('pages/contact.html', lang=lang, title=title)