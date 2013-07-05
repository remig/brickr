from flask.ext.wtf import Form, TextField, PasswordField, BooleanField, RecaptchaField, HiddenField
from flask.ext.wtf import Required, Email, EqualTo
from wtforms.validators import ValidationError
from app.models import User

class LoginForm(Form):
    email = TextField('Email Address', [Required(), Email()])
    password = PasswordField('Password', [Required()])
    nextURL = HiddenField('nextURL')
    
class RegisterForm(Form):
    screen_name = TextField('Screen Name', [Required()])
    real_name = TextField('Real Name')
    email = TextField('Email address', [Required(), Email()])
    password = PasswordField('Password', [Required()])
    confirm = PasswordField('Repeat Password', [Required(), EqualTo('password', message = 'Passwords must match')])
    accept_tos = BooleanField('I accept the TOS')
    flickr_auth = BooleanField('Authenticate with Flickr')
    
    def validate_screen_name(form, field):
        if User.query.filter_by(name = field.data).count() > 0:
            raise ValidationError("That screen name is already taken.")

    def validate_email(form, field):
        if User.query.filter_by(email = field.data).count() > 0:
            raise ValidationError("There is already an account registered to this email address.")
