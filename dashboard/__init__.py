from models import *
import os
from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='af08igu9ing',
        SQLALCHEMY_DATABASE_URI = 'sqlite:///app.sqlite',
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    from . import dashboard
    app.register_blueprint(dashboard.bp)
    
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app