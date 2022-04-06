from flask import render_template, request, redirect, flash
from flask.blueprints import Blueprint

main = Blueprint('main', __name__)

@main.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('main/login.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('main/register.html')