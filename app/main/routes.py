from flask import render_template, request, redirect, g, session
from flask.blueprints import Blueprint
from flask_login import current_user, login_required
from flask_babelplus import lazy_gettext as _l, get_locale

from app import db_session
from app.posts.forms import PostForm
from app.models import Posts

main = Blueprint('main', __name__)

@main.before_app_request
def before_request():
    g.locale = str(get_locale())

@main.route('/language/<string:name>', methods=['GET'])
def lang(name):
    if current_user.is_authenticated:
        current_user.local_lang = name
        db_session.commit()
        session['lang'] = name
    if not current_user.is_authenticated:
        session['lang'] = name
    return redirect(request.referrer)

@main.route('/', methods=['GET', 'POST'])
@main.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    lang = session['lang']
    title = _l('Home')
    post_form = PostForm()
    posts = Posts.query.filter_by(author=current_user).all()
    if request.method == 'POST' and post_form.validate_on_submit():
        post = Posts(content=post_form.post.data, is_public=True, user_id=current_user.id)
        db_session.add(post)
        db_session.commit()
        return redirect(request.referrer)
    return render_template(
                            'main/home.html', lang=lang, title=title, post_form=post_form,
                            posts=posts)