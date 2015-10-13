import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[SSIG cvContest]'
    FLASKY_MAIL_SENDER = 'SSIG cvContest Admin <ssig.cvcontest@gmail.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
    PHOTOS_FOLDER = os.environ.get('PHOTOS_FOLDER')
    IMAGES_FOLDER = os.environ.get('IMAGES_FOLDER')
    COMPARA_FOLDER = os.environ.get('COMPARA_FOLDER')
    APP_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}