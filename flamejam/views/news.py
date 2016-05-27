from flamejam import app, db, cache_it
from flask import render_template, url_for, redirect, flash, request
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts, taxonomies
from wordpress_xmlrpc.exceptions import ServerConnectionError, InvalidCredentialsError
from flask.ext.login import login_required, current_user
from BeautifulSoup import BeautifulSoup


@cache_it
def getWordpressPostById(id):
    wpPost = []
    try:
        wpClient = Client(app.config.get('BLOG_URL'), app.config.get('BLOG_USER'), app.config.get('BLOG_PASSWORD'))
        wpPost = wpClient.call(posts.GetPost(id))
    finally:
        return wpPost


@cache_it
def getWordpressPosts():
    allPosts = []
    try:
        wpClient = Client(app.config.get('BLOG_URL'), app.config.get('BLOG_USER'), app.config.get('BLOG_PASSWORD'))
        allPosts = wpClient.call(posts.GetPosts({'post_status': 'publish'}))
    finally:
        return allPosts


@cache_it
def getWordpressCategories():
    wpCats = []
    try:
        wpClient = Client(app.config.get('BLOG_URL'), app.config.get('BLOG_USER'), app.config.get('BLOG_PASSWORD'))
        wpCats = wpClient.call(taxonomies.GetTerms('category'))
    finally:
        return wpCats


@app.route('/news/<news_id>/')
def news_show(news_id):
    wpPost = []
    wpCats = []
    wpRelatedPosts = []

    try:
        wpPost = getWordpressPostById(news_id)

        for term in wpPost.terms:
            if term.taxonomy == 'category':
                wpCategory = term.name
        wpCats = getWordpressCategories()
        allPosts = getWordpressPosts()
        wpRelatedPosts = []
        for post in allPosts:
            for term in post.terms:
                if term.taxonomy == 'category':
                    if term.name == wpCategory and post.id != news_id:
                        wpRelatedPosts.append(post)
    finally:
        return render_template('news/show.html', news=wpPost, categories=wpCats, related=wpRelatedPosts)


@app.route('/news/tags/<tag>/')
def news_tag(tag):
    wpCats = []
    wpRelatedPosts = []

    try:
        wpCats = getWordpressCategories()
        allPosts = getWordpressPosts()

        wpRelatedPosts = []
        for post in allPosts:
            for term in post.terms:
                if term.taxonomy == 'post_tag':
                    if term.name == tag:
                        wpRelatedPosts.append(post)
    finally:
        return render_template('news/list.html', news=wpRelatedPosts, categories=wpCats)


@app.route('/news/category/<category>/')
def news_category(category):
    wpCats = []
    wpRelatedPosts = []

    try:
        wpCats = getWordpressCategories()
        allPosts = getWordpressPosts()
        wpRelatedPosts = []
        for post in allPosts:
            for term in post.terms:
                if term.taxonomy == 'category':
                    if term.name == category:
                        wpRelatedPosts.append(post)
    finally:
        return render_template('news/list.html', news=wpRelatedPosts, categories=wpCats)


@app.route('/news/')
def news():
    wpPost = []
    wpCats = []

    try:
        wpPost = getWordpressPosts()
        wpCats = getWordpressCategories()
    finally:
        return render_template('news/list.html', news=wpPost, categories=wpCats)
