import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')

    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

    DATABASE = 'sqliteext:///%s' % os.path.join(basedir, 'blog.db')

    SITE_WIDTH = 800

    # email server setup
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL_ADDRESS')
