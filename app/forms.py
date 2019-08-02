from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.fields.core import StringField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, \
    Length
from app.models import User


class LoginForm(FlaskForm):
    username = StringField(
        label='User Name',
        validators=[DataRequired(message='Need user name.')])
    password = PasswordField(
        label='Password', validators=[DataRequired(message='Need password')])
    remember_me = BooleanField(label='Remember Me')
    submit = SubmitField(label='Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('User name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password',
                              validators=[DataRequired(),
                                          EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('User name', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class PostForm(FlaskForm):
    title = StringField('Post Title',
                        validators=[DataRequired(message='Need Post title.')])
    body = TextAreaField('Content', validators=[Length(min=0, max=140)])
    submit = SubmitField('New Post')


class UpdatePostForm(FlaskForm):
    title = StringField('Post Title',
                        validators=[DataRequired(message='Need Post title.')])
    body = TextAreaField('Content', validators=[Length(min=0, max=140)])
    submit = SubmitField('Update')
    # delete = SubmitField('Delete')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password',
                              validators=[DataRequired(),
                                          EqualTo('password')])
    submit = SubmitField('Request Password Reset')
