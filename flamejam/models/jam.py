# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from flask import url_for, Markup, render_template
from flask_mail import Message
from smtplib import SMTPRecipientsRefused

from flamejam import app, db, mail
from flamejam.filters import formattime, humandelta
from flamejam.models import Game, GamePackage
from flamejam.utils import get_slug


class Jam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(128), unique=True)
    title = db.Column(db.String(128), unique=True)
    theme = db.Column(db.String(128))
    location = db.Column(db.String(255))
    announced = db.Column(db.DateTime)  # Date on which the jam was announced
    start_time = db.Column(db.DateTime)  # The jam starts at this moment
    team_limit = db.Column(db.Integer)  # 0 = no limit
    on_site_limit = db.Column(db.Integer, nullable=False, default=0)  # 0 = no on-site participants
    games = db.relationship("Game", backref="jam", lazy="noload")
    participations = db.relationship(
        "Participation",
        backref="jam",
        lazy="select"
    )
    teams = db.relationship("Team", backref="jam", lazy="noload")
    photos = db.relationship("JamPhoto", backref="jam", lazy="noload")

    description = db.Column(db.Text)
    restrictions = db.Column(db.Text)

    registration_duration = db.Column(db.Integer)  # hours
    packaging_duration = db.Column(db.Integer)  # hours
    rating_duration = db.Column(db.Integer)  # hours
    duration = db.Column(db.Integer)  # hours

    # last notification that was sent, e.g. 0 = announcement,
    # 1 = registration, (see status codes)
    last_notification_sent = db.Column(db.Integer, default=-1)

    def __init__(self,
                 title,
                 start_time,
                 duration=48,
                 team_limit=0,
                 on_site_limit=0,
                 theme=''):
        self.title = title
        self.slug = get_slug(title)
        self.start_time = start_time
        self.duration = duration
        self.registration_duration = 24 * 14
        self.packaging_duration = 24 * 1
        self.rating_duration = 24 * 5
        self.announced = datetime.utcnow()
        self.theme = theme
        self.team_limit = team_limit
        self.on_site_limit = on_site_limit

    @property
    def participants(self):
        return [r.user for r in self.participations]

    @property
    def end_time(self):
        return self.start_time + timedelta(hours=self.duration)

    @property
    def packaging_deadline(self):
        return self.end_time + timedelta(hours=self.packaging_duration)

    @property
    def rating_end(self):
        return self.packaging_deadline + timedelta(hours=self.rating_duration)

    @property
    def registration_start(self):
        return self.start_time - timedelta(hours=self.registration_duration)

    def __repr__(self):
        return '<Jam %r>' % self.slug

    def getStatus(self):
        now = datetime.utcnow()
        if self.registration_start > now:
            return JamStatus(JamStatusCode.ANNOUNCED, self.start_time)
        elif self.start_time > now:
            return JamStatus(JamStatusCode.REGISTRATION, self.start_time)
        elif self.end_time > now:
            return JamStatus(JamStatusCode.RUNNING, self.end_time)
        elif self.packaging_deadline > now:
            return JamStatus(JamStatusCode.PACKAGING, self.packaging_deadline)
        elif self.rating_end > now:
            return JamStatus(JamStatusCode.RATING, self.rating_end)
        else:
            return JamStatus(JamStatusCode.FINISHED, self.end_time)

    def url(self, **values):
        return url_for('jam_info', jam_slug=self.slug, **values)

    def gamesFilteredByPackageTypes(self, filters):
        games = Game.query.filter_by(is_deleted=False).filter_by(jam_id=self.id)
        if filters == set():
            games = games
        elif 'packaged' in filters:
            games = games.join(GamePackage)
        else:
            games = games.filter(GamePackage.type.in_(filters)).join(
                GamePackage
            )
        return games.all()

    def gamesByScore(self, filters=set()):
        e = self.gamesFilteredByPackageTypes(filters)
        e.sort(key=Game.numberVotes.fget, reverse=True)
        return e

    def gamesByTotalRatings(self, filters=set()):
        e = self.gamesFilteredByPackageTypes(filters)
        e.sort(key=Game.numberRatings.fget)
        return e

    @property
    def showTheme(self):
        return self.getStatus().code >= JamStatusCode.RUNNING and self.theme

    @property
    def showRatings(self):
        return self.getStatus().code == JamStatusCode.FINISHED

    def getLink(self):
        s = '<a class="jam" href="%s">%s</a>' % (self.url(), self.title)
        if self.showTheme:
            s += ' <span class="theme">%s</span>' % self.theme
        return Markup(s)

    def sendAllNotifications(self):
        last = -1
        for n in range(
            self.last_notification_sent + 1,
            self.getStatus().code + 1
        ):
            if self.sendNotification(n): last = n
        return last

    def sendNotification(self, n):
        if not JamStatusCode.ANNOUNCED <= n <= JamStatusCode.FINISHED: return \
            False

        kwargs = {}

        if n == JamStatusCode.ANNOUNCED:
            template = "announcement"
            notify = "new_jam"
            subject = "Jam announced: " + self.title
        elif n == JamStatusCode.REGISTRATION:
            template = "registration_start"
            notify = "new_jam"
            subject = "Registrations for " + self.title + " now open"
        elif n == JamStatusCode.RUNNING:
            template = "start"
            notify = "jam_start"
            subject = self.title + " starts now!"
        elif n == JamStatusCode.PACKAGING:
            template = "packaging_start"
            notify = "jam_finish"
            subject = self.title + " is over"
        elif n == JamStatusCode.RATING:
            template = "rating_start"
            notify = "jam_finish"
            subject = "Rating for " + self.title + " starts now"
        elif n == JamStatusCode.FINISHED:
            template = "finished"
            notify = "jam_finish"
            subject = "Rating for " + self.title + " finished - Winners"
            kwargs = {"games": self.gamesByScore()[:3]}

        if n >= JamStatusCode.RUNNING and n != JamStatusCode.RATING:
            users = [r.user for r in self.participations]
        else:
            from flamejam.models import User
            users = User.query.all()

        # Set this first because we might send for longer than a minute at
        # which point the
        # next tick will come around.
        self.last_notification_sent = n
        db.session.commit()

        subject = app.config["LONG_NAME"] + ": " + subject

        with mail.connect() as conn:
            for user in users:
                if getattr(user, "notify_" + notify):
                    body = render_template(
                        "emails/jam/" + template + ".txt",
                        recipient=user,
                        jam=self,
                        **kwargs
                    )
                    sender = app.config['MAIL_DEFAULT_SENDER']
                    recipients = [user.email]
                    message = Message(
                        subject=subject,
                        sender=sender,
                        body=body,
                        recipients=recipients
                    )
                    try:
                        conn.send(message)
                    except SMTPRecipientsRefused:
                        pass
        return True

    @property
    def livestreamTeams(self):
        return [t for t in self.teams if t.livestream]


class JamStatusCode(object):
    ANNOUNCED = 0
    REGISTRATION = 1
    RUNNING = 2
    PACKAGING = 3
    RATING = 4
    FINISHED = 5


class JamStatus(object):
    def __init__(self, code, time):
        self.code = code
        self.time = time

    def __repr__(self):
        t = formattime(self.time)
        d = humandelta(datetime.utcnow(), self.time)
        if self.code == JamStatusCode.ANNOUNCED:
            return "Announced for {0}".format(t)
        elif self.code == JamStatusCode.REGISTRATION:
            return "Registrations until {0}".format(t)
        elif self.code == JamStatusCode.RUNNING:
            return "Running until {0} ({1} left)".format(t, d)
        elif self.code == JamStatusCode.PACKAGING:
            return "Packaging until {0} ({1} left)".format(t, d)
        elif self.code == JamStatusCode.RATING:
            return "Rating until {0} ({1} left)".format(t, d)
        elif self.code == JamStatusCode.PACKAGING:
            return "Finished since {0}".format(t)

        return "Database error."
