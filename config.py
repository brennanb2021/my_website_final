import os
basedir = os.path.abspath(os.path.dirname(__file__))
from tempfile import mkdtemp # used to create a temp directory

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'th1515453cr3tk37'
    #generates a hidden field that includes a token that is used to protect the form against CSRF attacks
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False #dont need a notification every time the database is changed
    #configure app.db database, store it in basedir.
    TEMPLATES_AUTO_RELOAD=True
    SESSION_FILE_DIR =  mkdtemp()
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"