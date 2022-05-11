from flask import jsonify, render_template, redirect, flash, request, abort, session
from flask.blueprints import Blueprint
from flask_login import current_user, login_required
from flask_babelplus import lazy_gettext as _l

from app import db_session
from app.posts.forms import CommentForm
from app.models import Posts, PostLikes, Comments

posts = Blueprint('posts', __name__)

@posts.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def post(id):
    lang = session['lang']
    comment_form = CommentForm()
    post = Posts.query.filter_by(id=id).order_by(Posts.published_date.desc()).first()
    title = post.content
    comments = Comments.query.filter_by(post_id=id).order_by(Comments.published_date.desc()).all()
    if not post:
        abort(404)
    if request.method == 'POST' and comment_form.validate_on_submit():
        content = comment_form.content.data
        comment = Comments(content=content, post_id=id, user_id=current_user.id)
        db_session.add(comment)
        db_session.commit()
        if current_user != post.author:
            text = '{} has commented your post'.format(current_user.username)
            tr = _l(text)
            post.author.add_notifications(name='commented', user=current_user, post=post.id)
            db_session.commit()
        return redirect(request.referrer)
    return render_template(
        'posts/post.html', lang=lang, post=post, title=title,
        comment_form=comment_form, comments=comments)

@posts.route('/post/<int:id>/<string:action>', methods=['GET'])
@login_required
def action(id, action):
    post = Posts.query.filter_by(id=id).first_or_404()
    message = None
    text = None
    if action is None:
        abort(404)
    if action == 'mark':
        current_user.book(post)
        db_session.commit()
        message = _l('bookmarke saved')
        text = _l('Remove bookmark')
    if action == 'unmark':
        current_user.unbook(post)
        db_session.commit()
        message = _l('bookmarke removed')
        text = _l('Bookmark')
    if action == 'like':
        like = PostLikes(post_id=post.id, user_id=current_user.id)
        db_session.add(like)
        db_session.commit()
        message = _l('liked')
        if current_user != post.author:
            post.author.add_notifications(name='liked', user=current_user, post=post.id)
            db_session.commit()
    if action == 'unlike':
        current_user.unliked(post)
        db_session.commit()
        message = _l('unliked')
    if action == 'repost':
        current_user.repost(post)
        db_session.commit()
        message = _l('repotsed')
        if current_user != post.author:
            post.author.add_notifications(name='reposted', user=current_user, post=post.id)
            db_session.commit()
    if action == 'unrepost':
        current_user.unrepost(post)
        db_session.commit()
        message = _l('unreposted')
    if action == 'private':
        post.is_public = False
        db_session.commit()
        message = _l('is private')
        text = _l('Public')
    if action == 'public':
        post.is_public = True
        db_session.commit()
        message = _l('is public')
        text = _l('Private')
    if action == 'delete':
        db_session.delete(post)
        db_session.commit()
        message = _l('deleted')
    return jsonify({"message": _l('Post ') + message, "text": text})

