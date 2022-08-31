from flamejam import app, db, mail #, cache
from flamejam.utils import get_slug
from flamejam.models import Jam, Game, Comment, GamePackage, GameScreenshot, JamStatusCode, Rating, Vote
from flamejam.models.rating import RATING_CATEGORIES
from flamejam.forms import WriteComment, GameEditForm, GameAddScreenshotForm, GameAddPackageForm, GameCreateForm, RateGameForm
from flask import render_template, url_for, redirect, flash, request, abort, send_from_directory
from flask_login import login_required, current_user
from sqlalchemy import desc
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = set(['tar.gz', 'tgz', 'rar', 'zip', 'tar', 'png', 'jpg', 'jpeg', 'gif'])


@app.route("/games/<page>")
def games(page):
    if page.isdigit():
        page = int(page)
    else:
        page = 1

    if page < 1:
        page = 1

    # is_deleted=False for enabling games again
    games = Game.query.filter_by(is_deleted=False).order_by(desc(Game.id)).paginate(page, 6, False)
    jams = Jam.query.all()

    return render_template("game/list.html", games=games, jams=jams)


@app.route("/games/show/<game_slug>")
def show_games(game_slug):
    game = Game.query.filter_by(slug=game_slug).first()
    if (game):
        return redirect(url_for('show_game', jam_slug=game.jam.slug, game_id=game.id))
    else:
        abort(404)


# @cache.cached(timeout=50, key_prefix='game_screenshot')
def get_game_screenshot(id):
    return GameScreenshot.query.filter_by(id=id).first_or_404()


@app.route("/games/screenshot/<int:id>", methods=["GET"])
def show_game_screenshot(id):
    screenshot = get_game_screenshot(id)

    return app.response_class(screenshot.screenshot, mimetype='image')


# @cache.cached(timeout=50, key_prefix='game_package')
def get_game_package(id):
    return GamePackage.query.filter_by(id=id).first_or_404()


@app.route("/games/package/<int:id>", methods=["GET"])
def show_game_package(id):
    package = get_game_package(id)

    return app.response_class(package.package, mimetype='application')


@app.route("/jams/<jam_slug>/create-game/", methods=("GET", "POST"))
@login_required
def create_game(jam_slug):
    jam = Jam.query.filter_by(slug=jam_slug).first_or_404()

    r = current_user.getParticipation(jam)
    if not r or not r.team:
        flash("You cannot create a game without participating in the jam.", category="error")
        return redirect(jam.url())
    if r.team.game:
        flash("You already have a game.")
        return redirect(r.team.game.url())

    enabled = (JamStatusCode.RUNNING <= jam.getStatus().code <= JamStatusCode.PACKAGING)

    form = GameCreateForm(request.form, obj=None)
    if enabled and form.validate_on_submit():
        game = Game(r.team, form.title.data)
        db.session.add(game)
        db.session.commit()
        return redirect(url_for("edit_game", jam_slug=jam_slug, game_id=game.id))

    return render_template("jam/game/create.html", jam=jam, enabled=enabled, form=form)


@app.route("/jams/<jam_slug>/<game_id>/vote")
@login_required
def vote_game(jam_slug, game_id):
    jam = Jam.query.filter_by(slug=jam_slug).first_or_404()
    game = Game.query.filter_by(is_deleted=False, id=game_id).first_or_404()
    if (current_user in jam.participants):
        if (current_user in game.team.members):
            flash("You can't vote for your own game!", "error")
        else:
            if (game.getVoteCountByUser(current_user) < 3):
                vote = Vote(game, current_user)
                db.session.add(vote)
                db.session.commit()
                flash("Your vote was saved!", "success")
            else:
                flash("You don't have any votes left!", "error")
    else:
        flash("You must participate in the Jam to vote!", "error")

    return redirect(game.url())


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/jams/<jam_slug>/<game_id>/edit/image", methods=("GET", "POST"))
@login_required
def upload_game_image(jam_slug, game_id):
    jam = Jam.query.filter_by(slug=jam_slug).first_or_404()
    game = Game.query.filter_by(is_deleted=False, id=game_id).first_or_404()

    if not game or not current_user in game.team.members:
        abort(403)

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            caption = secure_filename(file.filename)
            s = GameScreenshot(None, caption, game, file.read())
            db.session.add(s)
            db.session.commit()
            flash("Your screenshot has been added.", "success")
        else:
            flash("Your file extension is not allowed. Please only upload: 'png', 'jpg', 'jpeg', 'gif'", "error")

    return redirect(url_for('edit_game', jam_slug=jam_slug, game_id=game_id))


@app.route("/jams/<jam_slug>/<game_id>/edit/package", methods=("GET", "POST"))
@login_required
def upload_game_package(jam_slug, game_id):
    jam = Jam.query.filter_by(slug=jam_slug).first_or_404()
    game = Game.query.filter_by(is_deleted=False, id=game_id).first_or_404()
    package_form = GameAddPackageForm()

    if not game or not current_user in game.team.members:
        abort(403)

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            p = GamePackage(game, None, file.read(), package_form.type.data)
            db.session.add(p)
            db.session.commit()
            flash("Your package has been added.", "success")
        else:
            flash("Your file extension is not allowed. Please only upload: 'tgz', 'rar', 'zip', 'tar'", "error")

    return redirect(url_for('edit_game', jam_slug=jam_slug, game_id=game_id))


@app.route("/jams/<jam_slug>/<game_id>/image/<filename>", methods=("GET", "POST"))
def game_image(jam_slug, game_id, filename):
    # jam = Jam.query.filter_by(slug=jam_slug).first_or_404()
    game = Game.query.filter_by(is_deleted=False, id=game_id).first_or_404()
    filename = str(game.id) + '_' + filename

    return send_from_directory(app.config.get('UPLOAD_FOLDER_IMAGES'), filename)


@app.route("/jams/<jam_slug>/<game_id>/package/<filename>", methods=("GET", "POST"))
def game_package(jam_slug, game_id, filename):
    # jam = Jam.query.filter_by(slug=jam_slug).first_or_404()
    game = Game.query.filter_by(is_deleted=False, id=game_id).first_or_404()
    filename = str(game.id) + '_' + filename

    return send_from_directory(app.config.get('UPLOAD_FOLDER_PACKAGES'), filename)


@app.route("/jams/<jam_slug>/<game_id>/edit/", methods=("GET", "POST"))
@login_required
def edit_game(jam_slug, game_id):
    jam = Jam.query.filter_by(slug=jam_slug).first_or_404()
    game = Game.query.filter_by(is_deleted=False, id=game_id).first_or_404()

    if not game or not current_user in game.team.members:
        abort(403)

    form = GameEditForm(request.form, obj=game)
    package_form = GameAddPackageForm()
    screenshot_form = GameAddScreenshotForm()

    if form.validate_on_submit():
        slug = get_slug(form.title.data)
        # if not jam.games.filter_by(slug = slug).first() in (game, None):
        # flash("A game with a similar title already exists. Please choose another title.", category = "error")
        # else:
        # form.populate_obj(game) this breaks dynamic stuff below

        game.title = form.title.data
        game.description = form.description.data
        game.technology = form.technology.data
        game.help = form.help.data

        if game.jam.getStatus().code < 4:
            for c in RATING_CATEGORIES:
                setattr(game, "score_" + c + "_enabled", form.get(c).data)

        game.slug = get_slug(game.title)
        db.session.commit()
        flash("Your settings have been applied.", category="success")
        return redirect(game.url())

    # if package_form.validate_on_submit():
    #    s = GamePackage(game, package_form.url.data, package_form.type.data)
    #    db.session.add(s)
    #    db.session.commit()
    #    flash("Your package has been added.", "success")
    #    return redirect(request.url)

    # if screenshot_form.validate_on_submit():
    #    s = GameScreenshot(screenshot_form.url.data, screenshot_form.caption.data, game)
    #    db.session.add(s)
    #    db.session.commit()
    #    flash("Your screenshot has been added.", "success")
    #    return redirect(request.url)

    return render_template("jam/game/edit.html", jam=jam, game=game,
                           form=form, package_form=package_form, screenshot_form=screenshot_form)


@app.route('/edit/package/<id>/<action>/')
@login_required
def game_package_edit(id, action):
    if not action in ("delete"):
        abort(404)

    p = GamePackage.query.filter_by(id=id).first_or_404()
    if not current_user in p.game.team.members:
        abort(403)

    if action == "delete":
        if (p.url):
            filename = str(p.game.id) + '_' + p.url.rsplit('/', 1)[-1]
            filepath = os.path.join(app.config.get('UPLOAD_FOLDER_PACKAGES'), filename)
            os.remove(filepath)
        db.session.delete(p)
        flash("Your package has been deleted.", "success")

    db.session.commit()
    return redirect(url_for("edit_game", jam_slug=p.game.jam.slug, game_id=p.game.id))


@app.route('/edit/screenshot/<id>/<action>/')
@login_required
def game_screenshot_edit(id, action):
    if not action in ("up", "down", "delete"):
        abort(404)

    s = GameScreenshot.query.filter_by(id=id).first_or_404()
    if not current_user in s.game.team.members:
        abort(403)

    if action == "up":
        s.move(-1)
    elif action == "down":
        s.move(1)
    elif action == "delete":
        if (s.url):
            filename = str(s.game.id) + '_' + s.url.rsplit('/', 1)[-1]
            filepath = os.path.join(app.config.get('UPLOAD_FOLDER_IMAGES'), filename)
            os.remove(filepath)
        db.session.delete(s)
        flash("Your image has been deleted.", "success")

        i = 0
        for x in s.game.screenshotsOrdered:
            x.index = i
            i += 1
    db.session.commit()
    return redirect(url_for("edit_game", jam_slug=s.game.jam.slug, game_id=s.game.id))


@app.route('/jams/<jam_slug>/<game_id>/', methods=("POST", "GET"))
def show_game(jam_slug, game_id):
    comment_form = WriteComment()
    jam = Jam.query.filter_by(slug=jam_slug).first_or_404()
    game = Game.query.filter_by(is_deleted=False, id=game_id).filter_by(jam=jam).first_or_404()

    if current_user.is_authenticated and comment_form.validate_on_submit():
        comment = Comment(comment_form.text.data, game, current_user)
        db.session.add(comment)
        db.session.commit()

        # notify the team
        for user in game.team.members:
            if user.notify_game_comment:
                body = render_template("emails/comment.txt", recipient=user, comment=comment)
                mail.send_message(subject=current_user.username + " commented on " + game.title,
                                  recipients=[user.email], body=body)

        flash("Your comment has been posted.", "success")
        return redirect(game.url())

    rating = Rating.query.filter_by(game_id=game.id, user_id=current_user.get_id()).first()
    return render_template('jam/game/info.html', game=game, form=comment_form, rating=rating)


@app.route("/jams/<jam_slug>/<game_id>/rate/", methods=("GET", "POST"))
@login_required
def rate_game(jam_slug, game_id):
    jam = Jam.query.filter_by(slug=jam_slug).first_or_404()
    game = Game.query.filter_by(jam_id=jam.id, is_deleted=False, id=game_id).first_or_404()

    form = RateGameForm()
    if jam.getStatus().code != JamStatusCode.RATING:
        flash("This jam is not in the rating phase. Sorry, but you cannot rate right now.", "error")
        return redirect(game.url())

    if current_user in game.team.members:
        flash("You cannot rate on your own game. Go rate on one of these!", "warning")
        return redirect(url_for("jam_games", jam_slug=jam.slug))

    # Allow only users who participate in this jam to vote.
    if not current_user in jam.participants:
        flash("You cannot rate on this game. Only participants are eligible for vote.", "error")
        return redirect(url_for("jam_games", jam_slug=jam.slug))

    rating = Rating.query.filter_by(game_id=game.id, user_id=current_user.id).first()
    if rating:
        flash("You are editing your previous rating of this game.", "info")

    if form.validate_on_submit():
        new = rating == None
        if not rating:
            rating = Rating(game, current_user, form.note.data, form.score.data)
            db.session.add(rating)
        else:
            rating.text = form.note.data

        for c in ["overall"] + game.ratingCategories:
            rating.set(c, form.get(c).data)

        db.session.commit()
        flash("Your rating has been " + ("submitted" if new else "updated") + ".", "success")
        return redirect(url_for("jam_games", jam_slug=jam.slug))

    elif rating:
        for c in ["overall"] + game.ratingCategories:
            form.get(c).data = rating.get(c)
        form.note.data = rating.text

    return render_template('jam/game/rate.html', jam=jam, game=game, form=form)
