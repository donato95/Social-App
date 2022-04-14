from flask_babelplus import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField
from wtforms.validators import DataRequired, ValidationError


class PostForm(FlaskForm):
    post = TextAreaField(_l('What\'s on your mind') ,validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

    def validate_post(self, field):
        if not field.data:
            raise ValidationError(_l('Can\'t be empty'))


class CommentForm(FlaskForm):
    content = TextAreaField(validators=[DataRequired()])
    submit = SubmitField(_l('Comment'))

    def validate_content(self, field):
        if not field.data:
            raise ValidationError(_l('Can\'t be emoty'))

