from flask import Blueprint

bp = Blueprint("main", __name__)

from app.views.main import view  # noqa: E402,F401
