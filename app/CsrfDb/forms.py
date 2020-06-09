from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField

class LoginForm(FlaskForm): #these have csrf validators but I turned them off because I'm doing it manually
    email = StringField('Email')
    password = PasswordField('Password')
    submit = SubmitField('Sign In')
        
class RegistrationForm(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    email = StringField('Email')
    password = PasswordField('Password')
    password2 = PasswordField('Repeat Password')
    submit = SubmitField('Register')

class EditPasswordForm(FlaskForm):
    password = PasswordField('Password')
    password2 = PasswordField('Repeat Password')
    submit = SubmitField('Change Password')

class EditAccountForm(FlaskForm):
    first_name = StringField('Change first name')
    last_name = StringField('Change last name')
    submit = SubmitField('Change account information')

