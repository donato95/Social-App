from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer

# Token utill functions
def generate_confirm_token(email):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps(email, salt='confirmation')
    
def confirm_token(token, exp=1800):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='confirmation', max_age=exp)
    except:
        return False
    return email
