import os
import unittest
import click

from app import create_app
from app.models import Roles

app = create_app('default')

@app.cli.group()
def translate():
    """ Translation and localization commands. """
    pass

@translate.command()
def update():
    """ Update all languages """
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command faild')
    if os.system('pybabel update -i messages.pot -d app/translations'):
        raise RuntimeError('update command faild')
    os.remove('messages.pot')

@translate.command()
def compile():
    """ Compile all languages """
    if os.system('pybabel compile -d app/translations'):
        raise RuntimeError('compile command faild')

@translate.command()
@click.argument('lang')
def init(lang):
    """ Initialize new language"""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
         raise RuntimeError('extract command failed')
    if os.system('pybabel init -i messages.pot -d app/translations -l ' + lang):
        raise RuntimeError('init command failed')
    os.remove('messages.pot')

@app.cli.command()
def test():
    """ Run the unit test code """
    tests = unittest.TestLoader().discover('tests', top_level_dir=app.root_path)
    unittest.TextTestRunner(verbosity=2).run(tests)

@app.cli.command()
def roles():
    """ Insert user roles into database """
    Roles.add_roles()
