from flask import current_app
from . import db
from .models import Build, BuildStatus
import os

def run_builds():
    build = Build.query.filter_by(status=0).first()
    if build != None:
        build.status = BuildStatus.BUILD
        db.session.commit()
        uploads = os.path.join(current_app.config['APP_ROOT'], current_app.config['UPLOAD_FOLDER'])
        file = open(uploads + "/" + build.build_hash + ".txt", "w")
        print(uploads + "/" + build.build_hash + ".txt", "w")
        for i in range(0, 30):
            file.write("build for: " + build.build_hash + "\n")    
        file.close()
        build.status = BuildStatus.SUCCESS
        db.session.commit()
    print(build)
