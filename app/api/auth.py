# from flask import jsonify, request
# from flask_bcrypt import check_password_hash
# from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

# from app import db_session
# from app.api import api
# from app.models import User
# from app.errors.errors import error_response


# basic_auth = HTTPBasicAuth()
# token_auth = HTTPTokenAuth()


# @basic_auth.verify_password
# def verify_password(username, password):
#     user = db_session.query(User).filter_by(username=username).first()
#     if user and check_password_hash(user.hashed_password, password):
#         return user
#     error_response(message='Incorrect Password')

# @token_auth.verify_token
# def check_token(token):
#     user = db_session.query(User).filter_by(api_token=token).first()
#     if user and user.check_token(token):
#         return user

# @basic_auth.error_handler
# def basic_auth_error(status):
#     error_response(status)

# @token_auth.error_handler
# def token_auth_error(status):
#     return error_response(status_code=status)

# @api.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     username = data['username']
#     password = data['password']
#     data = None
#     user = db_session.query(User).filter_by(username=username).first()
#     if user and check_password_hash(user.hashed_password, password):
#         data = user.to_dict()
#         token = user.get_token()
#         return jsonify({'data': data, "token": token})
#     return error_response(201, '')

# @api.route('/token/create', methods=['POST'])
# @basic_auth.login_required
# def create_token():
#     user = basic_auth.current_user()
#     token = user.get_token()
#     db_session.commit()
#     return jsonify({"token": token})

# @api.route('/token/revoke', methods=['DELETE'])
# @token_auth.login_required
# def revoke_token():
#     user = token_auth.current_user()
#     user.revoke_token()
#     return '', 204
