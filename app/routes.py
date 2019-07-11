from app import app
from flask import render_template, redirect, flash, url_for
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Brad Lee'}
    post = [
        {'author': 'James', 'body': 'I am OK!'},
        {'author': 'Brad lee', 'body': 'Fine~~~'},
        {'author': 'Vivian', 'body': 'You are welcome'},
        {'author': 'Andy', 'body': 'No Problem!'}
    ]
    return render_template('index.html', title='Home', user=user, seq=post)

@app.route('/login', methods=['GET', 'POST'])
def login():
    user = {'username': 'Brad Lee'}
    form = LoginForm()
    if form.validate_on_submit():
        flash(
            f'Login requested for user {form.username.data}, \
                remember_me = {form.remember_me.data}'
        )
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', user=user, form=form)
