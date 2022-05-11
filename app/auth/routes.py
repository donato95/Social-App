from datetime import datetime
from flask import render_template, request, redirect, flash, url_for, session, current_app, abort
from flask.blueprints import Blueprint
from flask_login import login_required, login_user, logout_user, current_user
from flask_babelplus import lazy_gettext as _l
from sqlalchemy.exc import IntegrityError

from app import db_session
from app.models import User
from app.email.email import send_email
from app.util.token import generate_confirm_token, confirm_token
from app.auth.forms import (
                            LoginForm, RegisterForm, 
                            SettingsForm, EmailResetForm,
                            PasswordUpdateForm, PasswordResetForm,
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
                flash(_l('You\'re successfuly logged in, welcome back'), 'success')
                return redirect(url_for('main.home'))
            else:
                return redirect(url_for('auth.unconfirmed'))
    return render_template('auth/login.html', form=form, lang=lang, title=title)

@auth.route('/settings', methods=['GET', 'POST'])
@login_required
def setting():
    title = _l('Settings')
    lang = session['lang']
    form = SettingsForm()
    if form.validate_on_submit():
        print(f'Form data username[{form.username.data}]')
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.username = form.username.data
        current_user.job = form.profossional.data
        current_user.city = form.city.data
        current_user.gender = bool(form.gender.data)
        current_user.birth_date = form.birth_date.data
        current_user.bio = form.bio.data
        db_session.add(current_user._get_current_object())
        db_session.commit()
        flash(_l('Your informations has been updated'), 'success')
        return redirect(request.referrer)
    form.firstname.data = current_user.firstname
    form.lastname.data = current_user.lastname
    form.username.data = current_user.username
    form.bio.data = current_user.bio
    form.birth_date.data = current_user.birth_date
    form.city.data = current_user.city
    form.profossional.data = current_user.job
    return render_template('auth/settings.html', lang=lang, title=title, form=form)


@auth.route('/settings/email', methods=['GET', 'POST'])
@login_required
def email():    
    form = EmailResetForm()
    title = _l('Update Email')
    lang = session['lang']
    if form.validate_on_submit():
        current_user.email = form.new_email.data
        db_session.commit()
        flash(_l('Your email is updated'), 'success')
        return redirect(url_for('auth.email'))
    return render_template('auth/update_email.html', lang=lang, title=title, form=form)


@auth.route('/settings/password', methods=['GET', 'POST'])
@login_required
def update_password():
    form = PasswordUpdateForm()
    title = _l('Update Password')
    lang = session['lang']
    if form.validate_on_submit():
        current_user.password = form.new_password.data
        db_session.commit()
        flash(_l('Password updated'), 'success')
        return redirect(url_for('auth.update_password'))
    return render_template('auth/update_password.html', lang=lang, title=title, form=form)


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
    if form.validate_on_submit():
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
    if form.validate_on_submit():
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

