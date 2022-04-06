from flask import request, render_template
from flask.blueprints import Blueprint


pages = Blueprint('pages', __name__)


@pages.route('/', methods=['GET'])
@pages.route('/home', methods=['GET'])
def home():
    return render_template('pages/home.html')


@pages.route('/about', methods=['GET'])
def about():
    return render_template('pages/about.html')


@pages.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('pages/contact.html')