from urllib.parse import urlencode

from flask import current_app, request
from flask_login import current_user


def modify_query(**new_values):
    args = request.args.copy()
    for key, value in new_values.items():
        args[key] = value
    return f"{request.path}?{urlencode(args)}"


def blankout(instr, r="*", s=1, e=-1):
    if e == 0:
        e = len(instr)
    return instr.replace(instr[s:e], r * len(instr[s:e]))


def log_request():
    if current_user.is_authenticated:
        current_app.logger.info(
            f"User:{current_user.username} | IP:{request.remote_addr} - Method:{request.method} URL:{request.full_path}"
        )
    else:
        current_app.logger.info(
            f"IP:{request.remote_addr} - Method:{request.method} URL:{request.full_path}"
        )
