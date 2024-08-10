from urllib.parse import unquote_plus, urlsplit

import sqlalchemy as sa
from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app import db
from app.bin.utils import log_request
from app.models import User
from app.views.auth import bp
from app.views.auth.forms import LoginForm


@bp.route("/login", methods=["GET", "POST"])
def login():
    log_request()

    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.lower()
        current_app.logger.info(
            f"User:{username} | IP: {request.remote_addr} - Attempting to login"
        )
        user = db.session.scalar(sa.select(User).where(User.username == username))
        next_page = request.args.get("next") or ""
        if user is None or not user.check_password(form.password.data):
            current_app.logger.warning(
                f"User:{username} | IP: {request.remote_addr} - Username or password is incorrect"
            )
            flash("Login failed. Invalid username or password", "danger")
            return redirect(url_for("auth.login", next=unquote_plus(next_page)))
        login_user(user)
        current_app.logger.info(
            f"User:{username} | IP: {request.remote_addr} - User successfully logged in"
        )

        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("main.index")
        return redirect(unquote_plus(next_page))
    return render_template("auth/login.html", title="Sign In", form=form)


@bp.route("/logout")
def logout():
    log_request()
    if current_user.is_authenticated:
        current_app.logger.info(
            f"User:{current_user.username} | IP: {request.remote_addr} - User logged out"
        )
    logout_user()
    return redirect(url_for("main.index"))
