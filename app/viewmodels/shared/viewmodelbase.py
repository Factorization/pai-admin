from typing import Optional

import flask
from flask import Request, current_app

from app.infrastructure import request_dict


class ViewModelBase:
    def __init__(self):
        self.request: Request = flask.request
        self.request_dict: dict = request_dict.create(default_val="")

        self.site_name: Optional[str] = current_app.config["SITE_NAME"]
        self.title: Optional[str] = current_app.config["DEFAULT_TITLE"]
        self.error: Optional[str] = None

    def to_dict(self):
        return self.__dict__

    def flash_error(self):
        if self.error:
            flask.flash(self.error, "danger")
