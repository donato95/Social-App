from flask import render_template, request, redirect, flash
from flask.blueprints import Blueprint

main = Blueprint('main', __name__)

@main.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('main/login.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('main/register.html')


@main.route('/account/<int:id>', methods=['GET', 'POST'])
def account(id):
    id = id
    return render_template('main/account.html', id=id)


@main.route('/account/<int:id>/setting', methods=['GET', 'POST'])
def setting(id):
    id = id
    return render_template('main/setting.html', id=id)


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

