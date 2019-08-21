from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.fields.core import StringField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, \
    Length
from app.models import User
from flask_babel import lazy_gettext as _l



class LoginForm(FlaskForm):
    username = StringField(
        label=_l('User Name'),
        validators=[DataRequired(message=_l('Need user name.'))],
        render_kw={'placeholder': _l('Please input user name')})
    password = PasswordField(
        label=_l('Password'),
        validators=[DataRequired(message=_l('Need password'))],
        render_kw={'placeholder': _l('Please input password')})
    remember_me = BooleanField(label=_l('Remember Me'))
    submit = SubmitField(label=_l('Sign In'))


class RegistrationForm(FlaskForm):
    username = StringField(
        label=_l('User name'),
        validators=[
            DataRequired(message=_l('User name is must')),
            Length(
                min=6,
                max=64,
                message=_l('Must be at least 6 characters, at most 64 characters.')
            )
        ],
        description=_l('Please input User name between 6 ~ 64 characters.'),
        render_kw={'placeholder': _l('Please input user name')})
    email = StringField(
        label=_l('Email'),
        validators=[DataRequired(message=_l('Email address is must')),
                    Email()],
        description=_l('Please input email address under 120 length.'),
        render_kw={'placeholder': _l('Please input email address')})
    password = PasswordField(
        label=_l('Password'),
        validators=[DataRequired(message=_l('Password is must'))],
        render_kw={'placeholder': _l('Please input password')})
    password2 = PasswordField(
        label=_l('Repeat Password'),
        validators=[DataRequired(), EqualTo('password')],
        render_kw={'placeholder': _l('Please input password again')})
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different username.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different email address.'))


class EditProfileForm(FlaskForm):
    username = StringField(
        label=_l('User name'),
        validators=[
            DataRequired(message=_l('User name is must')),
            Length(
                min=6,
                max=64,
                message=_l('Must be at least 6 characters, at most 64 characters.')
            )
        ],
        description=_l('Please input User name between 6 ~ 64 characters.'),
        render_kw={'placeholder': _l('Please input user name')})
    about_me = TextAreaField(
        label=_l('About me'),
        validators=[Length(max=140, message=_l('Must be at most 140 characters'))],
        description=_l('Please input post content under 140 length.'),
        render_kw={'placeholder': _l('Please input self-content')})
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError(_l('Please use a different username.'))


class PostForm(FlaskForm):
    title = StringField(label=_l('Post Title'),
                        validators=[
                            DataRequired(message=_l('Need Post title.')),
                            Length(max=64,
                                   message=_l('Must be at most 64 characters'))
                        ],
                        description=_l('Please input post title under 64 length.'),
                        render_kw={'placeholder': _l('Please input post title')})
    body = TextAreaField(
        label=_l('Content'),
        validators=[Length(max=140, message=_l('Must be at most 140 characters'))],
        description=_l('Please input post content under 140 length.'),
        render_kw={'placeholder': _l('Please input post content')})
    submit = SubmitField(_l('New Post'))


class UpdatePostForm(FlaskForm):
    title = StringField(label=_l('Post Title'),
                        validators=[DataRequired(message=_l('Need Post title.'))],
                        description=_l('Please input post title under 64 length.'),
                        render_kw={'placeholder': _l('Please input post title')})
    body = TextAreaField(
        label=_l('Content'),
        validators=[Length(max=140, message=_l('Must be at most 140 characters'))],
        description=_l('Please input post content under 140 length.'),
        render_kw={'placeholder': _l('Please input post content')})
    submit = SubmitField(_l('Update'))
    # delete = SubmitField(_l('Delete'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(
        label=_l('Email'),
        validators=[DataRequired(message=_l('Email address is must')),
                    Email()],
        description=_l('Please input email address under 120 length.'),
        render_kw={'placeholder': _l('Please input email address')})
    submit = SubmitField(_l('Send Password Reset e-mail'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        label=_l('Password'),
        validators=[DataRequired(message=_l('Password is must'))],
        render_kw={'placeholder': _l('Please input password')})
    password2 = PasswordField(
        label=_l('Repeat Password'),
        validators=[DataRequired(), EqualTo('password')],
        render_kw={'placeholder': _l('Please input password again')})
    submit = SubmitField(_l('Request Password Reset'))
