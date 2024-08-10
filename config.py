import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SITE_NAME = "PAI Admin"
    DEFAULT_TITLE = "PAI Admin"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")
    SUPPORTED_FILE_EXTENSIONS = ["pdf", "doc", "docx", "txt"]
    DATA_DIR = os.environ.get("DATA_DIR")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    DELETE_FILE_ENABLED = False
