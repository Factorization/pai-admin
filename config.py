import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SITE_NAME = "PAI Admin"
    DEFAULT_TITLE = "PAI Admin"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    LOG_TO_STDOUT = (
        True if os.environ.get("LOG_TO_STDOUT", "True").lower() == "true" else False
    )
    SUPPORTED_FILE_EXTENSIONS = ["pdf", "doc", "docx", "txt"]
    DATA_DIR = os.environ.get("DATA_DIR")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    DELETE_FILES_ENABLED = (
        True
        if os.environ.get("DELETE_FILES_ENABLED", "False").lower() == "true"
        else False
    )
