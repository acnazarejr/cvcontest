from flask import render_template, redirect, jsonify, url_for, flash, current_app, send_from_directory, request
from flask.ext.login import login_required, current_user
from flask_wtf.file import FileField
from werkzeug import secure_filename
from . import main
from .. import db
from .forms import UploadBuildForm
from ..models import Build, BuildStatus, User
import uuid
from datetime import datetime
import os


@main.route('/')
def index():
    if current_user.is_authenticated():
        return render_template('index.html')
    else:
        return redirect(url_for('auth.login'))


@main.route('/view-builds')
@login_required
def view_builds():
    builds = current_user.builds.all()
    star_build = current_user.star_build
    return render_template('view_builds.html', builds=builds, star_build=star_build)


@main.route('/make-star')
@login_required
def make_star():
    try:
        build_id = request.args.get('build_id', 0, type=int)
        build = Build.query.get(build_id)
        if build.author == current_user and build.status == BuildStatus.SUCCESS:
            current_user.star_build = build
            db.session.add(current_user)
            db.session.commit()
            message = "The favorite build has changed"
        else:
            message = "Operation not allowed"
    except:
        message = "An unknown error occurred"
        return jsonify(confirm=False, message=message)
    return jsonify(confirm=True, message=message)


@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadBuildForm()
    if form.validate_on_submit():
        timestamp = datetime.utcnow
        filename = secure_filename(form.buildFile.data.filename)
        uid = uuid.uuid4()
        build_hash = uid.hex
        build_hash = current_user.username + '_' + str(build_hash)
        uploads_folder = os.path.join(current_app.config['APP_ROOT'], 'static', current_app.config['UPLOAD_FOLDER'])
        form.buildFile.data.save(uploads_folder + '/' + build_hash + '.zip')
        build = Build(build_hash=build_hash,
                      message=form.message.data,
                      status=BuildStatus.WAIT,
                      author=current_user._get_current_object(),
                      rank1=-1, rank2=-1, rank3=-1)
        db.session.add(build)
        db.session.commit()
        flash('Build uploaded with success!')
        return redirect(url_for('.index'))
    return render_template('upload.html', form=form)


@main.route('/download/<build_id>')
@login_required
def download(build_id):
    build = Build.query.get(build_id)
    if build.author == current_user:
        build_hash = build.build_hash
        uploads = os.path.join(current_app.config['APP_ROOT'], 'static', current_app.config['UPLOAD_FOLDER'])
        return send_from_directory(directory=uploads, filename=build_hash + '.zip')
    else:
        flash('You do not have permission to access this build.')
        return redirect(url_for('main.index'))


@main.route('/view-log/<build_id>')
@login_required
def view_log(build_id):
    build = Build.query.get(build_id)
    if build.author == current_user:
        build_hash = build.build_hash
        uploads = os.path.join(current_app.config['APP_ROOT'], 'static', current_app.config['UPLOAD_FOLDER'])
        log_txt = open(uploads + "/" + build_hash + ".txt", "r")
        return render_template('view_log.html', log_text=log_txt.read().encode('utf-8'))
    else:
        flash('You do not have permission to access this build.')
        return redirect(url_for('main.index'))


@main.route('/ranking1')
@login_required
def ranking1():
    users = User.query.all()
    builds = []
    for user in users:
        if user.star_build is not None:
            builds.append(user.star_build)
    builds = sorted(builds, key=lambda build: build.rank1)
    return render_template('ranking.html', builds=builds, ranking=1)


@main.route('/ranking2')
@login_required
def ranking2():
    users = User.query.all()
    builds = []
    for user in users:
        if user.star_build is not None:
            builds.append(user.star_build)
    builds = sorted(builds, key=lambda build: build.rank2, reverse=True)
    return render_template('ranking.html', builds=builds, ranking=2)


@main.route('/ranking3')
@login_required
def ranking3():
    users = User.query.all()
    builds = []
    for user in users:
        if user.star_build is not None:
            builds.append(user.star_build)
    builds = sorted(builds, key=lambda build: build.rank3)
    return render_template('ranking.html', builds=builds, ranking=3)
