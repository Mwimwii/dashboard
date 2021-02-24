""" Flask Configuration """
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))
FLASK_ENV=environ.get("DEV_FLASK_ENV")
# SECRET_KEY=environ.get("SECRET_KEY")
# STATIC_FOLDER="static"
# TEMPLATES_FOLDER="templates"
TESTING=True
DEBUG=True
SQLALCHEMY_DATABASE_URI = environ.get("DEV_SQLALCHEMY_DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = True