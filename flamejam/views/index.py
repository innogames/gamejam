from flamejam import app, db
from flamejam.models import Jam, Game
from flask import render_template, url_for, redirect
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
from wordpress_xmlrpc.exceptions import ServerConnectionError, InvalidCredentialsError


@app.route("/")
def index():
    try:
        wpClient = Client(app.config.get('BLOG_URL'), app.config.get('BLOG_USER'), app.config.get('BLOG_PASSWORD'))
        wpPosts = wpClient.call(posts.GetPosts({'number': 4}))
    except (ServerConnectionError, InvalidCredentialsError):
        wpPosts = []

    games = db.engine.execute(
        "SELECT AVG(score_gameplay)+AVG(score_graphics)+AVG(score_audio)+AVG(score_innovation)+AVG(score_story)+AVG(score_technical)+AVG(score_controls)+AVG(score_humor) as score, r.game_id, g.title, gs.url FROM rating r LEFT JOIN game_screenshot gs on gs.game_id = r.game_id LEFT JOIN game g on r.game_id = g.id GROUP BY r.game_id ORDER BY 1 DESC LIMIT 4;")

    return render_template("index.html", all_jams=Jam.query.all(), news=wpPosts, games=games)