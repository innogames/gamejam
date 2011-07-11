from flask import Flask
from datetime import *
from flaskext.sqlalchemy import SQLAlchemy
from flaskext.markdown import Markdown

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flamejam.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'lolsecret'
db = SQLAlchemy(app)
Markdown(app, safe_mode="escape")

import flamejam.filters
import flamejam.views
import flamejam.models

@app.context_processor
def inject_announcement():
    a = flamejam.models.Announcement.query.order_by(flamejam.models.Announcement.posted.desc()).first()
    return dict(last_announcement = a)