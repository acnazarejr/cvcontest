from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask.ext.login import UserMixin
from datetime import datetime
from . import db, login_manager


class BuildStatus:
    WAIT = 0
    BUILD = 1
    ERROR = 2
    SUCCESS = 3


class Build(db.Model):
    __tablename__ = 'builds'
    build_id = db.Column(db.Integer, primary_key=True)
    build_hash = db.Column(db.String(200), index=True)
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    rank1 = db.Column(db.Float)
    rank2 = db.Column(db.Float)
    rank3 = db.Column(db.Float)
    status = db.Column(db.Integer)

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint, random
        import forgery_py

        seed()
        for i in range(count):
            u = User.query.offset(i % 10).first()
            b = Build(
                build_hash=u.username,
                message=forgery_py.lorem_ipsum.words(5),
                author=u,
                rank1=random() * 10,
                rank2=random() * 10,
                rank3=random() * 10,
                status=randint(0,3)
            )
            db.session.add(b)
            db.session.commit()

            u.star_build = b
            db.session.add(u)
            db.session.commit()
            print(b)

    def current_status(self):
        n = self.status
        if n == 0:
            return 'Queued'
        elif n == 1:
            return 'Processing'
        elif n == 2:
            return 'Error'
        elif n >= 3:
            return 'Passed'

    def get_ranking_value(self, ranking=1):
        if ranking == 1:
            return self.rank1
        elif ranking == 2:
            return self.rank2
        elif ranking == 3:
            return self.rank3
        return self.rank1

    def __repr__(self):
        return '<Build %r>' % self.build_id


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(30), unique=True, index=True)
    complete_name = db.Column(db.String(200), unique=True, index=True)
    register = db.Column(db.String(20), unique=True, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    star_build_id = db.Column(db.Integer, db.ForeignKey('builds.build_id', use_alter=True, name="fk_star_build"))
    builds = db.relationship('Build', backref='author', lazy='dynamic', primaryjoin=user_id == Build.author_id)
    star_build = db.relationship(Build, primaryjoin=star_build_id == Build.build_id, post_update=True)
    confirmed = db.Column(db.Boolean, default=False)

    @staticmethod
    def generate_fake(count=10):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     complete_name=forgery_py.name.full_name(),
                     register=str(i).zfill(8),
                     timestamp=forgery_py.date.date(True),
                     password='123',
                     confirmed=True)
            print(u)
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def get_id(self):
        try:
            return self.user_id
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.user_id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.user_id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.user_id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.user_id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.user_id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.user_id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
