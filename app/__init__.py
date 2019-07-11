from flask import Flask

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY='devfortesting',
    PP_KEY_TESTING='Just for testing.'
)

from app import routes
