from flask import request, render_template

from app import db_session
from app.errors import error_bp
from app.errors.errors import error_response as api_error_response


def json_response() -> bool:
    if request.is_json:
        return True

def is_html() -> bool:
    if request.accept_mimetypes['html/text']:
        return True

@error_bp.app_errorhandler(400)
def bad_request(error):
    if json_response():
        return api_error_response(400)
    if is_html():
        return render_template('errors/400.html')

@error_bp.app_errorhandler(401)
def unautherized_access(error):
    if json_response():
        return api_error_response(401)
    if is_html():
        return render_template('errors/401.html')

@error_bp.app_errorhandler(403)
def forbidden_access(error):
    if json_response():
        return api_error_response(403)
    if is_html():
        return render_template('errors/403.html')

@error_bp.app_errorhandler(404)
def not_found_error(error):
    if json_response():
        return api_error_response(404)
    if is_html():
        return render_template('errors/404.html')

error_bp.app_errorhandler(405)
def method_not_allowed(error):
    if json_response():
        return api_error_response(405)
    if is_html():
        return render_template('errors/405.html')

@error_bp.app_errorhandler(500)
def internerl_error(error):
    if json_response():
        return api_error_response(500)
    if is_html():
        return render_template('errors/500.html')
