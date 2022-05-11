from flask import current_app, request, redirect, session, render_template, abort, flash, url_for
from flask.blueprints import Blueprint
from flask_login import current_user, login_required
from flask_babelplus import lazy_gettext as _l, get_locale
from sqlalchemy.orm import aliased

from app import db_session
from app.models import (
    User, Message, Posts, PostRepost, 
    PostLikes, PostBookmark, Follows, 
    MessagesReplies, Notifications)
from app.user.forms import ChatForm, PostForm

user = Blueprint('user', __name__)

@user.route('/account/<int:id>', methods=['GET', 'POST'])
@login_required
def account(id):
    lang = session['lang']
    user = User.query.get_or_404(id)
    title = user.firstname + ' ' + user.lastname
    page = request.args.get('page', 1, type=int)
    query = Posts.query.filter_by(author=user).order_by(Posts.published_date.desc())
    pagination = query.paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    msg = _l('There\'s no activites yet')
    return render_template('user/account.html', lang=lang, title=title, user=user, msg=msg, posts=posts)

@user.route('/account/<int:id>/<string:action>', methods=['GET', 'POST'])
@login_required
def action(id, action):
    user = User.query.get_or_404(id)
    action = action
    if action == 'follow':
        current_user.follow(user)
        db_session.commit()
        user.add_notifications(name='new_follower', user=current_user)
        db_session.commit()
        return redirect(request.referrer)
    if action == 'unfollow':
        current_user.unfollow(user)
        db_session.commit()
        return redirect(request.referrer)
    if action == 'block':
        pass
    return render_template('user/account.html', id=id, action=action)

@user.route('/<string:username>/<string:type>', methods=['GET', 'POST'])
@login_required
def contacts(username, type):
    lang = session['lang']
    Follows = False
    Followers = False
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    if type == 'follows':
        title = _l('Follows')
        query = user.followed
        Follows = True
    if type == 'followers':
        title = _l('Followers')
        query = user.followers
        Followers = True
    pagination = query.paginate(
        page, per_page=current_app.config['USER_PER_PAGE'], error_out=False
    )
    contacts = pagination.items
    return render_template(
                            'user/contacts.html', lang=lang, title=title, 
                            contacts=contacts, user=user, Follows=Follows,
                            Followers=Followers)

@user.route('/<int:id>/activities/<string:action>', methods=['GET', 'POST'])
@login_required
def activities(id, action):
    lang = session['lang']
    title = _l(action.capitalize())
    msg = _l('There\'s no ' + action + ' yet')
    user = User.query.filter_by(id=id).first_or_404()
    page = request.args.get('page', 1, type=int)
    if action == 'posts':
        query = Posts.query.filter_by(author=user).order_by(Posts.published_date.desc())
    if action == 'bookmarks':
        query = Posts.query.filter(Posts.bookmarked, PostBookmark.user_id==id)\
            .order_by(PostBookmark.timestamp.desc())
    if action == 'likes':
        query = Posts.query.filter(Posts.likes, PostLikes.user_id==id)\
            .order_by(PostLikes.timestamp.desc())
    if action == 'reposts':
        query = Posts.query.filter(Posts.reposts, PostRepost.user_id==id)\
            .order_by(PostRepost.timestamp.desc())
    pagination = query.paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('user/account.html', lang=lang, title=title, user=user, msg=msg, posts=posts)

@user.route('/<int:id>/about', methods=['GET'])
@login_required
def about(id):
    lang = session['lang']
    title = _l('About')
    user = User.query.get_or_404(id)
    return render_template('user/about.html', lang=lang, title=title, user=user)

@user.route('/messages')
@login_required
def messages():
    lang = session['lang']
    title = _l('Messages')
    page = request.args.get('page', 1, type=int)
    query = current_user.messages_received.filter_by(recipient=current_user)
    pagination = query.order_by(Message.timestamp.asc()).paginate(
        page, per_page=current_app.config['MESSAGES_PER_PAGE'], error_out=False)
    messages = pagination.items
    return render_template('user/messages.html', lang=lang, title=title, messages=messages)

@user.route('/contact/<string:username>', methods=['GET', 'POST'])
@login_required
def send_message(username):
    user = User.query.filter_by(username=username).first_or_404()
    lang = session['lang']
    title_str = f'Contact {user.username}'
    title = _l(title_str)
    form = ChatForm()
    sent = current_user.messages_sent\
        .order_by(Message.timestamp.asc())
    if request.method == 'POST' and form.validate_on_submit():
        m = Message(author=current_user, recipient=user, body=form.text.data)
        db_session.add(m)
        db_session.commit()
        flash(_l('Message sent'), 'success')
        return redirect(request.referrer)
    return render_template('user/chat.html', lang=lang, title=title, user=user, form=form, msgs=sent)

