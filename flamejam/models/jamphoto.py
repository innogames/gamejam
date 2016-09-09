from flamejam import db
from sqlalchemy.dialects.mysql import LONGBLOB


class JamPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jam_id = db.Column(db.Integer, db.ForeignKey('jam.id'))
    photo = db.Column(LONGBLOB)

    def __init__(self, jam_id, photo):
        self.jam_id = jam_id
        self.photo = photo
