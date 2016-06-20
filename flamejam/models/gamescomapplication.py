# -*- coding: utf-8 -*-

from flamejam import app, db


class GamescomApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    year = db.Column(db.Integer)
    title = db.Column(db.String(128))
    city = db.Column(db.String(128))
    country = db.Column(db.String(128))
    zip_code = db.Column(db.String(128))
    street = db.Column(db.String(128))
    job_title = db.Column(db.String(128))
    experience = db.Column(db.String(128))
    reason = db.Column(db.String(255))
    travel_funding_amount = db.Column(db.Integer)
    travel_funding_reason = db.Column(db.String(255))

    def __init__(self, user):
        self.user = user
        self.user_id = user.id
