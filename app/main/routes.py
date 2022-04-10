from flask import current_app, render_template, request, redirect, flash, url_for, g, session
from flask.blueprints import Blueprint
from flask_login import login_required, current_user, login_user, logout_user
from flask_babelplus import lazy_gettext as _l, get_locale
from sqlalchemy.exc import IntegrityError

from app import db_session
from app.models import User
from app.main.forms import LoginForm, RegisterForm, SettingsForm, EmailResetForm, PasswordResetForm

main = Blueprint('main', __name__)

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


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    title = _l('Login')
    lang = session['lang']
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        user = db_session.query(User).filter_by(username=username).first()
        if user:
            login_user(user, form.remember.data)
            flash(_l('You\'re successfuly logged in'), 'success')
            return redirect(url_for('main.inbox', id=user.id))
    return render_template('main/login.html', form=form, lang=lang, title=title)


@main.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('pages.home'))


@main.route('/register', methods=['GET', 'POST'])
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
            session.add(user)
            session.commit()
            flash(_l('You\'re successfuly registered'), 'success')
            return redirect(url_for('main.login'))
        except IntegrityError:
            session.rollback()
            flash(_l('Sorry we couldn\'t register you, please try again'))
            return redirect(url_for(request.referrer))
    return render_template('main/register.html', form=form, lang=session['lang'], title=title)


@main.route('/contacts', methods=['GET', 'POST'])
@login_required
def contacts():
    lang = session['lang']
    title = _l('Contacts')
    user = current_user._get_current_object()
    return render_template('main/contacts.html', user=user, lang=lang, title=title)


@main.route('/account/<int:id>', methods=['GET', 'POST'])
@login_required
def account(id):
    user = User.query.get_or_404(id)
    title = _l('Profile')
    lang = session['lang']

    return render_template('main/account.html', user=user, lang=lang, title=title)


@main.route('/account/<int:id>/settings', methods=['GET', 'POST'])
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
    return render_template('main/settings.html', 
                            user=user, form=form, lang=session['lang'], 
                            title=title, email_form=email_form, 
                            password_form=password_form)


@main.route('/account/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete(id):
    id = id
    return render_template('main/account.html', id=id)


@main.route('/account/<int:id>/confirm', methods=['GET', 'POST'])
@login_required
def confirm(id):
    title = _l('Confirm Account')
    lang = session['lang']
    id = id
    return render_template('main/account.html', id=id, title=title, lang=lang)


@main.route('/account/<int:id>/<string:action>', methods=['GET', 'POST'])
@login_required
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


@main.route('/inbox', methods=['GET', 'POST'])
@login_required
def inbox():
    title = _l('Inbox')
    lang = session['lang']
    return render_template('main/messages.html', title=title, lang=lang)


