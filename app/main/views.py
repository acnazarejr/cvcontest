from flask import render_template, redirect, request, url_for, flash, current_app, send_from_directory
from flask.ext.login import login_required, current_user
from flask_wtf.file import FileField
from werkzeug import secure_filename
from . import main
from .. import db
from .forms import UploadBuildForm
from ..models import Build, BuildStatus
import uuid
from datetime import datetime
import os



@main.route('/')
def index():
	if current_user.is_authenticated():
		builds = current_user.builds.all()
		return render_template('index.html', builds=builds)
	else:
		return redirect(url_for('auth.login'))

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
	form = UploadBuildForm()
	if form.validate_on_submit():
		timestamp=datetime.utcnow
		filename = secure_filename(form.buildFile.data.filename)
		# mHash = hashlib.md5()
		# originalString = filename + current_user.username + str(timestamp) + randon		
		# mHash.update(originalString.encode('utf-8'))
		# mHash = random.getrandbits(128)
		uid = uuid.uuid4()
		buildHash = uid.hex
		form.buildFile.data.save(current_app.config['UPLOAD_FOLDER'] + '/' + str(buildHash) + '.zip')
		build = Build(build_hash=buildHash,
			message=form.message.data,
			status=BuildStatus.WAIT,
			author=current_user._get_current_object())
		db.session.add(build)
		db.session.commit()        
		flash('Build uploaded with success!')
		return redirect(url_for('.index'))
	return render_template('upload.html', form=form)

@main.route('/download/<buildHash>')
@login_required
def download(buildHash):
    uploads = os.path.join(current_app.config['APP_ROOT'], current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=buildHash + '.zip')


@main.route('/view/<buildHash>')
@login_required
def view(buildHash):
	uploads = os.path.join(current_app.config['APP_ROOT'], current_app.config['UPLOAD_FOLDER'])
	log_txt = open(uploads + "/" + buildHash + ".txt", "r")
	return render_template('view.html', log_text=log_txt.read().encode('utf-8'))