from flamejam import app, db, cache_it
from flamejam.models import Jam, Game
from flask import render_template, url_for, redirect, request
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
from wordpress_xmlrpc.exceptions import ServerConnectionError, InvalidCredentialsError


@cache_it
def getWordpressPostsLimit(limit):
    wpPost = []

    try:
        wpClient = Client(app.config.get('BLOG_URL'), app.config.get('BLOG_USER'), app.config.get('BLOG_PASSWORD'))
        wpPost = wpClient.call(posts.GetPosts({'number': limit, 'post_status': 'publish'}))
    finally:
        return wpPost


def getBestGames():
    games = db.engine.execute(
        "SELECT count(v.game_id) as score, v.game_id, g.title, g.slug, gs.url FROM vote v LEFT JOIN game_screenshot gs on gs.game_id = v.game_id LEFT JOIN game g on v.game_id = g.id GROUP BY v.game_id, gs.url ORDER BY 1 DESC LIMIT 4;")

    return games


@app.route("/")
def index():
    if (request.host.find('igjam.eu') != -1):
        return render_template("index_gamescom.html")
    wpPosts = getWordpressPostsLimit(4)
    games = getBestGames()
    return render_template("index.html", all_jams=Jam.query.all(), news=wpPosts, games=games)
