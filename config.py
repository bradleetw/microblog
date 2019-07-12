import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    '''
    Flask app config class.
    '''
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'devfortesting'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PP_KEY_TESTING = 'Just for testing.'
