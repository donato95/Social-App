from flask import redirect, request, render_template, session, url_for, g
from flask.blueprints import Blueprint
from flask_login import current_user
from flask_babelplus import lazy_gettext as _l


pages = Blueprint('pages', __name__)

@pages.route('/home', methods=['GET', 'POST'])
def home():
    lang = session['lang']
    title = _l('Bees')
    return render_template('/pages/home.html', lang=lang, title=title)

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

@pages.route('/terms', methods=['GET', 'POST'])
def terms():
    lang = session['lang']
    title = _l('Terms and Privacy')
    return render_template('pages/terms.html', lang=lang, title=title)