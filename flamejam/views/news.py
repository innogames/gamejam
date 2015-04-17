from flamejam import app, db
from flask import render_template, url_for, redirect, flash, request
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts, taxonomies
from wordpress_xmlrpc.exceptions import ServerConnectionError
from flask.ext.login import login_required, current_user
from BeautifulSoup import BeautifulSoup


@app.route('/news/<news_id>/')
def news_show(news_id):
    try:
        wpClient = Client('http://dev.gamejam.innogames.de/xmlrpc.php', 'gamejamRPC', 'g4m3j4mRPCus3r!')
        wpPost = wpClient.call(posts.GetPost(news_id))
    except ServerConnectionError:
        wpPost = []

    for term in wpPost.terms:
        if term.taxonomy == 'category':
            wpCategory = term.name
    wpCats = wpClient.call(taxonomies.GetTerms('category'))
    allPosts = wpClient.call(posts.GetPosts())
    wpRelatedPosts = []
    for post in allPosts:
        for term in post.terms:
            if term.taxonomy == 'category':
                if term.name == wpCategory and post.id != news_id:
                    wpRelatedPosts.append(post)

    return render_template('news/show.html', news=wpPost, categories=wpCats, related=wpRelatedPosts)


@app.route('/news/tags/<tag>/')
def news_tag(tag):
    try:
        wpClient = Client('http://dev.gamejam.innogames.de/xmlrpc.php', 'gamejamRPC', 'g4m3j4mRPCus3r!')
        wpCats = wpClient.call(taxonomies.GetTerms('category'))

        allPosts = wpClient.call(posts.GetPosts())
        wpRelatedPosts = []
        for post in allPosts:
            for term in post.terms:
                if term.taxonomy == 'post_tag':
                    if term.name == tag:
                        wpRelatedPosts.append(post)
    except ServerConnectionError:
        wpCats = []
        wpRelatedPosts = []

    return render_template('news/list.html', news=wpRelatedPosts, categories=wpCats)


@app.route('/news/category/<category>/')
def news_category(category):
    try:
        wpClient = Client('http://dev.gamejam.innogames.de/xmlrpc.php', 'gamejamRPC', 'g4m3j4mRPCus3r!')
        wpCats = wpClient.call(taxonomies.GetTerms('category'))
        allPosts = wpClient.call(posts.GetPosts())
        wpRelatedPosts = []
        for post in allPosts:
            for term in post.terms:
                if term.taxonomy == 'category':
                    if term.name == category:
                        wpRelatedPosts.append(post)
    except ServerConnectionError:
        wpCats = []
        wpRelatedPosts = []

    return render_template('news/list.html', news=wpRelatedPosts, categories=wpCats)


@app.route('/news/')
def news():
    try:
        wpClient = Client('http://dev.gamejam.innogames.de/xmlrpc.php', 'gamejamRPC', 'g4m3j4mRPCus3r!')
        wpPost = wpClient.call(posts.GetPosts({'post_status': 'publish'}))
        wpCats = wpClient.call(taxonomies.GetTerms('category'))
    except ServerConnectionError:
        wpPost = []
        wpCats = []

    return render_template('news/list.html', news=wpPost, categories=wpCats)