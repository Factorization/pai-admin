from flask import Blueprint

bp = Blueprint("errors", __name__)

from app.views.errors import view  # noqa: E402,F401
