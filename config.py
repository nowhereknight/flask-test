import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default'
    MONGO_URI = os.environ.get('MONGO_URI') or \
        'mongodb://127.0.0.1:27017/wineadvisor'
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
