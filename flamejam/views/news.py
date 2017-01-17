from flamejam import app, cache
from flask import render_template
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts, taxonomies
from wordpress_xmlrpc.exceptions import ServerConnectionError, InvalidCredentialsError
import logging


def getWordpressPostById(id):
    wpPost = []
    try:
        wpClient = Client(app.config.get('BLOG_URL'), app.config.get('BLOG_USER'), app.config.get('BLOG_PASSWORD'))
        wpPost = wpClient.call(posts.GetPost(id))
    except (ServerConnectionError, InvalidCredentialsError) as e:
        logging.warn(e.message)
    finally:
        return wpPost


@cache.cached(timeout=50, key_prefix='wp_posts')
def getWordpressPosts():
    allPosts = []
    try:
        wpClient = Client(app.config.get('BLOG_URL'), app.config.get('BLOG_USER'), app.config.get('BLOG_PASSWORD'))
        allPosts = wpClient.call(posts.GetPosts({'post_status': 'publish'}))
    except (ServerConnectionError, InvalidCredentialsError) as e:
        logging.warn(e.message)
    finally:
        return allPosts


@cache.cached(timeout=50, key_prefix='wp_categories')
def getWordpressCategories():
    wpCats = []
    try:
        wpClient = Client(app.config.get('BLOG_URL'), app.config.get('BLOG_USER'), app.config.get('BLOG_PASSWORD'))
        wpCats = wpClient.call(taxonomies.GetTerms('category'))
    except (ServerConnectionError, InvalidCredentialsError) as e:
        logging.warn(e.message)
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
    except (ServerConnectionError, InvalidCredentialsError) as e:
        logging.warn(e.message)
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
    except (ServerConnectionError, InvalidCredentialsError) as e:
        logging.warn(e.message)
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
    except (ServerConnectionError, InvalidCredentialsError) as e:
        logging.warn(e.message)
    finally:
        return render_template('news/list.html', news=wpRelatedPosts, categories=wpCats)


@app.route('/news/')
@cache.cached(timeout=50)
def news():
    wpPost = []
    wpCats = []

    try:
        wpPost = getWordpressPosts()
        wpCats = getWordpressCategories()
    except (ServerConnectionError, InvalidCredentialsError) as e:
        logging.warn(e.message)
    finally:
        for news in wpPost:
            for term in news.terms:
                if term.taxonomy == "category":
                    news.rubrik = term.name
            if news.thumbnail:
                for key, value in news.thumbnail.iteritems():
                    if key == "thumbnail":
                        news.thumbpic = value

        return render_template('news/list.html', news=wpPost, categories=wpCats)
