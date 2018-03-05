import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'definitely-a-secret'

    ADMIN_PASSWORD = 'secret'

    DATABASE = 'sqliteext:///%s' % os.path.join(basedir, 'blog.db')

    SITE_WIDTH = 800