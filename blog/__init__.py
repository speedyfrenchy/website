from flask import Flask
from micawber import bootstrap_basic
from micawber.cache import Cache as OEmbedCache
from playhouse.flask_utils import FlaskDB
from flask_bootstrap import Bootstrap

from .config import Config

blog = Flask(__name__)
blog.config.from_object(Config)

flask_db = FlaskDB(blog)
database = flask_db.database

oembed_providers = bootstrap_basic(OEmbedCache())

bootstrap = Bootstrap(blog)

from flask_mail import Mail
email = Mail(blog)

from blog import routes, models