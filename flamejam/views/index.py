from flamejam import app
from flamejam.utils import get_current_jam
from flamejam.models import Jam
from flask import render_template, url_for, redirect
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts

@app.route("/")
def index():
    wpClient = Client('http://dev.gamejam.innogames.de/xmlrpc.php', 'gamejamRPC', 'g4m3j4mRPCus3r!')
    wpPosts = wpClient.call(posts.GetPosts({'number': 4}))

    return render_template("index.html", all_jams = Jam.query.all(), news = wpPosts)

#@app.route("/home")
#def home():
#    return render_template("index.html", all_jams = Jam.query.all())
