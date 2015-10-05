from flask.ext.uploads import UploadSet, IMAGES
from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class UploadBuildForm(Form):    
    buildFile = FileField('Build File (*.zip)', validators=[
		FileRequired(),
		FileAllowed(['zip'], 'Compacted zip files only!')
    ])
    message = StringField('Message (optional)')
    submit = SubmitField('Upload Build')
