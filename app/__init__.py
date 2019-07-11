from flask import Flask

app = Flask(__name__)

app.config.from_object('app.default_cfg')

from app import routes
