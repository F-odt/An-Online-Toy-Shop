from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from babel.numbers import format_currency as babel_format_currency

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Register the custom filter
    @app.template_filter()
    def format_currency(value, currency):
        return babel_format_currency(value, currency, locale='en_US')

    return app
