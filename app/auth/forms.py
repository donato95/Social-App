from flask_wtf import FlaskForm
from wtforms.fields import (StringField, DateField, TextAreaField,
                            PasswordField, BooleanField, EmailField, 
                            RadioField, SubmitField)
from wtforms.validators import DataRequired, Optional, Email, EqualTo, ValidationError
from flask_babelplus import lazy_gettext as _l
from flask_bcrypt import check_password_hash
from flask_login import current_user

from app.models import User
from app.util.validators import length, empty_check


class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Passowrd'), validators=[DataRequired()])
    remember = BooleanField(_l('Remember me'))
    submit = SubmitField(_l('Login'))

    def validate_username(self, field):
        empty_check(field)
        length(field=field, min=5, max=25)
        user = User.query.filter_by(username=field.data).first()
        if not user:
            raise ValidationError(_l('Username doesn\'t extists. Make sure you\'re registered'))

    def validate_password(self, field):
        empty_check(field)
        length(field=field, min=8, max=25)
        user = User.query.filter_by(username=self.username.data).first()
        if user and not check_password_hash(user.hashed_password, field.data):
            raise ValidationError(_l('Wrong password'))


class RegisterForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Passowrd'), validators=[DataRequired()])
    firstname = StringField(_l('First name'), validators=[DataRequired()])
    lastname = StringField(_l('Last name'), validators=[ DataRequired()])
    email = EmailField(_l('Email'), 
                    validators=[
                        DataRequired(), 
                        Email(message=_l('Please enter a valid email'))])
    confirm = PasswordField(_l('Confirm password'), 
                    validators=[
                        DataRequired(), 
                        EqualTo('password', message=_l('Passwords arn\'t matched'))])
    submit = SubmitField(_l('Register'))

    def validate_firstname(self, field):
        empty_check(field)
        length(field=field, min=3, max=25)
    
    def validate_lastname(self, field):
        empty_check(field)
        length(field=field, min=3, max=25)

    def validate_username(self, field):
        empty_check(field)
        length(field=field, min=5, max=25)
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError(_l('Username already extists. Try again with another username'))

    def validate_email(self, field):
        empty_check(field)
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError(_l('Email already extists. Try again with another username'))


class SettingsForm(FlaskForm):
    firstname = StringField(_l('First name'), validators=[DataRequired()])
    lastname = StringField(_l('Last name'), validators=[ DataRequired()])
    username = StringField(_l('Username'), validators=[DataRequired()])
    # upload = FileField(_l('Upload profile picture'))
    bio = TextAreaField(_l('Bio'), validators=[Optional()])
    city = StringField(_l('City'), validators=[Optional()])
    profossional = StringField(_l('Profossional'), validators=[Optional()])
    birth_date = DateField(_l('Date of birth'))
    gender = RadioField(
                        _l('Gender'), 
                        choices=[(0, _l('Male')), (1, _l('Female'))], 
                        validators=[Optional()])
    submit = SubmitField(_l('Save'))

    # def __init__(self, *args, **kwargs):
    #     super(SettingsForm, self).__init__(*args, **kwargs)

    def validate_firstname(self, field):
        empty_check(field)
        length(field=field, min=3, max=25)
    
    def validate_lastname(self, field):
        empty_check(field)
        length(field=field, min=3, max=25)

    def validate_username(self, field):
        empty_check(field)
        length(field=field, min=5, max=25)
        if field.data != current_user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(_l('Username already exists, try another one'))


class EmailResetForm(FlaskForm):
    old_email = EmailField(_l('Old email'), 
                    validators=[DataRequired(), Email(message=_l('Please enter a valid email'))])
    new_email = EmailField(_l('New email'), 
                    validators=[DataRequired(), Email(message=_l('Please enter a valid email'))])
    password = PasswordField(_l('Passowrd'), validators=[DataRequired()])
    submit = SubmitField(_l('Changes'))

    def validate_old_email(self, field):
        empty_check(field)
        user = User.query.filter_by(email=field.data).first()
        if not user:
            raise ValidationError(_l('Email doesn\'t match'))
    
    def validate_new_email(self, field):
        empty_check(field)
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError(_l('Email already extists. Try again with another username'))
    
    def validate_password(self, field):
        empty_check(field)
        length(field=field, min=8, max=25)
        user = User.query.filter_by(username=self.username.data).first()
        if user and not check_password_hash(user.hashed_password, field.data):
            raise ValidationError(_l('Wrong password'))


class PasswordUpdateForm(FlaskForm):
    old_password = PasswordField(_l('Old passowrd'), validators=[DataRequired()])
    new_password = PasswordField(_l('New passowrd'), validators=[DataRequired()])
    confirm = PasswordField(_l('Confirm password'), 
                        validators=[
                            DataRequired(), 
                            EqualTo('new_password', message=_l('Passwords aren\'t matched'))])
    submit = SubmitField(_l('Changes'))
    
    def validate_old_password(self, field):
        empty_check(field)
        length(field=field, min=8, max=25)
        user = User.query.filter_by(username=current_user.username).first()
        if user and not check_password_hash(user.hashed_password, field.data):
            raise ValidationError(_l('Wrong password'))
    
    def validate_new_password(self, field):
        empty_check(field)
        length(field=field, min=8, max=25)
    
    def validate_confirm(self, field):
        empty_check(field)


class ForgotPassForm(FlaskForm):
    email = EmailField(_l('Your email address'), 
                validators=[
                    DataRequired(), 
                    Email(message=_l('Please enter a valid email'))])
    submit = SubmitField(_l('Send'))

    def validate_email(self, field):
        empty_check(field)
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError(_l('Email already extists. Try again with another username'))


class PasswordResetForm(FlaskForm):
    new_password = PasswordField(_l('New passowrd'), validators=[DataRequired()])
    confirm = PasswordField(_l('Confirm password'), 
                        validators=[
                            DataRequired(), 
                            EqualTo('new_password', message=_l('Passwords aren\'t matched'))])
    submit = SubmitField(_l('Update'))
    
    def validate_new_password(self, field):
        empty_check(field)
        length(field=field, min=8, max=25)
    
    def validate_confirm(self, field):
        empty_check(field)


class ChatForm(FlaskForm):
    text = TextAreaField(validators=[DataRequired(_l('Can\'t send empty message'))])
    submit = SubmitField(_l('Send'))

    def validate_text(self, field):
        empty_check(field)

