import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')

    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

    DATABASE = 'sqliteext:///%s' % os.path.join(basedir, 'blog.db')

    SITE_WIDTH = 800
