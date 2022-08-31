from flask import Flask, request
from datetime import *
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flaskext.markdown import Markdown
from flask_principal import Principal, Permission, RoleNeed
from flask_login import LoginManager, current_user
from raven.contrib.flask import Sentry
from os import getenv
from flask_caching import Cache

app = Flask(__name__)
app.config.from_pyfile(getenv('FLAMEJAM_CONFIG', '/etc/flamejam/flamejam.cfg'))
app.config["CACHE_TYPE"] = 'memcached'
cache = Cache(app)

app.jinja_env.add_extension('jinja2.ext.loopcontrols')

mail = Mail(app)
db = SQLAlchemy(app)
markdown_object = Markdown(app, safe_mode="escape")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

principals = Principal(app)
admin_permission = Permission(RoleNeed('admin'))

sentry = Sentry(app, dsn=app.config.get('SENTRY_DSN'))

from flamejam.utils import *
import flamejam.filters
import flamejam.views
import flamejam.models


@app.context_processor
def inject():
    return dict(current_user=current_user,
                current_datetime=datetime.utcnow(),
                current_jam=get_current_jam(),
                RATING_CATEGORIES=flamejam.models.rating.RATING_CATEGORIES)
