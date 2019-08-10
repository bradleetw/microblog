from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.fields.core import StringField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, \
    Length
from app.models import User


class LoginForm(FlaskForm):
    username = StringField(
        label='User Name',
        validators=[DataRequired(message='Need user name.')],
        render_kw={'placeholder': 'Please input user name'})
    password = PasswordField(
        label='Password',
        validators=[DataRequired(message='Need password')],
        render_kw={'placeholder': 'Please input password'})
    remember_me = BooleanField(label='Remember Me')
    submit = SubmitField(label='Sign In')


class RegistrationForm(FlaskForm):
    username = StringField(
        label='User name',
        validators=[
            DataRequired(message='User name is must'),
            Length(
                min=6,
                max=64,
                message='Must be at least 6 characters, at most 64 characters.'
            )
        ],
        description='Please input User name between 6 ~ 64 characters.',
        render_kw={'placeholder': 'Please input user name'})
    email = StringField(
        label='Email',
        validators=[DataRequired(message='Email address is must'),
                    Email()],
        description='Please input email address under 120 length.',
        render_kw={'placeholder': 'Please input email address'})
    password = PasswordField(
        label='Password',
        validators=[DataRequired(message='Password is must')],
        render_kw={'placeholder': 'Please input password'})
    password2 = PasswordField(
        label='Repeat Password',
        validators=[DataRequired(), EqualTo('password')],
        render_kw={'placeholder': 'Please input password again'})
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
    username = StringField(
        label='User name',
        validators=[
            DataRequired(message='User name is must'),
            Length(
                min=6,
                max=64,
                message='Must be at least 6 characters, at most 64 characters.'
            )
        ],
        description='Please input User name between 6 ~ 64 characters.',
        render_kw={'placeholder': 'Please input user name'})
    about_me = TextAreaField(
        label='About me',
        validators=[Length(max=140, message='Must be at most 140 characters')],
        description='Please input post content under 140 length.',
        render_kw={'placeholder': 'Please input self-content'})
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
    title = StringField(label='Post Title',
                        validators=[
                            DataRequired(message='Need Post title.'),
                            Length(max=64,
                                   message='Must be at most 64 characters')
                        ],
                        description='Please input post title under 64 length.',
                        render_kw={'placeholder': 'Please input post title'})
    body = TextAreaField(
        label='Content',
        validators=[Length(max=140, message='Must be at most 140 characters')],
        description='Please input post content under 140 length.',
        render_kw={'placeholder': 'Please input post content'})
    submit = SubmitField('New Post')


class UpdatePostForm(FlaskForm):
    title = StringField(label='Post Title',
                        validators=[DataRequired(message='Need Post title.')],
                        description='Please input post title under 64 length.',
                        render_kw={'placeholder': 'Please input post title'})
    body = TextAreaField(
        label='Content',
        validators=[Length(max=140, message='Must be at most 140 characters')],
        description='Please input post content under 140 length.',
        render_kw={'placeholder': 'Please input post content'})
    submit = SubmitField('Update')
    # delete = SubmitField('Delete')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(
        label='Email',
        validators=[DataRequired(message='Email address is must'),
                    Email()],
        description='Please input email address under 120 length.',
        render_kw={'placeholder': 'Please input email address'})
    submit = SubmitField('Send Password Reset e-mail')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        label='Password',
        validators=[DataRequired(message='Password is must')],
        render_kw={'placeholder': 'Please input password'})
    password2 = PasswordField(
        label='Repeat Password',
        validators=[DataRequired(), EqualTo('password')],
        render_kw={'placeholder': 'Please input password again'})
    submit = SubmitField('Request Password Reset')
