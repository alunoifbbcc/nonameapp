from flask import Flask
from config import config
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_view = 'auth.login'
admin = Admin()

def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    admin.init_app(app)

    from app.models import User, Topic, Thread, Comment, Role
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Topic, db.session))
    admin.add_view(ModelView(Thread, db.session))
    admin.add_view(ModelView(Comment, db.session))
    admin.add_view(ModelView(Role, db.session))

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
