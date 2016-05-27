# -*- coding: utf-8 -*-

from flamejam import app, db


class GamescomApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    year = db.Column(db.Integer)
    city = db.Column(db.String(128))
    zip_code = db.Column(db.String(128))
    street = db.Column(db.String(128))
    job_title = db.Column(db.String(128))

    def __init__(self, user):
        self.user = user
        self.user_id = user.id
