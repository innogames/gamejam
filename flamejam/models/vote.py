# -*- coding: utf-8 -*-

from flamejam import app, db
from datetime import datetime


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    jam_id = db.Column(db.Integer, db.ForeignKey('jam.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    voted_at = db.Column(db.DateTime)

    def __init__(self, game, user):
        self.game = game
        self.jam = game.jam
        self.user = user
        self.voted_at = datetime.utcnow()

        self.game_id = game.id
        self.jam_id = game.jam_id
        self.user_id = user.id
