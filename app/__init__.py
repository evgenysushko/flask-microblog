import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask, request
from flask.logging import create_logger
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from config import Config

my_app = Flask(__name__)
my_app.config.from_object(Config)
db = SQLAlchemy(my_app)
migrate = Migrate(my_app, db)
login = LoginManager(my_app)
login.login_view = 'login'
login.login_message = _l('Please log in to access this page.')
log = create_logger(my_app)
mail = Mail(my_app)
bootstrap = Bootstrap(my_app)
moment = Moment(my_app)
babel = Babel(my_app)

if not my_app.debug:
    if my_app.config['MAIL_SERVER']:
        auth = None
        if my_app.config['MAIL_USERNAME'] or my_app.config['MAIL_PASSWORD']:
            auth = (
                my_app.config['MAIL_USERNAME'], my_app.config['MAIL_PASSWORD']
                )
        secure = None
        if my_app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(my_app.config['MAIL_SERVER'], my_app.config['MAIL_PORT']),
            fromaddr='no-reply@' + my_app.config['MAIL_SERVER'],
            toaddrs=my_app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        log.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    log.addHandler(file_handler)

    log.setLevel(logging.INFO)
    log.info('* Microblog startup *')


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(my_app.config['LANGUAGES'])
    # return 'es'


from app import routes, models, errors
