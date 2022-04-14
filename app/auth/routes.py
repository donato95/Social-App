from flask import render_template, request, redirect, flash, url_for, session
from flask.blueprints import Blueprint
from flask_login import login_required, login_user, logout_user, current_user
from flask_babelplus import lazy_gettext as _l
from sqlalchemy.exc import IntegrityError

from app import db_session
from app.models import User
from app.auth.forms import LoginForm, RegisterForm, SettingsForm, EmailResetForm, PasswordResetForm

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    title = _l('Create Account')
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
            db_session.add(user)
            db_session.commit()
            flash(_l('You\'re successfuly registered'), 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db_session.rollback()
            flash(_l('Sorry we couldn\'t register you, please try again'))
            return redirect(url_for(request.referrer))
    return render_template('auth/register.html', form=form, lang=session['lang'], title=title)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    title = _l('Login')
    lang = session['lang']
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        user = db_session.query(User).filter_by(username=username).first()
        if user:
            login_user(user, form.remember.data)
            flash(_l('You\'re successfuly logged in'), 'success')
            return redirect(url_for('user.inbox', id=user.id))
    return render_template('auth/login.html', form=form, lang=lang, title=title)

@auth.route('/account/<int:id>/settings', methods=['GET', 'POST'])
@login_required
def setting(id):
    user = User.query.get_or_404(id)
    form = SettingsForm()
    email_form = EmailResetForm()
    password_form = PasswordResetForm()
    title = _l('Settings')
    if request.method == 'POST' and form.validate_on_submit():
        pass
    if request.method == 'POST' and email_form.validate_on_submit():
        pass
    if request.method == 'POST' and password_form.validate_on_submit():
        pass
    return render_template('auth/settings.html', 
                            user=user, form=form, lang=session['lang'], 
                            title=title, email_form=email_form, 
                            password_form=password_form)

@auth.route('/account/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete(id):
    id = id
    return render_template('main/account.html', id=id)

@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('pages.home'))

