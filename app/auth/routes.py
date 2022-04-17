from os import abort
from flask import render_template, request, redirect, flash, url_for, session, current_app
from flask.blueprints import Blueprint
from flask_login import login_required, login_user, logout_user, current_user
from flask_babelplus import lazy_gettext as _l
from sqlalchemy.exc import IntegrityError

from app import db_session
from app.models import User
from app.email.email import send_email
from app.util import generate_confirm_token, confirm_token
from app.auth.forms import (
                            LoginForm, RegisterForm, 
                            SettingsForm, EmailResetForm, 
                            PasswordResetForm, PasswordUpdateForm,
                            ForgotPassForm)

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
            token = generate_confirm_token(user.email)
            token_url = url_for('auth.confirm', token=token, _external=True)
            header = _l('Welcome! Thanks for signing up. Please follow this link to activate your account:')
            html = render_template('layout/email.html', username=user.username, token_url=token_url, header=header)
            send_email(
                subject=_l('Email confirmation'), 
                recipient=[user.email],
                sender=current_app.config['MAIL_USERNAME'],
                html_body=html)
            flash(_l('You\'re successfuly registered, Check your email for confirmation'), 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db_session.rollback()
            flash(_l('Sorry we couldn\'t register you, please try again'))
            return redirect(request.referrer)
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
        user = User.query.filter_by(username=username).first()
        if user:
            login_user(user, form.remember.data)
            if user.confirmed:
                flash(_l('You\'re successfuly logged in'), 'success')
                return redirect(url_for('main.home', id=user.id))
            else:
                return redirect(url_for('auth.unconfirmed'))
    return render_template('auth/login.html', form=form, lang=lang, title=title)

@auth.route('/account/<int:id>/settings', methods=['GET', 'POST'])
@login_required
def setting(id):
    user = User.query.get_or_404(id)
    form = SettingsForm()
    email_form = EmailResetForm()
    password_form = PasswordUpdateForm()
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


@auth.route('/account/unconfirmed', methods=['GET'])
@login_required
def unconfirmed():
    title = _l('Unconfirmed')
    lang = session['lang']
    if current_user.confirmed:
        return redirect(url_for('main.home'))
    else:
        token = generate_confirm_token(current_user.email)
        token_url = url_for('auth.confirm', token=token, _external=True)
        header = _l('Welcome! Thanks for signing up. Please follow this link to activate your account:')
        html = render_template('layout/email.html', username=current_user.username, token_url=token_url, header=header)
        try:
            send_email(
                subject=_l('Confirm Account'), 
                recipient=[current_user.email], 
                sender=current_app.config['MAIL_USERNAME'], 
                html_body=html)
        except:
            logout_user()
            return redirect(url_for('auth.login'))
    return render_template('auth/unconfirmed.html', lang=lang, title=title)


@auth.route('/account/<token>/confirm', methods=['GET', 'POST'])
@login_required
def confirm(token):
    try:
        email = confirm_token(token)
    except:
        flash(_l('Confirmation link is invalid'))
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        return redirect(url_for('main.login'))
    else:
        user.confirmed = True
        db_session.commit()
        flash(_l('Congrates, you have confirmed your account'))
    return redirect(url_for('main.home'))


@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    title = _l('Forgot Password')
    lang = session['lang']
    form = ForgotPassForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(email=str(form.email.data)).first()
        if user:
            token = generate_confirm_token(user.email)
            token_url = url_for('auth.reset', token=token, _external=True)
            header = _l('Hello, We\'ve notice that you requested a new password link:')
            html = render_template('layout/email.html', username=user.username, token_url=token_url, header=header)
            try:
                send_email(
                    subject=_l('Password Reset'), 
                    recipient=[user.email], 
                    sender=current_app.config['MAIL_USERNAME'], 
                    html_body=html)
                flash(_l('Confirmation link has been sent to your email'), 'success')
                return redirect(request.referrer)
            except:
                flash(_l('Email wasn\'t sent please make sure you enter valid email'))
                return redirect(request.referrer)
    return render_template('auth/forgot_password.html', lang=lang, title=title, form=form)


@auth.route('/reset/<token>', methods=['GET'])
def reset(token):
    try:
        email = confirm_token(token)
    except:
        flash(_l('Confirmation link is invalid'))
        return redirect(url_for('auth.forgot_password'))
    user = User.query.filter_by(email=email).first_or_404()
    if user:
        return redirect(url_for('auth.reset_password', id=user.id))        
    else:
        return redirect(url_for('auth.forgot_password'))    

@auth.route('/<int:id>/reset_password', methods=['GET', 'POST'])
def reset_password(id):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    title = _l('Reset Password')
    lang = session['lang']
    form = PasswordResetForm()
    user = User.query.get_or_404(id)
    if not user:
        abort(404)
    if request.method == 'POST' and form.validate_on_submit():
        user.password = str(form.password.data)
        db_session.commit()
        return redirect(url_for('auth.login'))
    return render_template('auth/passreset.html', lang=lang, title=title, form=form)


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

