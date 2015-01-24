from flamejam import app, db
from flask import render_template, url_for, redirect, flash, request
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
from flask.ext.login import login_required, current_user
from BeautifulSoup import BeautifulSoup

@app.route('/news/<news_id>/')
def news_show(news_id):
    wpClient = Client('http://dev.gamejam.innogames.de/xmlrpc.php', 'gamejamRPC', 'g4m3j4mRPCus3r!')
    wpPost = wpClient.call(posts.GetPost(news_id))

    return render_template('news/show.html', news = wpPost)

@app.route('/news/')
def news():
    wpClient = Client('http://dev.gamejam.innogames.de/xmlrpc.php', 'gamejamRPC', 'g4m3j4mRPCus3r!')
    wpPost = wpClient.call(posts.GetPosts())

    return render_template('news/show.html', news = wpPost)