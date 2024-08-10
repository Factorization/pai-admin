import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"
login.login_message = "Please log in to access this page."
login.login_message_category = "info"
login.session_protection = "strong"
limiter = Limiter(key_func=get_remote_address, default_limits=["60 per hour"])


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2, x_host=2)  # type: ignore

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from app.views.auth import bp as auth_bp

    limiter.limit("30 per hour")(auth_bp)
    limiter.limit("3 per second")(auth_bp)
    app.register_blueprint(auth_bp)

    from app.views.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    from app.views.main import bp as main_bp

    app.register_blueprint(main_bp)

    # Setup logging
    if app.config["LOG_TO_STDOUT"]:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/flask.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("Flask App startup")
    app.logger.info(f"URL Prefix: {app.config["FLASK_URL_PREFIX"]}")
    return app


from app import models  # noqa: E402, F401
