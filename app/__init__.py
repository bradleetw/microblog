from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'devfortesting'
app.config['PP_KEY_TESTING'] = 'Just for testing.'

from app import routes
