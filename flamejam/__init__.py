import os, sys
from flask import Flask, request
from datetime import *
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.markdown import Markdown
from flask.ext.principal import Principal, Permission, RoleNeed
from flask.ext.login import LoginManager, current_user
from flask.ext.cache import Cache
import pyfscache

cache_it = pyfscache.FSCache('/tmp/iggj', days=1)

app = Flask(__name__)

if os.environ.get('CONFIG_TYPE') == "production":
    app.config.from_pyfile('/usr/share/doc/flamejam/flamejam.cfg.default')
    app.config.from_pyfile('/etc/flamejam/flamejam.cfg', silent=True)
else:
    app.config.from_pyfile('../doc/flamejam.cfg.default')
    app.config.from_pyfile('../flamejam.cfg', silent=True)
    app.config.from_pyfile('../doc/flamejam.cfg', silent=True)
    app.config.from_pyfile('/etc/flamejam/flamejam-staging.cfg', silent=True)

if os.environ.get('CONFIG_SITE') == "gamescom":
    app.config.from_pyfile('/etc/flamejam/flamejam-gamescom.cfg', silent=True)

app.jinja_env.add_extension('jinja2.ext.loopcontrols')

mail = Mail(app)
db = SQLAlchemy(app)
markdown_object = Markdown(app, safe_mode="escape")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

principals = Principal(app)
admin_permission = Permission(RoleNeed('admin'))

cache = Cache(app)

from flamejam.utils import *
import flamejam.filters
import flamejam.views
import flamejam.models


@app.context_processor
def inject():
    return dict(current_user=current_user,
                current_datetime=datetime.utcnow(),
                current_jam=get_current_jam(),
                gamescom=((request.host.find('igjam.eu') != -1) | (request.host.find('gamejam-staging.innogames.com') != -1)),
                RATING_CATEGORIES=flamejam.models.rating.RATING_CATEGORIES)
