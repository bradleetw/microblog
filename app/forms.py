from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField
from wtforms.fields.core import StringField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField(label='User Name', validators=[DataRequired(message='Need user name.')])
    password = PasswordField(label='Password', validators=[DataRequired(message='Need password')])
    remember_me = BooleanField(label='Remember Me')
    submit = SubmitField(label='Sign In')