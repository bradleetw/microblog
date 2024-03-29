from app import app, db, babel
from flask import render_template, redirect, flash, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.forms import PostForm, UpdatePostForm, ResetPasswordRequestForm
from app.forms import ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from app.email import send_password_reset_email
from werkzeug.urls import url_parse
from werkzeug.exceptions import abort
from datetime import datetime
from flask_babel import _


@app.route('/')
@app.route('/index')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    print(_('Home Page'))

    return render_template('index.html',
                           title=_('Home Page'),
                           pagination=posts,
                           posts=posts.items)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title=_('Sign In'), form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html', title=_('Register'), form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    return render_template('user.html',
                           user=user,
                           pagination=posts,
                           posts=posts.items)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',
                           title=_('Edit Profile'),
                           form=form)


@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    body=form.body.data,
                    author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Congratulations, post is created!'))
        return redirect(url_for('index'))
    return render_template('post/create_post.html',
                           title=_('Create Post'),
                           form=form)


@app.route('/update_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = get_post(id=post_id)
    form = UpdatePostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        # post.timestamp = datetime.utcnow()
        db.session.commit()
        flash(_('Congratulations, post is updated!'))
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.body.data = post.body
    return render_template('post/update_post.html',
                           title=_('Edit Post'),
                           form=form)


@app.route('/delete/<int:post_id>', methods=('POST', ))
@login_required
def delete_post(post_id):
    post = get_post(id=post_id)
    db.session.delete(post)
    db.commit()
    return redirect(url_for('index'))


def get_post(id, check_author=True):
    post = Post.query.filter_by(id=id).first_or_404()
    if check_author and post.author != current_user:
        abort(403)
    return post


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User {0} not found.').format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following {0}').format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User {0} not found.').format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following {0}').format(username))
    return redirect(url_for('user', username=username))


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    return render_template('index.html',
                           title=_('Explore Page'),
                           pagination=posts,
                           posts=posts.items)


@app.route('/reset_password_request', methods=['POST', 'GET'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash(
                _('Check your email for the instruction to reset your password'))
        else:
            flash(_('There is no user with email, {0}').format(form.email.data))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title=_('Reset Password'),
                           form=form)


@app.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html',
                           title=_('Reset Your Password'),
                           form=form)
