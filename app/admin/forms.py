from tkinter.tix import Select
from flask_wtf import FlaskForm
from wtforms.fields import SelectField,  StringField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired
from flask_babelplus import lazy_gettext as _l

from app.util.validators import empty_check, length
from app.auth.forms import RegisterForm, Roles, User

class CreateAccountForm(RegisterForm):
    activate = BooleanField(_l('Activate'))
    role = SelectField(_l('Role & Permissions'), coerce=int)

    def __init__(self, *formdata, **kwargs):
        super(CreateAccountForm, self).__init__(*formdata, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Roles.query.all()]


class EditAccountForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    firstname = StringField(_l('Firstname'), validators=[DataRequired()])
    lastname = StringField(_l('Lastname'), validators=[DataRequired()])
    activate = BooleanField(_l('Activate'))
    role = SelectField(_l('Role & Permission'), coerce=int)
    submit = SubmitField()

    def __init__(self, user, *formdata, **kwargs):
        super(EditAccountForm, self).__init__(*formdata, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Roles.query.all()]
        self.user = user

    def validate_firstname(self, field):
        empty_check(field)
        length(field)
    
    def validate_lastname(self, field):
        empty_check(field)
        length(field)
    
    def validate_username(self, field):
        empty_check(field)
        length(field=field, min=5, max=25)
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(_l('Username already exists, try another one'))
