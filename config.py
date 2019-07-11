import os


class Config(object):
    '''
    Flask app config class.
    '''
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'devfortesting'

    PP_KEY_TESTING = 'Just for testing.'
