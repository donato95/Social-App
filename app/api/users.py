from flask import abort, jsonify, request

from app import db_session
from app.api import api
from app.models import User
from app.api.auth import basic_auth
from app.util import valid_credintials


@api.route('/account', methods=['GET'])
@basic_auth.login_required
def account():
    user = basic_auth.current_user()
    data = user.to_dict()
    return {'data': data}

@api.route('/account/edit', methods=['POST'])
@basic_auth.login_required
def edit_account():
    user = basic_auth.current_user()
    if not user:
        abort(404)
    data = request.get_json()
    if user.username != data['username']:
        if valid_credintials(field='username', Model=User):
            return jsonify({"error_msg": "Username is already exits"})
        user.username = data['username']
    if user.email != data['email']:
        if valid_credintials(field='email', Model=User):
            return jsonify({"error_msg": "Username is already exits"})
        user.username = data['username']
    user.user_image = data['image']
    user.full_name = data['fullname']
    db_session.commit()
    return jsonify({"user": user.to_dict()})
