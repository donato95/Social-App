from flask import jsonify, redirect, request, render_template, flash, url_for, abort, session, current_app
from flask.blueprints import Blueprint
from flask_babelplus import lazy_gettext as _l
from sqlalchemy.exc import IntegrityError
from flask_login import current_user, login_required, login_fresh

from app import db_session
from app.util.decorators import admin_required
from app.models import User, Posts, Roles
from app.admin.forms import CreateAccountForm, EditAccountForm

admin = Blueprint('admin', __name__)

@admin.route('/home', methods=['GET', 'POST'])
@login_required
@admin_required
def home():
    u_query = User.query
    p_query = Posts.query
    users = u_query.order_by(User.joined_date.desc()).limit(20)
    return render_template('admin/home.html', lang=session['lang'], title='Dashboard', 
                            u_count=u_query.count(), p_count=p_query.count(), users=users)

@admin.route('/account', methods=['GET', 'POST'])
@login_required
@admin_required
def account():
    page = request.args.get('page', 1, type=int)
    query = Posts.query.filter_by(author=current_user).order_by(Posts.published_date.desc())
    pagination = query.paginate(page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    msg = _l('There\'s no activites yet')
    to_follow = User.query.order_by(User.joined_date.desc()).limit(3)
    return render_template('user/account.html', lang=session['lang'], title='Account', pagination=pagination,
                            user=current_user, posts=posts, to_follow=to_follow, msg=msg)

@admin.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.paginate(page, per_page=current_app.config['USER_PER_PAGE'], error_out=False)
    users = pagination.items
    return render_template('admin/users.html', lang=session['lang'], title=_l('Users'), users=users, pagination=pagination)

@admin.route('/account/<action>', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_user(action):
    lang = session['lang']
    create = False
    edit = False
    if action == 'create':
        form = CreateAccountForm()
        if form.validate_on_submit():
            username = form.username.data
            firstname = form.firstname.data
            lastname = form.lastname.data
            password = form.password.data
            activate = form.activate.data
            email = form.email.data
            role_id = int(form.role.data)
            role = Roles.query.get(role_id)
            user = User(username=username, firstname=firstname, lastname=lastname, 
                        password=password, confirmed=activate, email=email, role=role)
            db_session.add(user)
            try:
                db_session.commit()
                user.add_chat()
                db_session.commit()
                user.add_self_follows()
                db_session.commit()
            except IntegrityError:
                db_session.rollback()
        return render_template('admin/user.html', lang=lang, title=_l('Create User Account'), 
                           form=form, create=True)
    if action == 'edit':
        user = User.query.get_or_404(request.args.get('id'))
        form = EditAccountForm(user=user)
        if form.validate_on_submit():
            user.username = form.username.data
            user.firstname = form.firstname.data
            user.lastname = form.lastname.data
            user.confirmed = form.activate.data
            role_id = int(form.role.data)
            role = Roles.query.get(role_id)
            user.role = role
            try:
                db_session.add(user)
                db_session.commit()
                print(f'user role [{user.role.name}]')
                return redirect(request.referrer)
            except IntegrityError:
                db_session.rollback()
        form.username.data = user.username
        form.firstname.data = user.firstname
        form.lastname.data = user.lastname
        form.activate.data = user.confirmed
        form.role.data = user.role
        return render_template('admin/user.html', lang=lang, title=_l('Edit User Account'), edit=True, 
                                form=form)
    if action == 'delete':
        user = User.query.get_or_404(request.args.get('id'))
        db_session.delete(user)
        db_session.commit()
        return redirect(request.referrer)

@admin.route('/reports', methods=['GET', 'POST'])
@login_required
@admin_required
def reports():
    return 'Users report handling'
