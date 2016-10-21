from flamejam import app, db, cache_it
from flamejam.models import Jam, Game
from flask import render_template, url_for, redirect, request
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
from wordpress_xmlrpc.exceptions import ServerConnectionError, InvalidCredentialsError
import logging


def getWordpressPostsLimit():
    wpPost = []

    try:
        wpClient = Client(app.config.get('BLOG_URL'), app.config.get('BLOG_USER'), app.config.get('BLOG_PASSWORD'))
        wpPost = wpClient.call(posts.GetPosts({'number': 4, 'post_status': 'publish'}))
    except (ServerConnectionError, InvalidCredentialsError) as e:
        logging.warn(e.message)
    finally:
        return wpPost


def getBestGames():
    games = db.engine.execute(
        "SELECT count(v.game_id) as score, v.game_id, g.title, g.slug, gs.url as url FROM vote v INNER JOIN (SELECT game_id, min(url) as url FROM game_screenshot GROUP BY game_id) gs on gs.game_id = v.game_id INNER JOIN game g on v.game_id = g.id GROUP BY v.game_id, gs.game_id ORDER BY 1 DESC LIMIT 4;")

    return games


@app.route("/")
def index():
    wpPosts = getWordpressPostsLimit()
    games = getBestGames()
    return render_template("index.html", all_jams=Jam.query.all(), news=wpPosts, games=games)


@app.route("/gamescom")
def gamescom():
    return render_template("gamescom/2016.html")
