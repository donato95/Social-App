import os
from flask import current_app
from werkzeug.utils import secure_filename
from wtforms.validators import ValidationError
from PIL import Image
from flask_babelplus import lazy_gettext as _l


def length(field, min=-1, max=-1, message=None):
    """ Custome length validator """
    min = min
    max = max
    if not message:
        string = f'This field must be between {min} and {max} characters'
        message = _l(string)
    l = field.data and len(field.data) or 0
    if l < min or max != -1 and l > max:
        raise ValidationError(message)

def empty_check(field, message=None): 
    """ Custome required validator """
    if not message:
        message = _l('This field is required')
    if len(field.data) < 1:
        raise ValidationError(message)

def validate_image(field, allowed_ext, allowed_size):
    """ Imagef validation function """
    if field.data:
        filename = secure_filename(field.data)
    file_ext = os.path.splitext(filename)[1]
    if file_ext not in allowed_ext:
        return ValidationError(_l('Extention not allowed'))
    