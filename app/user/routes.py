from flask import request, redirect, session, render_template, abort, flash, url_for
from flask.blueprints import Blueprint
from flask_login import current_user, login_required
from flask_babelplus import lazy_gettext as _l, get_locale
from sqlalchemy.orm import aliased

from app import db_session
from app.models import User, Message, Posts, PostRepost, PostLikes, PostBookmark
from app.user.forms import ChatForm, PostForm

user = Blueprint('user', __name__)

@user.route('/contacts', methods=['GET', 'POST'])
@login_required
def contacts():
    lang = session['lang']
    title = _l('Contacts')
    user = current_user._get_current_object()
    return render_template('user/contacts.html', user=user, lang=lang, title=title)


@user.route('/account/<int:id>', methods=['GET', 'POST'])
@login_required
def account(id):
    lang = session['lang']
    user = User.query.get_or_404(id)
    title = user.firstname + ' ' + user.lastname
    lang = session['lang']
    msg = _l('There\'s no activites yet')
    return render_template('user/account.html', lang=lang, title=title, user=user, msg=msg)

@user.route('/account/<int:id>/<string:action>', methods=['GET', 'POST'])
@login_required
def action(id, action):
    user = User.query.get_or_404(id)
    action = action
    if action == 'follow':
        current_user.follow(user)
        db_session.commit()
        return redirect(request.referrer)
    if action == 'unfollow':
        current_user.unfollow(user)
        db_session.commit()
        return redirect(request.referrer)
    if action == 'block':
        pass
    return render_template('user/account.html', id=id, action=action)


@user.route('/inbox', methods=['GET', 'POST'])
@login_required
def inbox():
    title = _l('Inbox')
    lang = session['lang']
    return render_template('user/messages.html', title=title, lang=lang)


@user.route('/<int:id>/posts')
@login_required
def posts(id):
    lang = session['lang']
    title = _l('Posts')
    post_form=PostForm()
    user = User.query.filter_by(id=id).first()
    msg = _l('There\'s no posts yet')
    if not user:
        abort(404)
    posts = Posts.query.filter_by(user_id=id).order_by(Posts.published_date.desc()).all()
    return render_template(
                            'user/account.html', title=title, lang=lang, user=user, 
                            post_form=post_form, posts=posts, msg=msg)


@user.route('/<int:id>/likes')
@login_required
def likes(id):
    lang = session['lang']
    title = _l('Likes')
    post_form=PostForm()
    user = User.query.filter_by(id=id).first()
    msg = _l('There\'s no likes yet')
    if not user:
        abort(404)
    posts = Posts.query.filter(Posts.likes, PostLikes.user_id==id)\
                                .order_by(PostLikes.timestamp.desc()).all()
    return render_template(
                            'user/account.html', lang=lang, title=title,
                            posts=posts, user=user, post_form=post_form,
                            msg=msg)


@user.route('/<int:id>/reposts', methods=['GET', 'POST'])
@login_required
def reposts(id):
    lang = session['lang']
    title = _l('Reposts')
    msg = _l('There\'s no reposts yet')
    post_form = PostForm()
    user = User.query.filter_by(id=id).first()
    users = User.query.filter(User.id != current_user.id).all()
    if not user:
        abort(404)
    posts = Posts.query.filter(Posts.reposts, PostRepost.user_id==id)\
                                .order_by(PostRepost.timestamp.desc()).all()
    return render_template(
                            'user/account.html', lang=lang, title=title,
                            posts=posts, user=user, post_form=post_form,
                            msg=msg)


@user.route('/<int:id>/bookmarks', methods=['GET', 'POST'])
@login_required
def bookmarks(id):
    lang = session['lang']
    title = _l('Bookmarks')
    msg = _l('There\'s no bookmarks yet')
    post_form=PostForm()
    user = User.query.filter_by(id=id).first()
    users = User.query.filter(User.id != current_user.id).all()
    if not user:
        abort(404)
    posts = Posts.query.filter(Posts.bookmarked, PostBookmark.user_id==id)\
                            .order_by(PostBookmark.timestamp.desc()).all()
    return render_template(
                            'user/account.html', lang=lang, title=title,
                            user=user, posts=posts, post_form=post_form,
                            msg=msg)


@user.route('/<int:id>/about', methods=['GET'])
@login_required
def about(id):
    lang = session['lang']
    title = _l('About')
    user = User.query.get_or_404(id)
    return render_template('user/about.html', lang=lang, title=title, user=user)


@user.route('/<int:id>/messages', methods=['GET'])
@login_required
def messages(id):
    user = User.query.get_or_404(id)
    return render_template('user/messages.html', user=user)


@user.route('/<int:id>/chat/', methods=['GET', 'POST'])
@login_required
def send_message(id):
    form = ChatForm()
    user = User.query.filter_by(id=id).first_or_404()
    sent = aliased(User)
    received = aliased(User)
    messages = db_session.query(Message)\
                    .join(Message.author.of_type(sent))\
                    .join(Message.recipient.of_type(received))\
                    .order_by(Message.timestamp.asc()).all()
    if request.method == 'POST' and form.validate_on_submit():
        body = str(form.body.data)
        msg = Message(sender_id=current_user.id, body=body, recipient_id=user.id)
        db_session.add(msg)
        flash('تم إرسال الرسالة', 'success')
        return redirect(request.referrer)
    return render_template(
                            'user/chat.html',
                            user=user,
                            recipient=user,
                            form=form, msgs=messages)
