from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from flask_babelplus import lazy_gettext as _l


class ChatForm(FlaskForm):
    text = TextAreaField(validators=[DataRequired(_l('Can\'t send empty message'))])
    submit = SubmitField(_l('Send'))

class PostForm(FlaskForm):
    content = TextAreaField(validators=[DataRequired(_l('Can\'t send empty message'))])
    submit = SubmitField(_l('Send'))
