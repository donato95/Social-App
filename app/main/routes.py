import email
from flask import render_template, request, redirect, flash, url_for
from flask.blueprints import Blueprint
from flask_login import login_required, current_user, login_user, logout_user
from flask_babel import lazy_gettext as _l
from sqlalchemy.exc import IntegrityError

from app import session
from app.models import User
from app.main.forms import LoginForm, RegisterForm, SettingsForm

main = Blueprint('main', __name__)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = session.query(User).filter_by(username=username).first()
        if user:
            login_user(user, form.remember.data)
            flash(_l('You\'re successfuly logged in'), 'success')
            return redirect(url_for('main.account', id=user.id))
    return render_template('main/login.html', form=form)


@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        user = User(
                    username=username, firstname=firstname, 
                    lastname=lastname, email=email, password=password)
        try:
            session.add(user)
            session.commit()
            flash(_l('You\'re successfuly registered'), 'success')
            return redirect(url_for('main.login'))
        except IntegrityError:
            session.rollback()
            flash(_l('Sorry we couldn\'t register you, please try again'))
            return redirect(url_for(request.referrer))
    return render_template('main/register.html', form=form)


@main.route('/account/<int:id>', methods=['GET', 'POST'])
def account(id):
    user = User.query.get_or_404(id)
    return render_template('main/account.html', user=user)


@main.route('/account/<int:id>/settings', methods=['GET', 'POST'])
def setting(id):
    user = User.query.get_or_404(id)
    form = SettingsForm()
    if request.method == 'POST' and form.validate_on_submit():
        pass
    return render_template('main/settings.html', user=user, form=form)


@main.route('/account/<int:id>/delete', methods=['GET', 'POST'])
def delete(id):
    id = id
    return render_template('main/account.html', id=id)


@main.route('/account/<int:id>/confirm', methods=['GET', 'POST'])
def confirm(id):
    id = id
    return render_template('main/account.html', id=id)


@main.route('/account/<int:id>/<string:action>', methods=['GET', 'POST'])
def action(id, action):
    id = id
    action = action
    if action == 'follow':
        pass
    if action == 'unfollow':
        pass
    if action == 'block':
        pass
    return render_template('main/account.html', id=id, action=action)

