from flask_wtf import FlaskForm
from wtforms.fields import (StringField, FileField,
                            PasswordField, BooleanField, EmailField, SubmitField)
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from flask_babelplus import lazy_gettext as _l
from flask_bcrypt import check_password_hash

from app.models import User


class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired(), ])
    password = PasswordField(_l('Passowrd'), validators=[DataRequired(), ])
    remember = BooleanField(_l('Remember me'), )
    submit = SubmitField(_l('Login'))

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if not field.data:
            raise ValidationError(_l('Fill the field first please'))
        if field.data and len(field.data) < 5:
            raise ValidationError(_l('Sorry usually username is 5 characters at leats'))
        if not user:
            raise ValidationError(_l('Username doesn\'t extists. Make sure you\'re registered'))

    def validate_password(self, field):
        user = User.query.filter_by(username=self.username.data).first()
        if not field.data:
            raise ValidationError(_l('Password field can\'t be empty'))
        if user and not check_password_hash(user.hashed_password, field.data):
            raise ValidationError(_l('Wrong password'))


class RegisterForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Passowrd'), validators=[DataRequired()])
    firstname = StringField(_l('First name'), validators=[DataRequired()])
    lastname = StringField(_l('Last name'), validators=[DataRequired()])
    email = EmailField(_l('Email'), validators=[DataRequired(), Email()])
    confirm = PasswordField(_l('Confirm password'), validators=[DataRequired(), EqualTo('password', message=_l('Passwords arn\'t matched'))])
    submit = SubmitField(_l('Register'))

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if not field.data:
            raise ValidationError(_l('Fill the username field first please'))
        if field.data and len(field.data) < 5:
            raise ValidationError(_l('Sorry username characters must be 5 at leats'))
        if user:
            raise ValidationError(_l('Username already extists. Try again with another username'))

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if not field.data:
            raise ValidationError(_l('Fill the email field first please'))
        if user:
            raise ValidationError(_l('Email already extists. Try again with another username'))

    def validate_firstname(self, field):
        if not field.data:
            raise ValidationError(_l('Fill the firstname field first please'))
        if field.data and len(field.data) < 4:
            raise ValidationError(_l('Sorry characters must be 4 at leats'))
        if field.data and len(field.data) > 25:
            raise ValidationError(_l('Sorry characters must not be more than 25'))

    def validate_lastname(self, field):
        if not field.data:
            raise ValidationError(_l('Fill the lastname field first please'))
        if field.data and len(field.data) < 4:
            raise ValidationError(_l('Sorry characters must be 4 at leats'))
        if field.data and len(field.data) > 25:
            raise ValidationError(_l('Sorry characters must not be more than 25'))

    def validate_password(self, field):
        if not field.data:
            raise ValidationError(_l('Fill the password field first please'))
        if field.data and len(field.data) < 9:
            raise ValidationError(_l('Sorry password have to be 8 characters at leats'))
        if field.data and len(field.data) > 25:
            raise ValidationError(_l('Sorry characters must not be more than 25'))
    
    def validate_confirm(self, field):
        if not field.data:
            raise ValidationError(_l('Fill the confirmation field first please'))


class SettingsForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    firstname = StringField(_l('First name'), validators=[DataRequired()])
    lastname = StringField(_l('Last name'), validators=[DataRequired()])
    email = EmailField(_l('Email'), validators=[DataRequired(), Email()])
    upload = FileField(_l('Upload profile picture'))
    submit = SubmitField(_l('Save'))

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if not field.data:
            raise ValidationError(_l('Fill the username field first please'))
        if field.data and len(field.data) < 5:
            raise ValidationError(_l('Sorry username characters must be 5 at leats'))
        if user:
            raise ValidationError(_l('Username already extists. Try again with another username'))

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if not field.data:
            raise ValidationError(_l('Fill the email field first please'))
        if user:
            raise ValidationError(_l('Email already extists. Try again with another username'))

    def validate_firstname(self, field):
        if not field.data:
            raise ValidationError(_l('Fill the firstname field first please'))
        if field.data and len(field.data) < 4:
            raise ValidationError(_l('Sorry characters must be 4 at leats'))
        if field.data and len(field.data) > 25:
            raise ValidationError(_l('Sorry characters must not be more than 25'))

    def validate_lastname(self, field):
        if not field.data:
            raise ValidationError(_l('Fill the lastname field first please'))
        if field.data and len(field.data) < 4:
            raise ValidationError(_l('Sorry characters must be 4 at leats'))
        if field.data and len(field.data) > 25:
            raise ValidationError(_l('Sorry characters must not be more than 25'))
