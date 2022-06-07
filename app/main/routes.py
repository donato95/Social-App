from flask import current_app, jsonify, render_template, request, redirect, g, session
from flask.blueprints import Blueprint
from flask_login import current_user, login_required
from flask_babelplus import lazy_gettext as _l, get_locale

from app import db_session, login_manager
from app.posts.forms import PostForm
from app.models import Posts, User, Roles, Notifications

main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

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
@login_required
def home():
    lang = session['lang']
    title = _l('Home')
    post_form = PostForm()
    page = request.args.get('page', 1, type=int)
    query = current_user.followed_posts.filter(Posts.is_public==True).order_by(Posts.published_date.desc())
    pagination = query.paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    if request.method == 'POST' and post_form.validate_on_submit():
        post = Posts(content=post_form.post.data, is_public=True, user_id=current_user.id)
        db_session.add(post)
        db_session.commit()
        return redirect(request.referrer)
    to_follow = User.query.filter(User.id != current_user.id).limit(3)
    return render_template('main/home.html', lang=lang, title=title, to_follow=to_follow, 
                            post_form=post_form, posts=posts, pagination=pagination)

@main.route('/notifications/<action>', methods=['GET'])
@login_required
def notifications(action):
    lang = session['lang']
    title = _l('Notifications')
    notis = None
    page = request.args.get('page', 1, type=int)
    if action == 'json':
            count = current_user.new_notifications()
            return jsonify({"count": count })
    if action == 'messages':
        count = current_user.new_messages()
        return jsonify({"count": count})
    if action == 'all':
        query = Notifications.query.filter_by(user=current_user)
        unseen = query.filter_by(seen=False).all()
        for noti in unseen:
            noti.seen = True
            db_session.commit()
        pagination = query.order_by(Notifications.action_date.desc()).paginate(page, per_page=current_app.config['NOTIFICATIONS_PER_PAGE'], error_out=False)
        notis = pagination.items
    to_follow = User.query.filter(User.id != current_user.id).limit(3)
    return render_template('main/notifications.html', lang=lang, title=title, 
                            notis=notis, pagination=pagination, to_follow=to_follow)
