from flask import ( 
    current_app, jsonify, request, redirect, session, g,
    render_template, abort, flash, url_for, json)
from flask.blueprints import Blueprint
from flask_login import current_user, login_required
from flask_babelplus import lazy_gettext as _l, get_locale
from sqlalchemy.exc import IntegrityError

from app import db_session, socketio
from app.errors.handlers import json_response
from app.models import (
    User, Posts, PostRepost, PostLikes, 
    PostBookmark, Follows, Notifications, Messages, Chat)
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
    to_follow = User.query.order_by(User.joined_date.desc()).limit(3)
    return render_template('user/account.html', lang=lang, title=title, user=user,
                            msg=msg, posts=posts, to_follow=to_follow)

@user.route('/account/<int:id>/<string:action>', methods=['GET', 'POST'])
@login_required
def action(id, action):
    user = User.query.get_or_404(id)
    action = action
    if action == 'follow':
        current_user.follow(user)
        db_session.commit()
        user.add_notifications(name='follower', user=current_user)
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
    to_follow = User.query.filter(User.id != current_user.id).limit(3)
    return render_template('user/account.html', lang=lang, title=title,
                            user=user, msg=msg, posts=posts, to_follow=to_follow)

@user.route('/<int:id>/about', methods=['GET'])
@login_required
def about(id):
    lang = session['lang']
    title = _l('About')
    user = User.query.get_or_404(id)
    return render_template('user/about.html', lang=lang, title=title, user=user)

@user.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    unread = Messages.query.filter_by(recipent=current_user, read=False).all()
    for m in unread:
        m.read = True
        db_session.commit()
    page = request.args.get('page', 1, type=int)
    query = current_user.messages_received
    pagination = query.paginate(page, per_page=current_app.config['MESSAGES_PER_PAGE'], error_out=False)
    messages = pagination.items
    return render_template('user/messages.html', messages=messages)

@user.route('/chat/<id>/<username>', methods=['GET', 'POST'])
@login_required
def chat(id, username):
    title = _l('Chat')
    user = User.query.filter_by(username=username).first_or_404()
    chat = Chat.query.get(id)
    messages = Messages.query.filter_by(chat_id=chat.id).all()
    return render_template(
                            'user/chat.html', title=title, lang=session['lang'], 
                            user=user, chat=chat, messages=messages)
 
@socketio.on('send_message')
def handle_send_message(data):
    socketio.emit('received_message', data, chat=data['chat_id'])
    message = Messages(
                        text=data['message'],
                        sender_id=data['sender_id'], 
                        receiver_id=data['receiver_id'], 
                        chat_id=data['chat_id'])
    try:
        db_session.add(message)
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
