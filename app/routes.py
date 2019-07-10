from app import app
from flask import render_template

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
    