from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField


class UploadBuildForm(Form):
    buildFile = FileField('Build File (*.zip)', validators=[
        FileRequired(),
        FileAllowed(['zip'], 'Compacted zip files only!')
    ])
    message = StringField('Message (optional)')
    submit = SubmitField('Upload Build')
